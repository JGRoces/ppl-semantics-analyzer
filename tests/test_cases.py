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
