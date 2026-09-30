"""
test_cases.py

Minimum required test cases for the syllabus rubric: at least three
meaningful tests covering normal execution and error handling. Run with:

    pytest tests/test_cases.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.ast_analyzer import analyze_ast
from core.execution_runner import execute_code


def test_static_analysis_detects_python_recursion():
    """Normal case: recursive Python factorial should be flagged as recursive."""
    source = (
        "def factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    return n * factorial(n - 1)\n"
    )
    result = analyze_ast(source, "python")
    assert "factorial" in result["recursive_functions"]
    assert result["syntax_error"] is None
    assert result["parse_method"] == "ast"


def test_static_analysis_handles_python_syntax_error():
    """Error case: malformed source should be reported, not crash the analyzer."""
    broken_source = "def broken(:\n    return 1"
    result = analyze_ast(broken_source, "python")
    assert result["syntax_error"] is not None
    assert result["function_names"] == []


def test_static_analysis_javascript_regex_fallback():
    """Normal case: JS snippet uses the regex fallback and still detects recursion."""
    js_source = (
        "function factorial(n) {\n"
        "    if (n <= 1) { return 1; }\n"
        "    return n * factorial(n - 1);\n"
        "}\n"
    )
    result = analyze_ast(js_source, "javascript")
    assert result["parse_method"] == "regex"
    assert "factorial" in result["recursive_functions"]


def test_static_analysis_no_state_leaks_between_calls():
    """Regression test: result dicts must not share mutable list state
    across separate calls (see deepcopy fix in ast_analyzer.py)."""
    valid_source = "def foo():\n    return 1\n"
    broken_source = "def broken(:\n"

    first = analyze_ast(valid_source, "python")
    second = analyze_ast(broken_source, "python")
    third = analyze_ast(valid_source, "python")

    assert first["function_names"] == ["foo"]
    assert second["function_names"] == []
    assert third["function_names"] == ["foo"]


def test_execution_runner_executes_normal_python_snippet():
    """Normal case: a valid Python snippet should run and produce expected stdout."""
    result = execute_code("print(2 + 2)", "python", timeout=5)
    assert result["timed_out"] is False
    assert result["exit_code"] == 0
    assert "4" in result["stdout"]


def test_execution_runner_captures_runtime_error():
    """Error case: a snippet that raises should return nonzero exit code
    and populated stderr, without raising inside the runner itself."""
    result = execute_code("print(1 / 0)", "python", timeout=5)
    assert result["timed_out"] is False
    assert result["exit_code"] != 0
    assert "ZeroDivisionError" in result["stderr"]


def test_execution_runner_enforces_timeout():
    """Error case: an infinite loop should be killed at the timeout, not hang."""
    result = execute_code("while True:\n    pass", "python", timeout=2)
    assert result["timed_out"] is True
    assert result["exit_code"] is None


# The following regressions check observable behavior, not implementation
# details. Toolchain-dependent cases explicitly skip only if the tool is absent.
import json
import math
import threading
import time

import pytest

from core.comparison import compare_snippets, render_report, render_view
from core.examples import LESSONS
from core.execution_runner import runtime_paths


@pytest.mark.parametrize("source,names", [
    ("x = 1\nx = 2\na, b = (3, 4)\n", ["a", "b", "x"]),
    ("value: int = 2\nfor n in range(2):\n    value += n\n", ["n", "value"]),
    ("def f(a, *args, **kwargs):\n    return a\n", ["a", "args", "kwargs"]),
])
def test_python_counts_unique_bindings(source, names):
    """Repeated assignments and destructuring follow documented count semantics."""
    result = analyze_ast(source, "python")
    assert result["variable_names"] == names
    assert result["variable_count"] == len(names)


def test_python_nested_function_call_does_not_make_outer_recursive():
    """A call in a separately defined function is not a direct outer self-call."""
    result = analyze_ast("def outer():\n    def inner():\n        return outer()\n    return inner\n", "python")
    assert result["recursive_functions"] == []
    assert result["max_scope_depth"] == 2


def test_python_token_and_tree_evidence():
    """The static view exposes the actual tokenizer and parsed tree evidence."""
    result = analyze_ast("x = 1\nprint(x)\n", "python")
    assert result["syntax_validated"]
    assert result["token_preview"][0] == {"kind": "NAME", "text": "x", "line": 1, "column": 1}
    assert "Assign" in result["structure_preview"]


def test_context_invalid_python_is_diagnosed_without_execution():
    """A top-level return parses into an AST but is rejected by compilation."""
    assert "outside function" in analyze_ast("return 1", "python")["syntax_error"]


@pytest.mark.parametrize("language,source", [
    ("javascript", "function f() { return 1; } console.log(f());"),
    ("cpp", "int f() { return 1; } int main() { return f(); }"),
])
def test_external_function_call_is_not_recursion(language, source):
    """Calling a helper outside its definition must not label it recursive."""
    result = analyze_ast(source, language)
    assert result["recursive_functions"] == []
    assert result["max_scope_depth"] is None
    assert not result["syntax_validated"]


def test_comments_and_url_strings_do_not_hide_real_javascript():
    """Comment delimiters inside a quoted URL cannot consume following code."""
    source = 'const url = "https://host/for("; function f() { return 1; } // while (x) {}\n'
    result = analyze_ast(source, "javascript")
    assert result["function_names"] == ["f"]
    assert result["loop_count"] == 0


@pytest.mark.parametrize("timeout", [0, -1, math.nan, math.inf, True, 31, "5"])
def test_invalid_timeout_rejected(timeout):
    """Invalid limits are rejected before launching any process."""
    with pytest.raises(ValueError):
        execute_code("print(1)", "python", timeout)


def test_unsupported_language_rejected_consistently():
    """Analysis and execution share supported IDs rather than guessing C++."""
    for operation in (analyze_ast, execute_code):
        with pytest.raises(ValueError):
            operation("hello", "unknown")


def test_timeout_preserves_text_on_both_streams():
    """Printed output before a timeout remains decoded, including stderr."""
    result = execute_code("import sys\nprint('ready')\nprint('notice', file=sys.stderr)\nwhile True: pass\n", "python", 0.2)
    assert result["timed_out"]
    assert "ready" in result["stdout"]
    assert "notice" in result["stderr"]
    assert isinstance(result["stderr"], str)


def test_stdin_and_eof_are_finite():
    """A second read reaches EOF instead of blocking for a terminal forever."""
    result = execute_code("import sys\nprint(sys.stdin.read().upper())\nprint(repr(sys.stdin.read()))", "python", stdin="hello")
    assert result["stdout"] == "HELLO\n''\n"
    assert result["status"] == "success"


def test_working_directory_is_temporary():
    """Relative writes happen under the temporary directory, then are removed."""
    result = execute_code("from pathlib import Path\nPath('demo.txt').write_text('demo')\nprint(Path.cwd())", "python")
    directory = Path(result["stdout"].strip())
    assert directory.name.startswith("ppl-demo-")
    assert not directory.exists()


def test_output_flood_stops_and_truncates():
    """A printing loop is stopped without holding its whole output in memory."""
    result = execute_code("while True: print('x' * 4096)", "python", 2)
    assert result["output_limited"]
    assert len(result["stdout"].encode()) <= 64 * 1024


def test_invalid_output_bytes_do_not_crash_decoder():
    """Non-UTF-8 output produces replacement text rather than a UI exception."""
    result = execute_code("import os\nos.write(1, b'\\xff')", "python")
    assert result["status"] == "success"
    assert result["stdout"] == "\ufffd"


def test_cancel_running_program():
    """A Stop event interrupts a running snippet before the full timeout."""
    event = threading.Event()
    timer = threading.Timer(0.2, event.set)
    timer.start()
    try:
        result = execute_code("while True: pass", "python", 5, cancel_event=event)
    finally:
        timer.cancel()
    assert result["cancelled"]
    assert result["duration_ms"] < 3000


def test_missing_tool_is_setup_error(monkeypatch):
    """Missing Node has a friendly setup status, not a snippet runtime error."""
    monkeypatch.setattr("core.execution_runner.runtime_paths", lambda: {"javascript": None})
    result = execute_code("console.log(1)", "javascript")
    assert result["status"] == "setup_error"
    assert "Node" in result["setup_error"]


def test_os_launch_error_is_captured(monkeypatch):
    """An executable path becoming unavailable is reported as a setup error."""
    monkeypatch.setattr("core.execution_runner.runtime_paths", lambda: {"python": "/no/such/python"})
    assert execute_code("print(1)", "python")["status"] == "setup_error"


@pytest.mark.parametrize("language", ["python", "javascript", "cpp"])
@pytest.mark.parametrize("lesson_name", list(LESSONS))
def test_every_bundled_lesson(lesson_name, language):
    """Run each advertised demo through the same pipeline used by the UI."""
    if runtime_paths()[language] is None:
        pytest.skip(f"{language} runtime not installed")
    lesson = LESSONS[lesson_name]
    source = lesson["sources"][language]
    # Pair with a tiny Python snippet so each language example is executed once.
    timeout = 0.2 if lesson_name == "Timeout" else 5
    report = compare_snippets(source, language, "print('reference')", "python",
                              stdin=lesson["stdin"], timeout=timeout)
    execution = report["snippets"][0]["execution"]
    expected_status = lesson.get("statuses", {}).get(language, "success")
    assert execution["status"] == expected_status, execution
    expected = lesson["expected"][language]
    if expected is not None:
        assert execution["stdout"] == expected
    if language == "cpp" and expected_status == "compile_error":
        assert execution["setup_error"] is None
        assert execution["compile_stderr"]


@pytest.mark.parametrize("language", ["python", "javascript", "cpp"])
@pytest.mark.parametrize("stdin", ["abc\n", "3.5\n", "11\n", ""])
def test_input_lesson_rejects_bad_input(language, stdin):
    """All languages handle non-integers, range errors and missing input."""
    if runtime_paths()[language] is None:
        pytest.skip(f"{language} runtime not installed")
    result = execute_code(LESSONS["Input and validation"]["sources"][language], language, stdin=stdin)
    assert result["status"] == "success"
    assert result["stdout"] == "Input error: Enter an integer from 0 to 10\n"


def test_static_only_does_not_execute_side_effects(tmp_path):
    """Static inspection compiles structure but never evaluates source."""
    marker = tmp_path / "must-not-exist"
    source = f"from pathlib import Path\nPath({str(marker)!r}).touch()"
    report = compare_snippets(source, "python", "print(1)", "python", run=False)
    assert not marker.exists()
    assert report["snippets"][0]["execution"] is None
    assert report["outputs_equal"] is None


def test_output_equality_requires_success():
    """Two identical failure outputs must not be presented as equivalence."""
    report = compare_snippets("raise ValueError('x')", "python", "raise ValueError('x')", "python")
    assert report["outputs_equal"] is None
    assert "unavailable" in report["observation"]


def test_report_serializes_sources_and_all_views():
    """Export reflects the executed snapshot and supports Markdown and JSON."""
    report = compare_snippets("print(42)", "python", "print(42)", "python")
    assert report["outputs_equal"] is True
    assert "does not establish" in report["observation"]
    assert json.loads(json.dumps(report))["snippets"][0]["source"] == "print(42)"
    markdown = render_report(report)
    for view in ("Static AST", "Runtime", "PPL Verdict"):
        assert view in markdown
        assert render_view(report, 0, view)
