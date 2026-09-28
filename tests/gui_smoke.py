"""Opt-in native GUI smoke check; run with python -m tests.gui_smoke.

This opens real windows on the current desktop. It verifies launcher handoff,
worker completion, view switching, report export, errors, cancellation, and
return to a usable state. Ordinary pytest runs never open windows.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from ui.launcher_window import LauncherWindow
from ui.main_window import MainWindow


def wait_until_idle(app, limit: float = 30) -> None:
    """Pump native events until a worker finishes, with an external deadline.

    Args:
        app: Dashboard under test.
        limit: Maximum smoke-test wait, in seconds.
    Returns:
        None.
    Raises:
        AssertionError: Worker did not finish within the test deadline.
    """
    deadline = time.monotonic() + limit
    while app.busy and time.monotonic() < deadline:
        app.update()
        time.sleep(0.02)
    assert not app.busy, "GUI worker did not complete"
    app.update()


def main() -> None:
    """Exercise the real dashboard using deterministic native callbacks.

    Args:
        None.
    Returns:
        None; assertions fail the command when an interaction breaks.
    """
    launcher = LauncherWindow()
    launcher.language_b_combo.set("C++")
    launcher.appearance_switch_var.set("light")
    launcher.after(200, launcher._on_start)
    launcher.mainloop()
    assert launcher.selected_languages == ("Python", "C++")
    assert launcher.dark_mode is False
    app = MainWindow(*launcher.selected_languages, dark_mode=launcher.dark_mode)
    try:
        app.update()
        assert not app.appearance_switch.get()
        assert app.language_menus[1].get() == "C++"
        app._start(True)
        wait_until_idle(app)
        assert app.report["outputs_equal"] is True
        for view in app.HEADER_TABS:
            app._change_view(view)
            assert app.results[0].get("1.0", "end-1c")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            with patch("ui.main_window.filedialog.asksaveasfilename", return_value=str(output)):
                app._export()
            assert json.loads(output.read_text())["outputs_equal"] is True
            source = Path(directory) / "example.js"
            source.write_text("console.log(9);\n", encoding="utf-8")
            with patch("ui.main_window.filedialog.askopenfilename", return_value=str(source)):
                app._open_source(0)
            assert app.language_menus[0].get() == "JavaScript"
            assert app.report is None
        app.language_menus[0].set("Python")
        app.lesson_menu.set("Types and coercion")
        app._load_lesson()
        app._start(True)
        wait_until_idle(app)
        assert [item["execution"]["status"] for item in app.report["snippets"]] == ["runtime_error", "compile_error"]
        app.lesson_menu.set("Timeout")
        app._load_lesson()
        app._start(True)
        app.after(200, app._stop)
        wait_until_idle(app)
        assert app.report["snippets"][0]["execution"]["cancelled"]
        app.lesson_menu.set("Recursion")
        app._load_lesson()
        app._start(False)
        wait_until_idle(app)
        assert app.report["snippets"][0]["execution"] is None
        app.appearance_switch.select()
        app._toggle_appearance()
        app.update()
        print("PASS: launcher, language/theme handoff, run, views, JSON export, file open, errors, stop, recovery")
    finally:
        app._close()


if __name__ == "__main__":
    main()
