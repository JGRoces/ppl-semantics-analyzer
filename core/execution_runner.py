"""Run local teaching snippets outside the GUI process.

A temporary working directory keeps ordinary relative file writes away from the
project. Time and output limits keep common demo mistakes manageable. This is
process isolation, not a security sandbox: only run code you trust.
"""

import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 5
MAX_OUTPUT_BYTES = 64 * 1024
SUPPORTED_LANGUAGES = ("python", "javascript", "cpp")


def runtime_paths() -> dict:
    """Locate the executables used by the three language adapters.

    Args:
        None.
    Returns:
        Mapping from language ID to executable path, or None if absent.
    """
    return {
        "python": sys.executable,
        "javascript": shutil.which("node") or shutil.which("nodejs"),
        "cpp": shutil.which("g++") or shutil.which("clang++"),
    }


def _empty_result(language: str) -> dict:
    """Create independent result state for one snippet.

    Args:
        language: Normalized language ID.
    Returns:
        A result with all fields present, including separate compile diagnostics.
    """
    return {
        "language": language, "stdout": "", "stderr": "", "exit_code": None,
        "duration_ms": 0.0, "timed_out": False, "compiled": None,
        "setup_error": None, "status": "pending", "output_limited": False,
        "cancelled": False, "compile_duration_ms": 0.0, "compile_stderr": "",
    }


def execute_code(code_string: str, language: str,
                 timeout: float = DEFAULT_TIMEOUT_SECONDS, stdin: str = "",
                 cancel_event: threading.Event | None = None) -> dict:
    """Validate, prepare, and execute a Python, Node.js, or C++17 snippet.

    Args:
        code_string: Source text, written as UTF-8 in a temporary directory.
        language: python, javascript, or cpp (case insensitive).
        timeout: Positive finite execution budget in seconds, at most 30.
        stdin: Text supplied to standard input; EOF follows immediately.
        cancel_event: Optional cooperative cancellation signal from the UI.
    Returns:
        Consistent diagnostics. Compilation errors are distinct from missing
        tools; C++ compilation time is separate from process execution time.
    Raises:
        TypeError: Source or stdin is not text.
        ValueError: Language or timeout is invalid.
    """
    if not isinstance(code_string, str) or not isinstance(stdin, str):
        raise TypeError("Source and stdin must be strings.")
    language = (language or "").strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language!r}")
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or not 0 < timeout <= 30):
        raise ValueError("Timeout must be a finite number greater than 0 and at most 30.")
    result = _empty_result(language)
    if not code_string.strip():
        result.update(status="input_error", setup_error="Empty snippet.")
        return result
    executable = runtime_paths()[language]
    if executable is None:
        result.update(status="setup_error", setup_error={
            "javascript": "Node.js was not found on PATH.",
            "cpp": "g++ or clang++ was not found on PATH.",
        }.get(language, "Python interpreter was not found."))
        return result

    try:
        with tempfile.TemporaryDirectory(prefix="ppl-demo-") as directory:
            workdir = Path(directory)
            extension = {"python": "py", "javascript": "js", "cpp": "cpp"}[language]
            source = workdir / f"snippet.{extension}"
            source.write_text(code_string, encoding="utf-8")
            if language == "cpp":
                binary = workdir / ("snippet.exe" if os.name == "nt" else "snippet")
                compilation = _run_process(
                    [executable, str(source), "-std=c++17", "-o", str(binary)],
                    workdir, min(timeout + 10, 30), "", cancel_event,
                )
                result["compile_duration_ms"] = compilation["duration_ms"]
                result["compile_stderr"] = compilation["stderr"]
                result["compiled"] = compilation["status"] == "success"
                if not result["compiled"]:
                    # A rejected program is a source/compilation error, not an
                    # installation error. Preserve cancellation and timeout flags.
                    for key in ("stderr", "exit_code", "timed_out", "cancelled",
                                "output_limited", "setup_error"):
                        result[key] = compilation[key]
                    result["status"] = ("compile_error" if compilation["status"] == "runtime_error"
                                        else "compile_" + compilation["status"])
                    return result
                command = [str(binary)]
            elif language == "python":
                # -u preserves output printed immediately before a timeout;
                # -I ignores user site packages and PYTHON* environment settings.
                command = [executable, "-I", "-u", str(source)]
            else:
                command = [executable, str(source)]
            result.update(_run_process(command, workdir, timeout, stdin, cancel_event))
    except OSError as exc:
        result.update(status="setup_error", setup_error=str(exc))
    return result


def _stop_process(process: subprocess.Popen) -> None:
    """Stop a process and, on POSIX, its process group.

    Args:
        process: Child started by _run_process in a new POSIX session.
    Returns:
        None. Already exited processes are harmless.
    """
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        elif process.poll() is None:
            process.kill()
    except ProcessLookupError:
        pass


def _run_process(command: list, workdir: Path, timeout: float, stdin: str,
                 cancel_event: threading.Event | None) -> dict:
    """Capture bounded text while polling for exit, cancellation, and limits.

    Args:
        command: Executable and arguments; never interpreted by a shell.
        workdir: Temporary source and working directory.
        timeout: Wall-clock budget for this phase only.
        stdin: Finite UTF-8 input supplied through a temporary file.
        cancel_event: Optional UI cancellation event.
    Returns:
        Process-specific fields to merge into the language result.
    """
    result = {key: value for key, value in _empty_result("").items()
              if key not in ("language", "compiled", "compile_duration_ms", "compile_stderr")}
    start = time.monotonic()
    # Files avoid pipe deadlocks and unbounded in-memory communicate() buffers.
    # The cap is checked every 10 ms, so disk writes can overshoot it briefly.
    with tempfile.TemporaryFile() as input_file, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        input_file.write(stdin.encode("utf-8"))
        input_file.seek(0)
        process = None
        try:
            if cancel_event is not None and cancel_event.is_set():
                result.update(status="cancelled", cancelled=True)
                return result
            process = subprocess.Popen(
                command, cwd=workdir, stdin=input_file, stdout=output,
                stderr=errors, start_new_session=os.name == "posix",
            )
            while True:
                output_size = os.fstat(output.fileno()).st_size + os.fstat(errors.fileno()).st_size
                if cancel_event is not None and cancel_event.is_set():
                    result.update(status="cancelled", cancelled=True)
                    break
                if output_size > MAX_OUTPUT_BYTES:
                    result.update(status="output_limit", output_limited=True)
                    break
                if process.poll() is not None:
                    result.update(exit_code=process.returncode,
                                  status="success" if process.returncode == 0 else "runtime_error")
                    break
                if time.monotonic() - start >= timeout:
                    result.update(status="timeout", timed_out=True)
                    break
                time.sleep(0.01)
        except OSError as exc:
            result.update(status="setup_error", setup_error=f"Could not launch process: {exc}")
        finally:
            if process is not None:
                # Also clean up ordinary descendants after the parent exits.
                _stop_process(process)
                process.wait()
            result["duration_ms"] = round((time.monotonic() - start) * 1000, 3)
            output.seek(0)
            errors.seek(0)
            result["stdout"] = output.read(MAX_OUTPUT_BYTES).decode("utf-8", errors="replace")
            result["stderr"] = errors.read(MAX_OUTPUT_BYTES).decode("utf-8", errors="replace")
    if result["timed_out"]:
        result["stderr"] += f"\n[Stopped: exceeded {timeout:g}s timeout]"
    if result["output_limited"]:
        result["stderr"] += "\n[Stopped: output limit exceeded; captured text is truncated]"
    return result
