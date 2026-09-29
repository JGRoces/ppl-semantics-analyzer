"""Opt-in GUI checks: python -m tests.finalization_smoke."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.examples import LESSONS
from tests.gui_smoke import wait_until_idle
from ui.application import Application
from ui.lesson_resources import LESSON_RESOURCES
from ui.ui_assets import UIAssets


def cancelled_comparison(*args):
    """Keep a worker active until navigation signals cancellation.

    Args:
        args: Comparison arguments, ending with the cancellation event.
    Returns:
        None after cancellation.
    """
    assert args[-1].wait(5), "Navigation did not cancel the worker"
    return None


def main() -> None:
    """Exercise navigation, layout, lesson actions, and active-worker cleanup.

    Args:
        None.
    Returns:
        None; assertions report a regression.
    """
    window = Application()
    errors = []
    window.report_callback_exception = lambda *error: errors.append(error)
    try:
        window.launcher._on_start()
        window.update()
        native_id = window.winfo_id()
        app = window.workspace
        assert set(app.pages) == {"workspace", "lessons", "reports"}
        assert not hasattr(app, "stdin_box")
        assert not hasattr(app, "lesson_text")
        results_card = app.results[0].master
        assert int(results_card.grid_info()["row"]) == 3
        assert app.workspace.grid_rowconfigure(3)["weight"] == 2
        assert results_card.winfo_height() > 150
        assert set(LESSON_RESOURCES) == set(LESSONS)
        for name in LESSONS:
            app.lesson_cards[name].invoke()
            assert app.lesson_menu.get() == name
            assert app.lesson_stdin == LESSONS[name]["stdin"]
            assert app.lesson_cards[name].cget("text") == "Load demonstration"
            assert app.lesson_view_buttons[name].cget("text") == "View Lesson"
            with patch("ui.main_window.os") as platform:
                platform.name = "nt"
                app.lesson_view_buttons[name].invoke()
                opened = Path(platform.startfile.call_args.args[0])
                assert opened.is_file()
                assert opened.name == LESSON_RESOURCES[name]["pdf"]
            with patch("ui.main_window.os", SimpleNamespace(name="posix")):
                with patch("ui.main_window.webbrowser.open", return_value=True) as browser:
                    app.lesson_view_buttons[name].invoke()
                    browser.assert_called_once_with(opened.as_uri())
        with patch("ui.main_window.Path.is_file", return_value=False):
            with patch("ui.main_window.messagebox.showerror") as dialog:
                app._view_lesson("Recursion")
                dialog.assert_called_once()
        with patch("ui.main_window.os", SimpleNamespace(name="posix")):
            with patch("ui.main_window.webbrowser.open", return_value=False):
                with patch("ui.main_window.messagebox.showerror") as dialog:
                    app._view_lesson("Recursion")
                    dialog.assert_called_once()
        app._select_lesson("Input and validation")
        app.language_menus[1].set("Python")
        app._load_lesson()
        app._start(True)
        wait_until_idle(app)
        assert app.report["snippets"][0]["execution"]["stdout"].strip() == "49"
        app.appearance_switch.select()
        app._toggle_appearance()
        app._toggle_sidebar()
        assert app.back_button.cget("text") == "←"
        app._toggle_sidebar()
        assert app.back_button.cget("text") == "Back to Menu"
        with patch("ui.main_window.compare_snippets", cancelled_comparison):
            app._start(True)
            app.back_button.invoke()
            window.update()
            assert app.cancel_event.is_set()
            assert app.poll_id is None
            assert not app.winfo_exists()
            assert window.workspace is None
            assert window.launcher.appearance_switch_var.get() == "dark"
            assert not window.bind("<Control-Return>")
            assert not window.bind("<Command-Return>")
            window.launcher._choose_pair(("Python", "C++"))
            window.launcher._on_start()
            window.update()
            assert window.workspace is not app
            assert window.workspace.language_menus[1].get() == "C++"
            assert window.winfo_id() == native_id
        # A second round trip catches stale root bindings and destroyed callbacks.
        window.workspace.back_button.invoke()
        window.update()
        window.launcher._on_start()
        window.update()
        assert not errors, errors
        assert window.workspace.back_button.cget("corner_radius") == UIAssets.CORNER_RADIUS
        assert window.workspace.cget("fg_color") == UIAssets.COLORS["BG_PRIMARY"]
        assert window.workspace.results[0].master.cget("fg_color") == UIAssets.COLORS["SURFACE"]
        print("PASS: layout, lesson input, all PDF actions, menu round trips, worker cancellation")
    finally:
        window._close()


if __name__ == "__main__":
    main()
