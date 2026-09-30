"""Debounced lexical coloring that never changes source or undo history."""

import tkinter as tk

import customtkinter as ctk
from pygments.lexers import CppLexer, JavascriptLexer, PythonLexer
from pygments.token import Comment, Keyword, Name, Number, String

from ui.ui_assets import UIAssets


class SyntaxHighlighter:
    """Apply independent, language-aware text tags to one source editor."""

    LEXERS = {"Python": PythonLexer(), "JavaScript": JavascriptLexer(), "C++": CppLexer()}
    GROUPS = ((Comment, "comment"), (Keyword, "keyword"), (String, "string"),
              (Number, "number"), (Name.Function, "function"), (Name.Builtin, "function"))

    def __init__(self, editor, language) -> None:
        """Keep the editor and its language getter without taking over bindings."""
        self.text = next(child for child in editor.winfo_children() if isinstance(child, tk.Text))
        self.language = language
        self.pending = None
        self.refresh_palette()

    def refresh_palette(self) -> None:
        """Resolve shared light/dark colors for native Tk tags."""
        mode = int(ctk.get_appearance_mode() == "Dark")
        for group, colors in UIAssets.SYNTAX_COLORS.items():
            self.text.tag_configure("syntax_" + group, foreground=colors[mode])
        self.text.tag_raise("sel")

    def request(self) -> None:
        """Wait for a short typing pause before recoloring the source."""
        if self.pending is not None:
            self.text.after_cancel(self.pending)
        self.pending = self.text.after(120, self.highlight)

    def highlight(self) -> None:
        """Color tokens while preserving selection, cursor, and modified state."""
        if self.pending is not None:
            self.text.after_cancel(self.pending)
            self.pending = None
        source = self.text.get("1.0", "end-1c")
        for group in UIAssets.SYNTAX_COLORS:
            self.text.tag_remove("syntax_" + group, "1.0", "end")
        # Match the workspace's source-size limit; oversized pastes stay editable.
        if len(source) > 100_000:
            return
        lexer = self.LEXERS.get(self.language())
        if lexer is None:
            return
        # Tk 8.6 counts supplementary Unicode characters as two index units.
        offsets = [0]
        wide = int(self.text.tk.call("string", "length", "\U0001f600")) == 2
        for char in source:
            offsets.append(offsets[-1] + (2 if wide and ord(char) > 0xFFFF else 1))
        ranges = {group: [] for group in UIAssets.SYNTAX_COLORS}
        for start, token, value in lexer.get_tokens_unprocessed(source):
            for family, group in self.GROUPS:
                if token in family and value:
                    ranges[group].extend((f"1.0+{offsets[start]}c",
                                          f"1.0+{offsets[start + len(value)]}c"))
                    break
        for group, indices in ranges.items():
            for start in range(0, len(indices), 1000):
                self.text.tag_add("syntax_" + group, *indices[start:start + 1000])
        self.text.tag_raise("sel")

    def close(self) -> None:
        """Cancel scheduled work before the editor is destroyed."""
        if self.pending is not None:
            self.text.after_cancel(self.pending)
            self.pending = None
