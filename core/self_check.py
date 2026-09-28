"""Verify actual toolchain execution before the presentation.

Run from the repository root with: python -m core.self_check
A detected executable is not necessarily a working compiler installation; this
check builds/runs a real program and verifies its stdout for each language.
"""

from core.examples import LESSONS
from core.execution_runner import execute_code, runtime_paths


def main() -> int:
    """Print tool paths and execute the deterministic recursion demo.

    Args:
        None.
    Returns:
        Zero if all three tools work, one if any check fails.
    """
    failed = False
    for language, path in runtime_paths().items():
        result = execute_code(LESSONS["Recursion"]["sources"][language], language)
        passed = result["status"] == "success" and result["stdout"] == "120\n"
        print(f"{'PASS' if passed else 'FAIL'} {language}: {path or 'not found'}")
        if not passed:
            print(result["setup_error"] or result["stderr"] or result["status"])
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
