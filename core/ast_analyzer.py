"""Inspect syntax without executing code.

Python uses its real tokenizer and AST. JavaScript/C++ use explicitly labeled
surface heuristics; their syntax and type errors are diagnosed by Node/compiler
when Run is selected. Structural evidence is not proof of runtime behavior.
"""

import ast
import io
import keyword
import re
import tokenize

SUPPORTED_LANGUAGES = ("python", "javascript", "cpp")


def analyze_ast(code_string: str, language: str) -> dict:
    """Collect comparable structural metrics and explain their limitations.

    Args:
        code_string: Source to inspect, without executing it.
        language: python, javascript, or cpp, case insensitive.
    Returns:
        Fresh metrics, token preview, and parsing evidence for one snippet.
    Raises:
        TypeError: Source is not text.
        ValueError: Language is not supported.
    """
    if not isinstance(code_string, str):
        raise TypeError("code_string must be a string")
    language = (language or "").strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language!r}")
    result = {
        "language": language, "parse_method": "ast" if language == "python" else "regex",
        "line_count": len(code_string.splitlines()), "function_count": 0,
        "function_names": [], "recursive_functions": [], "variable_count": 0,
        "variable_names": [], "loop_count": 0, "branch_count": 0,
        "max_scope_depth": None, "uses_exception_handling": False,
        "syntax_error": None, "syntax_validated": False, "token_count": 0,
        "token_preview": [], "structure_preview": "", "warnings": [],
    }
    if not code_string.strip():
        result["syntax_error"] = "Empty snippet."
        return result
    if language == "python":
        return _analyze_python(code_string, result)
    return _analyze_surface(code_string, result)


def _analyze_python(source: str, result: dict) -> dict:
    """Tokenize, parse, and inspect Python, preserving useful error evidence.

    Args:
        source: Python text.
        result: Fresh result dictionary populated in place.
    Returns:
        Metrics or a syntax diagnostic with line/column information.
    """
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NL,
                              tokenize.NEWLINE, tokenize.COMMENT):
                continue
            category = "KEYWORD" if keyword.iskeyword(token.string) else tokenize.tok_name[token.type]
            tokens.append({"kind": category, "text": token.string,
                           "line": token.start[0], "column": token.start[1] + 1})
    except (tokenize.TokenError, IndentationError):
        # ast.parse supplies the more useful grammar diagnostic below.
        pass
    result["token_count"] = len(tokens)
    result["token_preview"] = tokens[:60]
    try:
        tree = ast.parse(source)
        # Parsing alone allows some context-invalid forms (e.g. top-level
        # return). Compilation checks those rules without executing anything.
        compile(tree, "<snippet>", "exec")
    except (SyntaxError, ValueError) as exc:
        result["syntax_error"] = (
            f"{getattr(exc, 'msg', str(exc))} "
            f"(line {getattr(exc, 'lineno', '?')}, column {getattr(exc, 'offset', '?')})"
        )
        return result
    result["syntax_validated"] = True
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["function_names"].append(node.name)
            if _python_function_is_recursive(node):
                result["recursive_functions"].append(node.name)
        if isinstance(node, ast.Lambda):
            result["function_names"].append(f"<lambda at line {node.lineno}>")
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While, ast.comprehension)):
            result["loop_count"] += 1
        if isinstance(node, (ast.If, ast.IfExp, ast.Match)):
            result["branch_count"] += 1
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        if isinstance(node, ast.arg):
            names.add(node.arg)
        if isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name.split(".")[0])
        if isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try))):
            result["uses_exception_handling"] = True
    result["function_count"] = len(result["function_names"])
    result["variable_names"] = sorted(names)
    result["variable_count"] = len(names)
    result["max_scope_depth"] = _python_scope_depth(tree)
    result["structure_preview"] = ast.dump(tree, indent=2)[:12000]
    result["warnings"] = [
        "Recursion means a direct same-name call in a function body; aliases, methods, mutual recursion and rebinding are not resolved.",
        "Variables count unique stored/parameter/import/exception names across the snippet, not separate bindings per scope; function/class names are excluded.",
        "Scope depth measures nested function/class/lambda/comprehension syntax, not a complete Python name-resolution model.",
    ]
    return result


def _python_function_is_recursive(function: ast.AST) -> bool:
    """Look for direct same-name calls, excluding separately nested scopes.

    Args:
        function: FunctionDef or AsyncFunctionDef node.
    Returns:
        Whether the body contains a syntactic direct self-call candidate.
    """
    pending = list(function.body)
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == function.name):
            return True
        pending.extend(ast.iter_child_nodes(node))
    return False


def _python_scope_depth(tree: ast.AST) -> int:
    """Measure structural nesting of constructs that introduce Python scopes.

    Args:
        tree: Parsed module.
    Returns:
        Maximum nesting depth; module itself has depth zero.
    """
    scope_nodes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
                   ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
    pending = [(tree, 0)]
    deepest = 0
    while pending:
        node, depth = pending.pop()
        depth += isinstance(node, scope_nodes)
        deepest = max(deepest, depth)
        pending.extend((child, depth) for child in ast.iter_child_nodes(node))
    return deepest


# A single left-to-right scan prevents // inside "https://..." from eating
# real code. Template literals are masked as a whole: ${...} is not analyzed.
_MASK = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_SURFACE_TOKEN = re.compile(r'[A-Za-z_$][\w$]*|\d+(?:\.\d+)?|===|!==|=>|==|!=|<=|>=|\+\+|--|&&|\|\||[^\s]')
_JS_FUNCTION = re.compile(
    r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{'
    r'|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\{'
)
_CPP_FUNCTION = re.compile(r'\b(?:[A-Za-z_]\w*[\s*&:<>]+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{')
_RESERVED = {"if", "for", "while", "switch", "catch", "return", "sizeof"}


def _strip_comments_and_strings(source: str) -> str:
    """Mask comments and quoted literals while preserving token positions.

    Args:
        source: JavaScript or C++ source.
    Returns:
        Equal-length text with spaces replacing comments/literals except newlines.
    """
    return _MASK.sub(lambda match: re.sub(r'[^\n]', ' ', match.group()), source)


def _analyze_surface(source: str, result: dict) -> dict:
    """Estimate C-family constructs without claiming full grammar validation.

    Args:
        source: JavaScript or C++ text.
        result: Fresh result to populate.
    Returns:
        Approximate metrics with explicit warnings and unknown scope depth.
    """
    cleaned = _strip_comments_and_strings(source)
    matches = list(_SURFACE_TOKEN.finditer(cleaned))
    result["token_count"] = len(matches)
    for match in matches[:60]:
        line = cleaned.count("\n", 0, match.start()) + 1
        column = match.start() - cleaned.rfind("\n", 0, match.start())
        result["token_preview"].append({"kind": "SURFACE", "text": match.group(),
                                        "line": line, "column": column})
    javascript = result["language"] == "javascript"
    pattern = _JS_FUNCTION if javascript else _CPP_FUNCTION
    structures = []
    for match in pattern.finditer(cleaned):
        name = next(group for group in match.groups() if group)
        if name in _RESERVED:
            continue
        result["function_names"].append(name)
        # Match the definition's own brace-delimited body; an invocation in
        # main() or at top level must not make a helper appear recursive.
        start = match.end()
        depth = 1
        end = start
        while end < len(cleaned) and depth:
            depth += (cleaned[end] == "{") - (cleaned[end] == "}")
            end += 1
        body = cleaned[start:end - 1] if depth == 0 else ""
        if re.search(rf'(?<![\w$]){re.escape(name)}\s*\(', body):
            result["recursive_functions"].append(name)
        structures.append(f"Function candidate: {name}")
    variable_pattern = (r'\b(?:let|const|var)\s+([A-Za-z_$][\w$]*)' if javascript else
                        r'\b(?:int|float|double|char|bool|long|short|auto|std::string|string)\s+[&*]?\s*([A-Za-z_]\w*)\s*(?=[=;,)]|\{)')
    result["variable_names"] = sorted(set(re.findall(variable_pattern, cleaned)))
    result["variable_count"] = len(result["variable_names"])
    result["function_count"] = len(result["function_names"])
    result["loop_count"] = len(re.findall(r'\b(?:for|while)\s*\(', cleaned))
    result["branch_count"] = len(re.findall(r'\b(?:if|switch)\s*\(', cleaned))
    result["uses_exception_handling"] = bool(re.search(r'\btry\s*\{', cleaned))
    result["structure_preview"] = "\n".join(structures) or "No supported function patterns found."
    result["warnings"] = [
        "Approximate surface analysis, not an AST. Run invokes the real language toolchain for syntax/type diagnostics.",
        "Comments and quoted literals are masked; token count excludes them. JS regex literals, template interpolation, C++ raw strings/macros and complex declarations are not parsed.",
        "Only named brace-bodied functions are detected. Recursion is a body-local name-match heuristic; nested scopes, aliases and overloads are not resolved.",
        "Variable counts cover simple declarations; scope depth is unknown. Cross-language counts use different analysis methods.",
    ]
    return result
