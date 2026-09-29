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
from ui.ui_assets import UIAssets


def check_line_numbers(app) -> None:
    """Exercise gutter alignment after edits, scrolling, resizing and theming.

    Args:
        app: Fully constructed dashboard with two editors and gutters.
    Returns:
        None; assertions catch missing, stale, or misaligned line labels.
    """
    for editor, gutter in zip(app.editors, app.line_gutters):
        app._set_text(editor, "")
        app.update()
        assert [gutter.surface.itemcget(item, "text") for item in gutter.surface.find_all()] == ["1"]
        small_width = gutter.gutter_width
        source = "\n".join(f"line_{number} = '{'x' * 150}'" for number in range(1, 1001))
        app._set_text(editor, source)
        app.update()
        assert gutter.gutter_width > small_width
        editor.yview_moveto(0.5)
        editor.xview_moveto(0.5)
        app.update()
        labels = gutter.surface.find_all()
        first = gutter.surface.itemcget(labels[0], "text")
        assert first == editor.index("@0,0").split(".")[0]
        assert int(first) > 1
        for item in labels:
            line = gutter.surface.itemcget(item, "text")
            expected_y = editor.dlineinfo(f"{line}.0")[1] + gutter.text.winfo_rooty() - gutter.surface.winfo_rooty()
            assert abs(gutter.surface.coords(item)[1] - expected_y) <= 1
        assert editor.get("1.0", "end-1c") == source
        editor.see("end-1c")
        app.update()
        assert gutter.surface.itemcget(gutter.surface.find_all()[-1], "text") == "1000"
        editor.insert("end-1c", "\nnew_line")
        editor.see("end-1c")
        app.update()
        assert gutter.surface.itemcget(gutter.surface.find_all()[-1], "text") == "1001"
        editor.delete("1.0", "end")
        app.update()
        assert [gutter.surface.itemcget(item, "text") for item in gutter.surface.find_all()] == ["1"]
    # Appearance changes must reach the native canvas as well as CTk widgets.
    for dark in (True, False):
        UIAssets.set_dark_mode(dark)
        app.update()
        for gutter in app.line_gutters:
            assert gutter.surface.cget("background") == UIAssets.COLORS["GUTTER_BG"][int(dark)]
    app.geometry("1180x720")
    app.update()
    app._load_lesson()
    app.update()


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
        check_line_numbers(app)
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
        print("PASS: line numbers, editing, vertical/horizontal scroll, theme, launcher, run, views, export, errors, stop, recovery")
    finally:
        app._close()


if __name__ == "__main__":
    main()
