"""Opt-in native GUI regression checks: python -m tests.syntax_smoke."""

import time

from ui.application import Application
from ui.ui_assets import UIAssets


def settle(window):
    """Allow the real debounce callback to execute."""
    end = time.monotonic() + 0.25
    while time.monotonic() < end:
        window.update()
        time.sleep(0.01)


def main():
    """Check both editors, language changes, Unicode, undo, and cleanup."""
    window = Application()
    errors = []
    window.report_callback_exception = lambda *args: errors.append(args)
    try:
        window.launcher._on_start()
        app = window.workspace
        samples = {
            "Python": '# comment\ndef demo():\n    return "hello" + str(42)\n',
            "JavaScript": '// comment\nfunction demo() { return "hello" + 42; }\n',
            "C++": '// comment\nint demo() { return 42; }\nconst char* s = "hello";\n',
        }
        for index in range(2):
            editor = app.editors[index]
            highlighter = app.highlighters[index]
            text = highlighter.text
            for language, source in samples.items():
                app.language_menus[index].set(language)
                app._set_text(editor, source)
                app._edited()
                settle(window)
                assert editor.get("1.0", "end-1c") == source
                for group in ("comment", "keyword", "number", "string"):
                    assert text.tag_ranges("syntax_" + group), (language, group)
                assert not editor.edit_modified()
            app.language_menus[index].set("Python")
            source = 's = "😀"; n = 42\n'
            app._set_text(editor, source)
            app._edited()
            settle(window)
            spans = text.tag_ranges("syntax_number")
            assert text.get(*spans) == "42", spans
            text.mark_set("insert", "1.0")
            text.tag_add("sel", "1.0", "1.1")
            highlighter.highlight()
            assert text.index("insert") == "1.0"
            assert text.get("sel.first", "sel.last") == "s"
            text.edit_reset()
            text.insert("end-1c", "# typed")
            settle(window)
            assert text.tag_ranges("syntax_comment")
            text.edit_undo()
            settle(window)
            assert text.get("1.0", "end-1c") == source
            assert not text.tag_ranges("syntax_comment")
        app.appearance_switch.select()
        app._toggle_appearance()
        assert app.highlighters[0].text.tag_cget("syntax_keyword", "foreground") == UIAssets.SYNTAX_COLORS["keyword"][1]
        for highlighter in app.highlighters:
            highlighter.request()
        app.back_button.invoke()
        settle(window)
        assert not errors, errors
        print("PASS: both editors, three languages, Unicode, typing, undo, theme, selection, cleanup")
    finally:
        window._close()


if __name__ == "__main__":
    main()
