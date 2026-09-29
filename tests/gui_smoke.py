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

import customtkinter as ctk

from ui.application import Application
from ui.ui_assets import UIAssets


def check_navigation(app) -> None:
    """Verify persistent pages, sidebar resizing, and actionable lesson cards.

    Args:
        app: Dashboard under test.
    Returns:
        None; assertions detect source loss, stale navigation, or overflow.
    """
    original = [editor.get("1.0", "end-1c") for editor in app.editors]
    for page in app.PAGE_TITLES:
        app._show_page(page)
        app.update()
        assert app.pages[page].winfo_ismapped()
        assert app.page_label.cget("text") == app.PAGE_TITLES[page]
        assert app.nav_buttons[page][0].cget("fg_color") == UIAssets.COLORS["ACCENT"]
        assert sum(frame.winfo_ismapped() for frame in app.pages.values()) == 1
    assert [editor.get("1.0", "end-1c") for editor in app.editors] == original
    app._show_page("workspace")
    app.update()
    expanded = app.editors[0].winfo_width()
    app._toggle_sidebar()
    app.update()
    assert app.editors[0].winfo_width() > expanded
    assert not app.runtime_label.winfo_ismapped()
    app._toggle_sidebar()
    app.update()
    assert app.runtime_label.winfo_ismapped()
    app._show_page("lessons")
    app.lesson_cards["Iteration"].invoke()
    app.update()
    assert app.active_page == "workspace"
    assert "total" in app.editors[0].get("1.0", "end-1c")
    app._select_lesson("Recursion")
    # Check the supported minimum size without relying on desktop capture.
    app.winfo_toplevel().geometry("1180x760")
    app.update()
    for widget in [
        app.run_button,
        app.stop_button,
        app.lesson_menu,
        *app.language_menus,
        *app.editors,
        *app.results,
    ]:
        assert widget.winfo_width() > 30
        assert widget.winfo_height() > 20
        assert widget.winfo_rootx() >= app.winfo_rootx()
        assert (
            widget.winfo_rootx() + widget.winfo_width()
            <= app.winfo_rootx() + app.winfo_width()
        )
        assert (
            widget.winfo_rooty() + widget.winfo_height()
            <= app.winfo_rooty() + app.winfo_height()
        )


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
        assert [
            gutter.surface.itemcget(item, "text") for item in gutter.surface.find_all()
        ] == ["1"]
        small_width = gutter.gutter_width
        source = "\n".join(
            f"line_{number} = '{'x' * 150}'" for number in range(1, 1001)
        )
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
            expected_y = (
                editor.dlineinfo(f"{line}.0")[1]
                + gutter.text.winfo_rooty()
                - gutter.surface.winfo_rooty()
            )
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
        assert [
            gutter.surface.itemcget(item, "text") for item in gutter.surface.find_all()
        ] == ["1"]
    # Appearance changes must reach the native canvas as well as CTk widgets.
    for dark in (True, False):
        UIAssets.set_dark_mode(dark)
        app.update()
        for gutter in app.line_gutters:
            assert (
                gutter.surface.cget("background")
                == UIAssets.COLORS["GUTTER_BG"][int(dark)]
            )
    app.winfo_toplevel().geometry("1180x720")
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
    window = Application()
    launcher = window.launcher
    launcher._choose_pair(("Python", "C++"))
    assert launcher.language_b_combo.get() == "C++"
    launcher.update()
    for panel in (launcher.brand_panel, launcher.setup_panel):
        assert panel.winfo_width() > 350
    launcher.language_b_combo.set("C++")
    launcher.appearance_switch_var.set("light")
    window.update()
    native_window = window.winfo_id()
    original_geometry = window.geometry()
    unmapped = []
    window.bind(
        "<Unmap>",
        lambda event: unmapped.append(event.widget) if event.widget == window else None,
    )
    # Reproduce wrappers that reject yscrollcommand while constructing gutters.
    supported = ctk.CTkTextbox._valid_tk_text_attributes - {"yscrollcommand"}
    with patch.object(ctk.CTkTextbox, "_valid_tk_text_attributes", supported):
        launcher._on_start()
    window.update()
    assert launcher.selected_languages == ("Python", "C++")
    assert launcher.dark_mode is False
    assert window.winfo_id() == native_window
    assert window.geometry() == original_geometry
    assert window.winfo_ismapped()
    assert unmapped == [], "The native window must not disappear during entry"
    app = window.workspace
    assert app.winfo_toplevel() is window
    assert not launcher.winfo_exists()
    assert app.brand_title.cget("font") == UIAssets.FONTS["H1"]
    assert app.brand_subtitle.cget("font") == UIAssets.FONTS["BODY"]
    try:
        app.update()
        assert not app.appearance_switch.get()
        assert app.language_menus[1].get() == "C++"
        check_navigation(app)
        check_line_numbers(app)
        app._start(True)
        wait_until_idle(app)
        assert app.report["outputs_equal"] is True
        app._show_page("reports")
        app.update()
        assert "120" in app.report_preview.get("1.0", "end-1c")
        app._show_page("workspace")
        for view in app.HEADER_TABS:
            app._change_view(view)
            assert app.results[0].get("1.0", "end-1c")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            with patch(
                "ui.main_window.filedialog.asksaveasfilename", return_value=str(output)
            ):
                app._export()
            assert json.loads(output.read_text())["outputs_equal"] is True
            source = Path(directory) / "example.js"
            source.write_text("console.log(9);\n", encoding="utf-8")
            with patch(
                "ui.main_window.filedialog.askopenfilename", return_value=str(source)
            ):
                app._open_source(0)
            assert app.language_menus[0].get() == "JavaScript"
            assert app.report is None
            assert "No comparison report" in app.report_preview.get("1.0", "end-1c")
        app.language_menus[0].set("Python")
        app.lesson_menu.set("Types and coercion")
        app._load_lesson()
        app._start(True)
        wait_until_idle(app)
        assert [item["execution"]["status"] for item in app.report["snippets"]] == [
            "runtime_error",
            "compile_error",
        ]
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
        print(
            "PASS: same-window entry, header, navigation, line numbers, theme, run, views, export, errors, stop, recovery"
        )
    finally:
        app._close()


if __name__ == "__main__":
    main()
