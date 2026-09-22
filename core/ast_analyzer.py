"""
core/ast_analyzer.py

Static analysis engine for the PPL Semantics Analyzer.

PPL concept in play here: SYNTAX vs. SEMANTICS. This module only looks
at the *shape* of the code (syntax) — it never executes anything. That
distinction matters for the course: `ast_analyzer.py` answers "what
does this program's structure tell us?" while `execution_runner.py`
(the dynamic tracing engine) answers "what does this program actually
do when run?". Keeping them separate mirrors how real compilers/
interpreters separate a parsing phase from an execution phase.

Two analysis strategies are used, chosen by `language`:

1. Python -> Python's built-in `ast` module builds a real Abstract
   Syntax Tree. This is a true parse: it understands nested scope,
   knows a `def` from a `lambda`, and can't be fooled by a variable
   named "for". This is the gold-standard approach and is only
   possible here because we're analyzing Python with a Python
   interpreter.

2. JavaScript / C++ (or anything else) -> Python's `ast` module cannot
   parse non-Python grammars, so we fall back to a REGEX-BASED
   TOKENIZER. This is a deliberately weaker technique: it pattern-matches
   surface tokens (keywords, brace-delimited blocks) instead of building
   a real parse tree. It is intentionally included as a teaching point —
   see PPL concept note in `_analyze_regex_fallback` below — but its
   results are approximate and should be presented as such in the UI
   (e.g. a "parse_method: regex" flag is included in the returned dict).
"""

import ast
import copy
import re
from typing import Optional

# Metrics that should exist in EVERY result dict, regardless of language
# or parse method, so the Streamlit "PPL Verdict" tab can always safely
# compare Snippet A vs Snippet B without doing per-language key checks.
_RESULT_TEMPLATE = {
    "language": None,
    "parse_method": None,      # "ast" or "regex"
    "line_count": 0,
    "function_count": 0,
    "function_names": [],
    "recursive_functions": [],
    "variable_count": 0,
    "variable_names": [],
    "loop_count": 0,
    "max_scope_depth": None,   # only reliably known for Python (ast method)
    "uses_exception_handling": False,
    "syntax_error": None,      # populated only if parsing/tokenizing failed
}

SUPPORTED_LANGUAGES = ("python", "javascript", "cpp")


def analyze_ast(code_string: str, language: str) -> dict:
    """Run static structural analysis on a source code snippet.

    Dispatches to a true AST parse for Python, or a regex-based
    fallback tokenizer for other supported languages.

    Args:
        code_string: Raw source code to analyze.
        language: One of "python", "javascript", "cpp" (case-insensitive).
            Unrecognized languages are treated as generic C-family syntax
            via the regex fallback rather than raising, so the UI never
            hard-crashes on an unexpected selector value.

    Returns:
        A dictionary of structural metrics. Always contains every key
        listed in `_RESULT_TEMPLATE`, so downstream comparison code can
        rely on a consistent shape regardless of language.

    Raises:
        TypeError: If `code_string` is not a string.
    """
    if not isinstance(code_string, str):
        raise TypeError(f"code_string must be a str, got {type(code_string).__name__}")

    normalized_language = (language or "").strip().lower()
    # IMPORTANT: use deepcopy, not dict(_RESULT_TEMPLATE). A shallow copy
    # would share the SAME list objects (function_names, variable_names,
    # etc.) across every call, silently leaking state between snippets.
    result = copy.deepcopy(_RESULT_TEMPLATE)
    result["language"] = normalized_language
    result["line_count"] = len(code_string.splitlines())

    if not code_string.strip():
        result["syntax_error"] = "Empty snippet."
        return result

    if normalized_language == "python":
        return _analyze_python_ast(code_string, result)

    # JavaScript, C++, and any unrecognized language all use the same
    # surface-token fallback. Real per-language grammars would require
    # a dedicated parser (e.g. Esprima for JS, a Clang binding for C++),
    # which is out of scope for a syllabus-level static analyzer.
    return _analyze_regex_fallback(code_string, result, normalized_language)


def _analyze_python_ast(code_string: str, result: dict) -> dict:
    """Populate `result` using Python's native `ast` module.

    Args:
        code_string: Python source code.
        result: The partially-filled result dict to populate in place.

    Returns:
        The same `result` dict, now populated (or with `syntax_error` set).
    """
    result["parse_method"] = "ast"

    try:
        tree = ast.parse(code_string)
    except SyntaxError as exc:
        result["syntax_error"] = f"{exc.msg} (line {exc.lineno}, offset {exc.offset})"
        return result

    for node in ast.walk(tree):
        # PPL concept: FUNCTIONS/PROCEDURES & RECURSION.
        # A function is recursive if it calls its own name anywhere in
        # its own body -- that's the textbook definition we implement.
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["function_count"] += 1
            result["function_names"].append(node.name)
            if _python_function_is_recursive(node):
                result["recursive_functions"].append(node.name)

        # PPL concept: CONTROL STRUCTURES (iteration).
        elif isinstance(node, (ast.For, ast.While)):
            result["loop_count"] += 1

        # PPL concept: VARIABLES, BINDING.
        # Assignment is where a name gets bound to a value/object.
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result["variable_count"] += 1
                    result["variable_names"].append(target.id)

        # PPL concept: ERROR HANDLING (exception-based model).
        elif isinstance(node, ast.Try):
            result["uses_exception_handling"] = True

    result["max_scope_depth"] = _python_scope_depth(tree)
    return result


def _python_function_is_recursive(func_node) -> bool:
    """Check whether a Python function calls itself.

    Args:
        func_node: An `ast.FunctionDef` or `ast.AsyncFunctionDef` node.

    Returns:
        True if the function body contains a call to its own name.
    """
    func_name = func_node.name
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == func_name:
                return True
    return False


def _python_scope_depth(tree: ast.AST) -> int:
    """Compute the deepest nested function/class scope in a Python AST.

    PPL concept: SCOPE & BINDING. Python uses lexical (static) scoping,
    so nesting depth here directly reflects how many enclosing scopes a
    name lookup may have to walk through.

    Args:
        tree: The parsed module AST.

    Returns:
        Integer depth; 0 means no nested function/class scopes.
    """
    def walk(node, depth):
        deepest = depth
        for child in ast.iter_child_nodes(node):
            child_depth = depth
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                child_depth = depth + 1
            deepest = max(deepest, walk(child, child_depth))
        return deepest

    return walk(tree, 0)


# --- Regex-based fallback for non-Python languages -------------------

# NOTE on PPL relevance: a regex tokenizer can't understand nesting, so
# "max_scope_depth" is deliberately left as None for these languages
# rather than guessed at with brace-counting, which would misrepresent
# scope semantics (e.g. a JS block `{ }` isn't always a new *function*
# scope the way a Python `def` always is). Presenting an honest `None`
# is safer, pedagogically, than a confidently wrong number.

_JS_FUNCTION_PATTERN = re.compile(
    r"function\s+([A-Za-z_$][\w$]*)\s*\(|"          # function foo(...)
    r"([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|"  # foo = (...) =>
    r"const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"  # const foo = (...) =>
)
_JS_VARIABLE_PATTERN = re.compile(r"\b(?:let|const|var)\s+([A-Za-z_$][\w$]*)")
_JS_LOOP_PATTERN = re.compile(r"\b(?:for|while)\s*\(")
_JS_TRY_PATTERN = re.compile(r"\btry\s*\{")

_CPP_FUNCTION_PATTERN = re.compile(
    r"\b(?:[A-Za-z_]\w*[\s\*&]+)+([A-Za-z_]\w*)\s*\([^;{]*\)\s*\{"
)
_CPP_VARIABLE_PATTERN = re.compile(
    r"\b(?:int|float|double|char|bool|long|short|auto|std::string|string)\s+([A-Za-z_]\w*)\s*[=;,)]"
)
_CPP_LOOP_PATTERN = re.compile(r"\b(?:for|while)\s*\(")
_CPP_TRY_PATTERN = re.compile(r"\btry\s*\{")

_CPP_RESERVED_WORDS = {
    "if", "for", "while", "switch", "return", "sizeof", "catch",
}


def _analyze_regex_fallback(code_string: str, result: dict, language: str) -> dict:
    """Populate `result` using regex-based surface tokenization.

    This is intentionally a weaker technique than a real AST parse
    (see module docstring). It is a reasonable approximation for
    demo/teaching purposes but will miscount in edge cases (e.g.
    a variable name appearing inside a string literal or comment).

    Args:
        code_string: Source code in a non-Python language.
        result: The partially-filled result dict to populate in place.
        language: The normalized language string, used to select the
            token patterns ("javascript" vs. everything else -> "cpp"
            style patterns as a generic C-family default).

    Returns:
        The same `result` dict, now populated with best-effort metrics.
    """
    result["parse_method"] = "regex"

    # Strip comments and string literal contents first so keywords that
    # appear inside them (e.g. a docstring mentioning "for") don't get
    # miscounted as real syntax. This is a coarse strip, not a real
    # lexer, so it still isn't perfectly reliable.
    cleaned = _strip_comments_and_strings(code_string)

    if language == "javascript":
        function_pattern = _JS_FUNCTION_PATTERN
        variable_pattern = _JS_VARIABLE_PATTERN
        loop_pattern = _JS_LOOP_PATTERN
        try_pattern = _JS_TRY_PATTERN
    else:
        # C++ and any other/unrecognized language fall back to
        # generic C-family patterns.
        function_pattern = _CPP_FUNCTION_PATTERN
        variable_pattern = _CPP_VARIABLE_PATTERN
        loop_pattern = _CPP_LOOP_PATTERN
        try_pattern = _CPP_TRY_PATTERN

    function_names = []
    for match in function_pattern.finditer(cleaned):
        name = next((g for g in match.groups() if g), None)
        if name and name not in _CPP_RESERVED_WORDS:
            function_names.append(name)

    result["function_names"] = function_names
    result["function_count"] = len(function_names)
    result["recursive_functions"] = _regex_find_recursive(cleaned, function_names)

    variable_names = [m.group(1) for m in variable_pattern.finditer(cleaned)]
    result["variable_names"] = variable_names
    result["variable_count"] = len(variable_names)

    result["loop_count"] = len(loop_pattern.findall(cleaned))
    result["uses_exception_handling"] = bool(try_pattern.search(cleaned))
    # max_scope_depth intentionally left None -- see note above.

    return result


def _regex_find_recursive(cleaned_code: str, function_names) -> list:
    """Best-effort recursion detection for regex-tokenized languages.

    A function is flagged as recursive if its own name appears as a
    call (`name(`) anywhere after its first definition. This is a
    coarse heuristic -- it does not confirm the call is actually
    inside that function's body -- but is adequate for short demo
    snippets typical of a classroom presentation.

    Args:
        cleaned_code: Source with comments/strings stripped.
        function_names: Names already identified as function definitions.

    Returns:
        List of function names that appear to call themselves.
    """
    recursive = []
    for name in function_names:
        call_pattern = re.compile(rf"\b{re.escape(name)}\s*\(")
        if len(call_pattern.findall(cleaned_code)) > 1:  # 1 = the def itself
            recursive.append(name)
    return recursive


def _strip_comments_and_strings(code_string: str) -> str:
    """Coarsely remove // and /* */ comments and quoted string contents.

    Args:
        code_string: Raw source code.

    Returns:
        Source code with comments blanked out and string literal
        contents replaced by empty quotes, reducing false keyword
        matches inside them. This is a regex-based approximation, not
        a real lexer, and can be fooled by unusual edge cases (e.g.
        escaped quotes) -- acceptable for demo-scale snippets.
    """
    no_block_comments = re.sub(r"/\*.*?\*/", "", code_string, flags=re.DOTALL)
    no_line_comments = re.sub(r"//.*", "", no_block_comments)
    no_strings = re.sub(r'"(?:[^"\\]|\\.)*"', '""', no_line_comments)
    no_strings = re.sub(r"'(?:[^'\\]|\\.)*'", "''", no_strings)
    return no_strings
