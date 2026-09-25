"""
main.py

Root entry point for the PPL Semantics Analyzer desktop application.

This file is intentionally thin: it only imports and launches the UI.
Backend wiring (core/ast_analyzer.py, core/execution_runner.py) into
the ui/main_window.py frames happens in a later pass, not here.
"""

from ui.main_window import MainWindow


def main() -> None:
    """Build the main window and start the CustomTkinter event loop.

    Args:
        None.

    Returns:
        None.
    """
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
