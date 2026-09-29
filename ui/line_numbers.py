"""Read-only line-number gutter aligned to a CustomTkinter source editor.

Numbers are canvas labels, never part of the source text. We draw only visible
lines at Tk's actual display coordinates, so scrollbar dragging, keyboard
navigation, resizing, and horizontal scrolling cannot desynchronize the gutter.
"""

import tkinter as tk
from tkinter import font as tkfont

import customtkinter as ctk

from ui.ui_assets import UIAssets


class LineNumberGutter(ctk.CTkFrame):
    """Render one editor's visible logical line numbers using its own font."""

    def __init__(self, master, editor: ctk.CTkTextbox) -> None:
        """Attach edit, layout, and scroll notifications to a source textbox.

        Args:
            master: Shared container for the gutter and source editor.
            editor: CTkTextbox displaying source with wrapping disabled.
        Returns:
            None.
        """
        super().__init__(master, width=44, **UIAssets.frame_kwargs(border=False))
        self.editor = editor
        # CTk exposes dlineinfo(), but its coordinates refer to its inner Text.
        # Find that native child by type rather than depending on a private name.
        self.text = next(
            child for child in editor.winfo_children() if isinstance(child, tk.Text)
        )
        self.pending_redraw = None
        self.gutter_width = 0
        self.surface = tk.Canvas(
            self, highlightthickness=0, borderwidth=0, takefocus=False
        )
        self.surface.place(x=0, y=0, relwidth=1, relheight=1)
        self.surface.bind("<Configure>", self._request_redraw)
        self.bindings = [
            (event, self.text.bind(event, self._request_redraw, add="+"))
            for event in ("<<Modified>>", "<Configure>")
        ]
        # Preserve CTk's scrollbar callback: replacing it outright would make
        # the code scroll while leaving its scrollbar thumb in the wrong place.
        # Some CTk versions do not expose this option through the wrapper.
        # The native Text owns it, so read and configure it there directly.
        self.original_scroll_command = self.text.cget("yscrollcommand")
        self.text.configure(yscrollcommand=self._on_scroll)
        self._request_redraw()

    def _on_scroll(self, first: str, last: str) -> None:
        """Update the original scrollbar and schedule aligned line labels.

        Args:
            first: Fraction of the document above the visible viewport.
            last: Fraction at the viewport's bottom edge.
        Returns:
            None.
        """
        if self.original_scroll_command:
            self.tk.call(*self.tk.splitlist(self.original_scroll_command), first, last)
        self._request_redraw()

    def _request_redraw(self, event=None) -> None:
        """Coalesce repeated notifications into one redraw after Tk lays out text.

        Args:
            event: Optional Tk edit/resize event; its payload is not needed.
        Returns:
            None.
        """
        if self.pending_redraw is None:
            self.pending_redraw = self.after_idle(self._redraw)

    def _redraw(self) -> None:
        """Draw visible numbers at their source lines' actual vertical positions.

        Args:
            None.
        Returns:
            None. Blank documents still have line 1; a final newline adds a line.
        """
        self.pending_redraw = None
        self.surface.delete("all")
        self.surface.configure(
            background=self._apply_appearance_mode(UIAssets.COLORS["GUTTER_BG"])
        )
        font = tkfont.Font(root=self.surface, font=self.text.cget("font"))
        line_count = int(self.editor.index("end-1c").split(".")[0])
        padding = round(10 * self._get_widget_scaling())
        width = font.measure(str(max(99, line_count))) + 2 * padding
        if width != self.gutter_width:
            self.gutter_width = width
            self.configure(width=width / self._get_widget_scaling())

        # Text and gutter include different internal padding. Their root-space
        # origin difference accounts for CTk's border, padding, and DPI scaling.
        offset = self.text.winfo_rooty() - self.surface.winfo_rooty()
        index = self.editor.index("@0,0 linestart")
        while True:
            position = self.editor.dlineinfo(index)
            if position is None:
                break
            line = index.split(".")[0]
            self.surface.create_text(
                width - padding,
                offset + position[1],
                anchor="ne",
                text=line,
                font=self.text.cget("font"),
                fill=self._apply_appearance_mode(UIAssets.COLORS["TEXT_MUTED"]),
            )
            index = self.editor.index(f"{index} + 1 line")

    def _set_appearance_mode(self, mode_string: str) -> None:
        """Refresh the native canvas when CustomTkinter changes theme.

        Args:
            mode_string: Appearance mode supplied by CustomTkinter.
        Returns:
            None.
        """
        super()._set_appearance_mode(mode_string)
        if hasattr(self, "surface"):
            self._request_redraw()

    def _set_scaling(self, *args, **kwargs) -> None:
        """Remeasure number widths when widget or display scaling changes.

        Args:
            args: Scaling values passed by CustomTkinter.
            kwargs: Additional CustomTkinter scaling arguments.
        Returns:
            None.
        """
        super()._set_scaling(*args, **kwargs)
        if hasattr(self, "surface"):
            self.gutter_width = 0
            self._request_redraw()

    def destroy(self) -> None:
        """Remove pending callbacks and restore the editor's scroll callback.

        Args:
            None.
        Returns:
            None.
        """
        if self.pending_redraw is not None:
            self.after_cancel(self.pending_redraw)
        if self.text.winfo_exists():
            self.text.configure(yscrollcommand=self.original_scroll_command)
            for event, binding in self.bindings:
                self.text.unbind(event, binding)
        super().destroy()
