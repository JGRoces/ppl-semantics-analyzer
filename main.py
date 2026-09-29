"""
main.py

Root entry point for the PPL Semantics Analyzer desktop application.

Flow: show LauncherWindow first (a split welcome and comparison setup
screen). If the user clicks Start, close the launcher and open
MainWindow. If they cancel or close the launcher instead, the app
exits without ever opening the dashboard.

This file stays thin on purpose — it only sequences the two windows.
The dashboard owns UI wiring; core modules remain usable without a GUI.
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

    app = MainWindow(*launcher.selected_languages, dark_mode=launcher.dark_mode)
    app.mainloop()


if __name__ == "__main__":
    main()
