"""UI-independent orchestration and readable presentation of comparison results.

Language profiles are reference facts. Metrics are structural observations.
Execution results are observations for one source/input pair. Keeping these
separate prevents a successful example from being mistaken for a proof about
all programs in a language.
"""

from datetime import datetime, timezone

from core.ast_analyzer import analyze_ast
from core.execution_runner import execute_code

PROFILES = {
    "python": {
        "Paradigms": "Supports imperative, object-oriented and functional styles.",
        "Types": "Dynamic typing; object types are checked by operations at runtime. Annotations alone do not enforce types.",
        "Scope / binding": "Lexical scoping; function assignment normally binds locally. global/nonlocal explicitly change the binding target.",
        "Parameters": "Parameters bind to passed objects. Mutation of a shared mutable object is visible; rebinding a parameter is local.",
        "Execution": "This app runs CPython: source is compiled to bytecode and executed by the interpreter.",
        "Errors": "Syntax errors are caught before execution; exceptions report or handle runtime failures.",
    },
    "javascript": {
        "Paradigms": "Supports imperative, prototype-based object-oriented and functional styles.",
        "Types": "Dynamic typing; some operators perform implicit coercion (for example string + number).",
        "Scope / binding": "Lexical scoping. let/const are block scoped; var is function scoped within functions.",
        "Parameters": "Arguments are passed by value. An object value provides shared object access; rebinding the parameter stays local.",
        "Execution": "This app uses Node.js, whose V8 engine can interpret and JIT-compile JavaScript.",
        "Errors": "Node diagnoses syntax errors and runtime exceptions; try/catch handles thrown errors.",
    },
    "cpp": {
        "Paradigms": "Supports procedural, object-oriented and generic programming; functions and lambdas also support functional styles.",
        "Types": "Static typing: declarations and expressions are checked during compilation; implicit conversions still exist.",
        "Scope / binding": "Lexical block, function, class and namespace scopes; inner declarations can shadow outer names.",
        "Parameters": "Value parameters copy/initialize a local value. T& reference parameters alias caller objects; pointers are another mechanism.",
        "Execution": "This app compiles C++17 to a native executable, then runs it in a separate process.",
        "Errors": "Compiler diagnostics reject invalid programs; exceptions can handle runtime failures. Some operations can have undefined behavior.",
    },
}


def compare_snippets(source_a: str, language_a: str, source_b: str, language_b: str,
                     stdin: str = "", timeout: float = 5, run: bool = True,
                     cancel_event=None) -> dict:
    """Analyze both source snapshots, optionally execute, then compare stdout.

    Args:
        source_a: First editor's source snapshot.
        language_a: First language ID.
        source_b: Second editor's source snapshot.
        language_b: Second language ID.
        stdin: Shared finite standard input for a fair input comparison.
        timeout: Per-process execution budget in seconds.
        run: False performs static inspection only, without launching snippets.
        cancel_event: Optional event propagated into process polling.
    Returns:
        Exportable report including original inputs, results and observation.
    """
    snippets = []
    for source, language in ((source_a, language_a), (source_b, language_b)):
        analysis = analyze_ast(source, language)
        language = analysis["language"]
        execution = None
        if run:
            if analysis["syntax_error"]:
                execution = {"status": "syntax_error", "stdout": "", "stderr": analysis["syntax_error"],
                             "exit_code": None, "duration_ms": 0, "compile_duration_ms": 0,
                             "setup_error": None}
            else:
                execution = execute_code(source, language, timeout, stdin, cancel_event)
        snippets.append({"source": source, "language": language,
                         "analysis": analysis, "execution": execution})
    first, second = (snippet["execution"] for snippet in snippets)
    equal = None
    if first and second and first["status"] == second["status"] == "success":
        equal = first["stdout"] == second["stdout"]
        observation = ("Both succeeded with identical stdout for this input." if equal else
                       "Both succeeded with different stdout for this input.")
        observation += " One observation does not establish semantic equivalence."
    elif run:
        observation = "Output comparison unavailable: both snippets must execute successfully. Inspect each diagnostic."
    else:
        observation = "Static analysis only; execution has not been requested."
    return {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
            "stdin": stdin, "timeout_seconds": timeout, "snippets": snippets,
            "outputs_equal": equal, "observation": observation}


def render_view(report: dict, index: int, view: str) -> str:
    """Format one report column for the selected dashboard view.

    Args:
        report: Comparison result from compare_snippets.
        index: 0 for snippet A or 1 for snippet B.
        view: Static AST, Runtime, or PPL Verdict.
    Returns:
        Human-readable text suitable for a read-only textbox or export.
    """
    snippet = report["snippets"][index]
    analysis = snippet["analysis"]
    language = snippet["language"]
    if view == "Runtime":
        execution = snippet["execution"]
        if execution is None:
            return "Not executed. Select Run comparison to observe behavior."
        return (
            f"STATUS: {execution['status']}\nExit code: {execution['exit_code']}\n"
            f"Process time: {execution['duration_ms']:.2f} ms\n"
            f"Compile time: {execution['compile_duration_ms']:.2f} ms\n\n"
            f"STDOUT\n{execution['stdout'] or '(empty)'}\n\n"
            f"DIAGNOSTICS\n{execution.get('setup_error') or execution['stderr'] or '(none)'}\n\n"
            "Process time includes startup. C++ compilation is separate. Single runs are not language benchmarks."
        )
    if view == "PPL Verdict":
        facts = "\n\n".join(f"{key}\n{value}" for key, value in PROFILES[language].items())
        evidence = (f"Functions: {analysis['function_count']}; loops: {analysis['loop_count']}; "
                    f"branches: {analysis['branch_count']}; exception handling: {analysis['uses_exception_handling']}.")
        return f"LANGUAGE REFERENCE — {language.upper()}\n{facts}\n\nSNIPPET EVIDENCE\n{evidence}\n\nOBSERVATION\n{report['observation']}"
    scope = analysis["max_scope_depth"]
    tokens = "\n".join(f"{token['line']}:{token['column']}  {token['kind']}  {token['text']!r}"
                       for token in analysis["token_preview"])
    validation = ("Validated" if analysis["syntax_validated"] else "Not validated by surface analysis")
    if analysis["syntax_error"]:
        validation = analysis["syntax_error"]
    return (
        f"METHOD: {'Python tokenizer + AST' if analysis['parse_method'] == 'ast' else 'Approximate surface heuristics'}\n"
        f"Syntax: {validation}\nLines: {analysis['line_count']} | Tokens: {analysis['token_count']}\n"
        f"Functions ({analysis['function_count']}): {', '.join(analysis['function_names']) or '(none)'}\n"
        f"Direct recursion candidates: {', '.join(analysis['recursive_functions']) or '(none)'}\n"
        f"Variables ({analysis['variable_count']}): {', '.join(analysis['variable_names']) or '(none)'}\n"
        f"Loops: {analysis['loop_count']} | Branches: {analysis['branch_count']}\n"
        f"Scope depth: {scope if scope is not None else 'unknown'}\n"
        f"Exception handling: {analysis['uses_exception_handling']}\n\n"
        + "\n".join(analysis["warnings"])
        + f"\n\nTOKEN PREVIEW (first 60)\n{tokens}\n\nSTRUCTURE (up to 12,000 characters)\n{analysis['structure_preview']}"
    )


def render_report(report: dict) -> str:
    """Produce a portable Markdown record of sources, inputs and all views.

    Args:
        report: Completed report snapshot; never reads current editor state.
    Returns:
        Markdown text that the UI can save to a user-selected path.
    """
    # A fence longer than any backtick sequence prevents source text from
    # accidentally breaking out of its exported code block.
    import re
    raw_text = str(report)
    fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r'`+', raw_text)), default=0))
    lines = ["# PPL Semantics Analyzer — comparison", "", report["created_at"], "",
             report["observation"], "", "## Standard input", "", fence + "text", report["stdin"], fence]
    for index, snippet in enumerate(report["snippets"]):
        lines += ["", f"## Snippet {'AB'[index]} — {snippet['language']}", "",
                  fence + snippet["language"], snippet["source"], fence]
        for view in ("Static AST", "Runtime", "PPL Verdict"):
            lines += ["", f"### {view}", "", fence + "text", render_view(report, index, view), fence]
    return "\n".join(lines) + "\n"
