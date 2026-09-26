"""
main.py

Root entry point for the PPL Semantics Analyzer desktop application.

Flow: show LauncherWindow first (an HWiNFO-style "start diagnostics"
screen). If the user clicks Start, close the launcher and open
MainWindow. If they cancel or close the launcher instead, the app
exits without ever opening the dashboard.

This file stays thin on purpose — it only sequences the two windows.
Backend wiring (core/ast_analyzer.py, core/execution_runner.py) into
either window's frames happens in a later pass, not here.
"""

from ui.launcher_window import LauncherWindow
from ui.main_window import MainWindow


def main() -> None:
    """Run the launcher, then the main dashboard if the user starts it.

    Args:
        None.

    Returns:
        None.
    """
    launcher = LauncherWindow()
    launcher.mainloop()

    if launcher.result != "start":
        return

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()