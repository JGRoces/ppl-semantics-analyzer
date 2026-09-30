"""Focused native GUI regression; run with python -m tests.gutter_smoke."""

from unittest.mock import patch

import customtkinter as ctk

from tests.gui_smoke import check_line_numbers
from ui.application import Application


def main() -> None:
    """Check workspace entry and gutter lifecycle with restricted CTk options.

    Args:
        None.
    Returns:
        None; assertions detect startup, scroll, or cleanup regressions.
    """
    errors = []
    window = Application()
    window.report_callback_exception = lambda *error: errors.append(error)
    supported = ctk.CTkTextbox._valid_tk_text_attributes - {"yscrollcommand"}
    try:
        with patch.object(ctk.CTkTextbox, "_valid_tk_text_attributes", supported):
            window.launcher._on_start()
            window.update()
            app = window.workspace
            assert app is not None
            assert window.launcher is None
            assert len(app.line_gutters) == 2
            check_line_numbers(app)
            for editor, gutter in zip(app.editors, app.line_gutters):
                app._set_text(editor, "\n".join(str(i) for i in range(300)))
                window.update()
                editor.yview_moveto(0.5)
                window.update()
                scrollbar = next(
                    child for child in editor.winfo_children()
                    if isinstance(child, ctk.CTkScrollbar)
                    and child.cget("orientation") == "vertical"
                )
                assert scrollbar.get() == editor.yview()
                original = gutter.original_scroll_command
                assert original
                text = gutter.text
                gutter.destroy()
                assert text.cget("yscrollcommand") == original
                editor.yview_moveto(0.0)
                window.update()
                assert scrollbar.get() == editor.yview()
            assert not errors, errors
        print("PASS: workspace entry, line alignment, scrolling, callback restoration")
    finally:
        window._close()


if __name__ == "__main__":
    main()
