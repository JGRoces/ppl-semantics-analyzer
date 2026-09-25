"""
ui/main_window.py

Main application window: a 10x10 grid skeleton for the PPL Semantics
Analyzer desktop UI. This module lays out the frame structure ONLY —
no backend wiring, no widget content beyond placeholder labels. Each
div is a stub CTkFrame ready for a team member to build out.

Grid map (10 rows x 10 columns, 0-indexed):

    row 0             : div1  Header                    (col 0-9)
    rows 1-7, col 0-1 : div3  Left Rail (config/run)
    rows 1-7, col 2-4 : div5  Code Editor — Snippet A
    rows 1-7, col 5-7 : div6  Code Editor — Snippet B
    rows 1-7, col 8-9 : div4  Right Rail (status/metadata)
    row 8             : div7  Analytics / Comparison     (col 0-9)
    row 9             : div2  Footer                     (col 0-9)

Do not change a div's grid position without discussing it with the
team first — other members are building against these coordinates.
See CONTRIBUTING.md for file/panel ownership.
"""

import customtkinter as ctk

from ui.ui_assets import UIAssets


class MainWindow(ctk.CTk):
    """Root application window, built on a fixed 10x10 grid.

    Attributes:
        div1_header: Top header bar frame.
        div3_left_rail: Left-side configuration/run-controls frame.
        div5_editor_a: Code editor frame for Snippet A.
        div6_editor_b: Code editor frame for Snippet B.
        div4_right_rail: Right-side status/metadata frame.
        div7_analytics: Bottom analytics/comparison panel frame
            (Static AST / Runtime / PPL Verdict tabs live here).
        div2_footer: Bottom footer frame.
    """

    GRID_SIZE = 10

    def __init__(self) -> None:
        """Initialize the window, apply the theme, and build the grid.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()

        UIAssets.apply_theme()

        self.title("PPL Semantics Analyzer")
        self.geometry("1440x900")
        self.minsize(1100, 700)
        self.configure(fg_color=UIAssets.COLORS["BG_PRIMARY"])

        self._configure_grid()
        self._build_stub_frames()

    def _configure_grid(self) -> None:
        """Configure the 10x10 row/column weights on the root window.

        The header (row 0) and footer (row 9) are pinned to a small
        minsize and given zero resize weight so they stay thin; the
        body rows (1-7) and the analytics row (8) absorb the rest of
        the available space.

        Args:
            None.

        Returns:
            None.
        """
        for column in range(self.GRID_SIZE):
            self.grid_columnconfigure(column, weight=1)

        for row in range(self.GRID_SIZE):
            self.grid_rowconfigure(row, weight=1)

        self.grid_rowconfigure(0, weight=0, minsize=56)
        self.grid_rowconfigure(9, weight=0, minsize=32)

    def _build_stub_frames(self) -> None:
        """Create and place every placeholder div frame on the grid.

        Each frame is an empty, labeled stub. Team members replace the
        placeholder CTkLabel inside their assigned frame with real
        widgets; the frame reference and grid position stay put so
        other panels aren't disturbed.

        Args:
            None.

        Returns:
            None.
        """
        self.div1_header = self._make_stub(
            "div1 — HEADER", row=0, column=0, rowspan=1, columnspan=10,
        )

        self.div3_left_rail = self._make_stub(
            "div3 — LEFT RAIL\n(language select / run controls)",
            row=1, column=0, rowspan=7, columnspan=2,
        )

        self.div5_editor_a = self._make_stub(
            "div5 — CODE EDITOR\n(Snippet A)",
            row=1, column=2, rowspan=7, columnspan=3,
        )

        self.div6_editor_b = self._make_stub(
            "div6 — CODE EDITOR\n(Snippet B)",
            row=1, column=5, rowspan=7, columnspan=3,
        )

        self.div4_right_rail = self._make_stub(
            "div4 — RIGHT RAIL\n(status / metadata)",
            row=1, column=8, rowspan=7, columnspan=2,
        )

        self.div7_analytics = self._make_stub(
            "div7 — ANALYTICS / COMPARISON\n(Static AST / Runtime / PPL Verdict)",
            row=8, column=0, rowspan=1, columnspan=10,
        )

        self.div2_footer = self._make_stub(
            "div2 — FOOTER", row=9, column=0, rowspan=1, columnspan=10,
        )

    def _make_stub(
        self,
        label_text: str,
        row: int,
        column: int,
        rowspan: int = 1,
        columnspan: int = 1,
    ) -> ctk.CTkFrame:
        """Create a single flat, bordered stub frame with a centered label.

        Args:
            label_text: Text shown inside the placeholder, identifying
                which div this frame corresponds to and its intended
                purpose.
            row: Grid row to place the frame at.
            column: Grid column to place the frame at.
            rowspan: Number of rows the frame spans. Defaults to 1.
            columnspan: Number of columns the frame spans. Defaults to 1.

        Returns:
            ctk.CTkFrame: The created and gridded frame, kept as an
            instance attribute by the caller for later reference.
        """
        frame = ctk.CTkFrame(self, **UIAssets.frame_kwargs())
        frame.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            sticky="nsew",
            padx=1,
            pady=1,
        )

        placeholder = ctk.CTkLabel(
            frame,
            text=label_text,
            justify="center",
            **UIAssets.label_kwargs("label"),
        )
        placeholder.configure(text_color=UIAssets.COLORS["TEXT_MUTED"])
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

        return frame


if __name__ == "__main__":
    # Quick visual check of the skeleton without going through main.py.
    app = MainWindow()
    app.mainloop()
