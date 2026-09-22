"""
core/execution_runner.py

Dynamic tracing engine for the PPL Semantics Analyzer.

PPL concept in play: this module is the counterpart to
`core/ast_analyzer.py`'s static analysis. Where that module inspects
*structure* without running anything, this one observes *runtime
behavior* -- actual stdout, actual errors, actual timing -- which is
where semantics (what the program really does) becomes observable, as
opposed to syntax (what the program looks like).

Execution is always isolated in a subprocess, never via exec()/eval()
in-process. This matters for two reasons:
  1. Safety: a hung or crashing snippet can't take the Streamlit app
     down with it -- we can kill the subprocess and keep going.
  2. Language-agnosticism: subprocess isolation lets us shell out to
     `node` or a compiled C++ binary exactly the same way we shell out
     to `python3`, using one consistent code path.

This is a TEACHING-GRADE sandbox, not a production-grade one. It
enforces a wall-clock timeout but does NOT fully restrict filesystem or
network access from within the executed snippet. Do not point it at
untrusted code outside a controlled demo/lab environment.
"""

import copy
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

DEFAULT_TIMEOUT_SECONDS = 5

SUPPORTED_LANGUAGES = ("python", "javascript", "cpp")

# Result dict shape kept identical across languages and failure modes so
# the Streamlit Runtime Execution tab never has to special-case keys.
_RESULT_TEMPLATE = {
    "language": None,
    "stdout": "",
    "stderr": "",
    "exit_code": None,
    "duration_ms": 0.0,
    "timed_out": False,
    "compiled": None,   # True/False for C++, None for interpreted languages
    "setup_error": None,  # e.g. "node not found on PATH" -- distinct from a
                           # runtime error produced BY the snippet itself
}


def execute_code(code_string: str, language: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Execute a source snippet in an isolated subprocess and trace it.

    Args:
        code_string: Raw source code to execute.
        language: One of "python", "javascript", "cpp" (case-insensitive).
        timeout: Maximum wall-clock seconds allowed before the process
            is killed and the result is marked `timed_out`.

    Returns:
        A dictionary always containing every key in `_RESULT_TEMPLATE`:
        stdout, stderr, exit_code, duration_ms, timed_out, compiled,
        and setup_error. Exactly one of these paths happens:
          - Normal run: exit_code is set (0 or nonzero), stdout/stderr
            captured, setup_error is None.
          - Timeout: timed_out=True, exit_code=None.
          - Environment problem (e.g. `node` not installed, or a C++
            compile failure): setup_error is set describing the problem;
            this is NOT the same as the snippet raising a runtime error.

    Raises:
        TypeError: If `code_string` is not a string.
        ValueError: If `language` is not one of SUPPORTED_LANGUAGES.
    """
    if not isinstance(code_string, str):
        raise TypeError(f"code_string must be a str, got {type(code_string).__name__}")

    normalized_language = (language or "").strip().lower()
    if normalized_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. Must be one of {SUPPORTED_LANGUAGES}."
        )

    # deepcopy (not dict()) so no state can ever leak between calls if
    # this template grows list/dict fields later -- see the same fix
    # and rationale in core/ast_analyzer.py.
    result = copy.deepcopy(_RESULT_TEMPLATE)
    result["language"] = normalized_language

    if not code_string.strip():
        result["setup_error"] = "Empty snippet -- nothing to execute."
        return result

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        if normalized_language == "python":
            return _run_python(code_string, tmp_path, timeout, result)
        elif normalized_language == "javascript":
            return _run_javascript(code_string, tmp_path, timeout, result)
        else:  # cpp
            return _run_cpp(code_string, tmp_path, timeout, result)


def _run_python(code_string: str, tmp_path: Path, timeout: int, result: dict) -> dict:
    """Run a Python snippet using the same interpreter running this app.

    Args:
        code_string: Python source code.
        tmp_path: Temporary directory to write the script into.
        timeout: Timeout in seconds.
        result: Partially-filled result dict to populate in place.

    Returns:
        The populated result dict.
    """
    script_path = tmp_path / "snippet.py"
    script_path.write_text(code_string, encoding="utf-8")
    return _run_and_time([sys.executable, str(script_path)], timeout, result)


def _run_javascript(code_string: str, tmp_path: Path, timeout: int, result: dict) -> dict:
    """Run a JavaScript snippet with Node.js, if available.

    Args:
        code_string: JavaScript source code.
        tmp_path: Temporary directory to write the script into.
        timeout: Timeout in seconds.
        result: Partially-filled result dict to populate in place.

    Returns:
        The populated result dict. If `node` is not on PATH,
        `setup_error` is set instead of attempting to run.
    """
    node_path = shutil.which("node") or shutil.which("nodejs")
    if node_path is None:
        result["setup_error"] = (
            "Node.js runtime not found on PATH. Install Node.js to enable "
            "JavaScript execution (this teammate's machine or the demo "
            "machine may simply be missing it)."
        )
        return result

    script_path = tmp_path / "snippet.js"
    script_path.write_text(code_string, encoding="utf-8")
    return _run_and_time([node_path, str(script_path)], timeout, result)


def _run_cpp(code_string: str, tmp_path: Path, timeout: int, result: dict) -> dict:
    """Compile a C++ snippet with g++, then execute the resulting binary.

    Compilation happens outside the timed execution window -- only the
    run of the compiled binary is measured, so a slow compile doesn't
    unfairly count against the snippet's "execution time" in the
    comparative display.

    Args:
        code_string: C++ source code.
        tmp_path: Temporary directory to write source/binary into.
        timeout: Timeout in seconds, applied to the *run* step only.
        result: Partially-filled result dict to populate in place.

    Returns:
        The populated result dict. If `g++` is not on PATH or
        compilation fails, `compiled` is False and `setup_error` /
        `stderr` describe why -- this is treated as distinct from a
        runtime error produced by a successfully-compiled program.
    """
    gpp_path = shutil.which("g++")
    if gpp_path is None:
        result["setup_error"] = (
            "g++ compiler not found on PATH. Install a C++ toolchain to "
            "enable C++ execution."
        )
        result["compiled"] = False
        return result

    source_path = tmp_path / "snippet.cpp"
    binary_path = tmp_path / "snippet_bin"
    source_path.write_text(code_string, encoding="utf-8")

    try:
        compile_result = subprocess.run(
            [gpp_path, str(source_path), "-o", str(binary_path), "-std=c++17"],
            capture_output=True,
            text=True,
            timeout=timeout + 10,  # compilation gets its own generous budget
        )
    except subprocess.TimeoutExpired:
        result["compiled"] = False
        result["setup_error"] = "Compilation itself timed out."
        return result

    if compile_result.returncode != 0:
        result["compiled"] = False
        result["setup_error"] = "Compilation failed."
        result["stderr"] = compile_result.stderr
        return result

    result["compiled"] = True
    return _run_and_time([str(binary_path)], timeout, result)


def _run_and_time(command: list, timeout: int, result: dict) -> dict:
    """Run a command as a subprocess, capturing output and timing it.

    Args:
        command: Argument list to pass to `subprocess.run`.
        timeout: Maximum wall-clock seconds before the process is killed.
        result: Partially-filled result dict to populate in place.

    Returns:
        The populated result dict with stdout, stderr, exit_code,
        duration_ms, and timed_out set.
    """
    start_time = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration_ms = (time.monotonic() - start_time) * 1000
        result["stdout"] = completed.stdout
        result["stderr"] = completed.stderr
        result["exit_code"] = completed.returncode
        result["duration_ms"] = round(duration_ms, 3)
        result["timed_out"] = False
        return result

    except subprocess.TimeoutExpired as exc:
        duration_ms = (time.monotonic() - start_time) * 1000
        result["stdout"] = exc.stdout or ""
        result["stderr"] = (exc.stderr or "") + f"\n[Killed: exceeded {timeout}s timeout]"
        result["exit_code"] = None
        result["duration_ms"] = round(duration_ms, 3)
        result["timed_out"] = True
        return result

    except FileNotFoundError as exc:
        # The interpreter/binary itself couldn't be launched at all --
        # distinct from the snippet failing once it started running.
        result["setup_error"] = f"Could not launch process: {exc}"
        return result
