"""
ui/main_window.py

Main dashboard window: the redesigned 8-div grid skeleton for the PPL
Semantics Analyzer desktop UI. This is layout scaffolding only — "a
finished house with wires, but no furniture." No backend calls, no
real widget content beyond placeholders and non-functional visual
tabs/buttons.

Grid map (10 rows x 10 columns, 0-indexed). Column 9 is intentionally
left empty in the middle rows (2-8) for minimalistic whitespace — none
of div3/div4/div5/div6/div7/div8 reach it.

    div1  Header            : row=0, column=0, rowspan=2, columnspan=10
    div7  Analytics Title   : row=2, column=1, rowspan=1, columnspan=9
    div3  Sidebar 1          : row=2, column=0, rowspan=7, columnspan=1
    div8  Tools Sidebar     : row=3, column=1, rowspan=6, columnspan=2
    div4  Editor A          : row=3, column=3, rowspan=4, columnspan=3
    div5  Editor B          : row=3, column=6, rowspan=4, columnspan=3
    div6  Results           : row=7, column=3, rowspan=2, columnspan=6
    div2  Footer            : row=9, column=0, rowspan=1, columnspan=10

Do not change a div's grid position without discussing it with the
team first — other members are building against these coordinates.
See CONTRIBUTING.md for file/panel ownership.
"""

import customtkinter as ctk

from ui.ui_assets import UIAssets


class MainWindow(ctk.CTk):
    """Root dashboard window, built on the redesigned 10x10 grid.

    Attributes:
        div1_header: Top header bar frame (title + tab strip).
        appearance_switch: Dark Mode toggle switch, placed in div1_header.
        div7_analytics_title: Thin title bar above the tools/editors row.
        div3_sidebar_1: Leftmost single-column sidebar frame.
        div8_tools_sidebar: Secondary tools sidebar, right of div3.
        div4_editor_a: Code editor frame for Snippet A.
        div5_editor_b: Code editor frame for Snippet B.
        div6_results: Results/output strip beneath the editors.
        div2_footer: Bottom footer frame.
    """

    GRID_SIZE = 10

    # Non-functional placeholder labels for the header tab strip.
    HEADER_TABS = ["Static AST", "Runtime", "PPL Verdict"]

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
        self._window_width = 1440
        self._window_height = 900
        UIAssets.center_window(self, self._window_width, self._window_height)
        self.minsize(1100, 700)
        self.configure(fg_color=UIAssets.COLORS["BG_PRIMARY"])

        self._configure_grid()
        self._build_header()
        self._build_analytics_title()
        self._build_sidebar_1()
        self._build_tools_sidebar()
        self._build_editor_a()
        self._build_editor_b()
        self._build_results()
        self._build_footer()

    def _configure_grid(self) -> None:
        """Configure the 10x10 row/column weights on the root window.

        The header (rows 0-1) and footer (row 9) are pinned to a small
        minsize and given zero resize weight so they stay thin; column
        9 gets zero weight everywhere so the reserved whitespace column
        stays narrow rather than stretching with the window.

        Args:
            None.

        Returns:
            None.
        """
        for column in range(self.GRID_SIZE):
            self.grid_columnconfigure(column, weight=1)

        for row in range(self.GRID_SIZE):
            self.grid_rowconfigure(row, weight=1)

        self.grid_rowconfigure(0, weight=0, minsize=36)
        self.grid_rowconfigure(1, weight=0, minsize=36)
        self.grid_rowconfigure(9, weight=0, minsize=32)
        self.grid_columnconfigure(9, weight=0, minsize=24)

    # ------------------------------------------------------------------
    # div1 — Header
    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        """Build div1: header bar with title and a placeholder tab strip.

        Args:
            None.

        Returns:
            None.
        """
        self.div1_header = ctk.CTkFrame(self, **UIAssets.debug_frame_kwargs(0))
        self.div1_header.grid(
            row=0, column=0, rowspan=2, columnspan=10,
            sticky="nsew", padx=1, pady=1,
        )
        self.div1_header.grid_columnconfigure(0, weight=1)
        self.div1_header.grid_columnconfigure(1, weight=0)
        self.div1_header.grid_columnconfigure(2, weight=0)

        title = ctk.CTkLabel(
            self.div1_header,
            text="PARADIGM DIAGNOSTICS",
            **UIAssets.label_kwargs("h1"),
        )
        title.grid(row=0, column=0, padx=24, pady=(10, 2), sticky="w")

        tab_strip = ctk.CTkSegmentedButton(
            self.div1_header,
            values=self.HEADER_TABS,
            corner_radius=UIAssets.CORNER_RADIUS,
            border_width=UIAssets.BORDER_WIDTH,
            fg_color=UIAssets.COLORS["SURFACE"],
            selected_color=UIAssets.COLORS["BLUE"],
            selected_hover_color=UIAssets.COLORS["BLUE_PRESSED"],
            unselected_color=UIAssets.COLORS["SURFACE"],
            text_color=UIAssets.COLORS["TEXT_PRIMARY"],
            font=UIAssets.FONTS["BODY"],
            command=lambda _tab: None,  # visual only, no view-switch logic
        )
        tab_strip.set(self.HEADER_TABS[0])
        tab_strip.grid(row=0, column=1, rowspan=2, padx=(24, 12), pady=10, sticky="e")

        self._build_appearance_switch(parent=self.div1_header, column=2)

    def _build_appearance_switch(self, parent, column: int) -> None:
        """Build the Dark Mode toggle and place it in the header.

        Args:
            parent: The container to place the switch in (div1_header).
            column: The grid column within `parent` to place it at.

        Returns:
            None.
        """
        self.appearance_switch_var = ctk.StringVar(value="dark")
        self.appearance_switch = ctk.CTkSwitch(
            parent,
            text="Dark Mode",
            variable=self.appearance_switch_var,
            onvalue="dark",
            offvalue="light",
            command=self._on_toggle_appearance,
            **UIAssets.switch_kwargs(),
        )
        self.appearance_switch.select()  # matches apply_theme()'s Dark default
        self.appearance_switch.grid(
            row=0, column=column, rowspan=2, padx=(0, 24), pady=10, sticky="e",
        )

    def _on_toggle_appearance(self) -> None:
        """Flip the global CustomTkinter appearance mode from the switch.

        Args:
            None.

        Returns:
            None.
        """
        UIAssets.set_dark_mode(self.appearance_switch_var.get() == "dark")

    # ------------------------------------------------------------------
    # div7 — Analytics Title
    # ------------------------------------------------------------------
    def _build_analytics_title(self) -> None:
        """Build div7: thin title bar above the tools/editor row.

        Args:
            None.

        Returns:
            None.
        """
        self.div7_analytics_title = ctk.CTkFrame(
            self, **UIAssets.debug_frame_kwargs(1),
        )
        self.div7_analytics_title.grid(
            row=2, column=1, rowspan=1, columnspan=9,
            sticky="nsew", padx=1, pady=1,
        )

        label = ctk.CTkLabel(
            self.div7_analytics_title,
            text="div7 — ANALYTICS TITLE",
            **UIAssets.label_kwargs("label"),
        )
        label.configure(text_color=UIAssets.COLORS["TEXT_MUTED"])
        label.place(relx=0.02, rely=0.5, anchor="w")

    # ------------------------------------------------------------------
    # div3 — Sidebar 1
    # ------------------------------------------------------------------
    def _build_sidebar_1(self) -> None:
        """Build div3: leftmost single-column sidebar frame.

        Args:
            None.

        Returns:
            None.
        """
        self.div3_sidebar_1 = self._make_stub(
            "div3\nSIDEBAR 1",
            row=2, column=0, rowspan=7, columnspan=1,
            palette_index=2,
        )

    # ------------------------------------------------------------------
    # div8 — Tools Sidebar
    # ------------------------------------------------------------------
    def _build_tools_sidebar(self) -> None:
        """Build div8: secondary tools sidebar, right of div3.

        Args:
            None.

        Returns:
            None.
        """
        self.div8_tools_sidebar = self._make_stub(
            "div8\nTOOLS SIDEBAR",
            row=3, column=1, rowspan=6, columnspan=2,
            palette_index=3,
        )

    # ------------------------------------------------------------------
    # div4 — Editor A
    # ------------------------------------------------------------------
    def _build_editor_a(self) -> None:
        """Build div4: code editor stub for Snippet A.

        Args:
            None.

        Returns:
            None.
        """
        self.div4_editor_a = self._make_stub(
            "div4\nEDITOR A",
            row=3, column=3, rowspan=4, columnspan=3,
            palette_index=4,
        )

    # ------------------------------------------------------------------
    # div5 — Editor B
    # ------------------------------------------------------------------
    def _build_editor_b(self) -> None:
        """Build div5: code editor stub for Snippet B.

        Args:
            None.

        Returns:
            None.
        """
        self.div5_editor_b = self._make_stub(
            "div5\nEDITOR B",
            row=3, column=6, rowspan=4, columnspan=3,
            palette_index=0,
        )

    # ------------------------------------------------------------------
    # div6 — Results
    # ------------------------------------------------------------------
    def _build_results(self) -> None:
        """Build div6: results/output strip beneath the editors.

        Args:
            None.

        Returns:
            None.
        """
        self.div6_results = self._make_stub(
            "div6\nRESULTS",
            row=7, column=3, rowspan=2, columnspan=6,
            palette_index=1,
        )

    # ------------------------------------------------------------------
    # div2 — Footer
    # ------------------------------------------------------------------
    def _build_footer(self) -> None:
        """Build div2: bottom footer frame.

        Args:
            None.

        Returns:
            None.
        """
        self.div2_footer = self._make_stub(
            "div2 — FOOTER",
            row=9, column=0, rowspan=1, columnspan=10,
            palette_index=2,
        )

    def _make_stub(
        self,
        label_text: str,
        row: int,
        column: int,
        rowspan: int,
        columnspan: int,
        palette_index: int,
    ) -> ctk.CTkFrame:
        """Create a single flat, tinted stub frame with a centered label.

        Args:
            label_text: Text shown inside the placeholder, identifying
                which div this frame corresponds to.
            row: Grid row to place the frame at.
            column: Grid column to place the frame at.
            rowspan: Number of rows the frame spans.
            columnspan: Number of columns the frame spans.
            palette_index: Index into `UIAssets.DEBUG_PALETTE`, used so
                adjacent panels get visually distinct tints.

        Returns:
            ctk.CTkFrame: The created and gridded frame, kept as an
            instance attribute by the caller for later reference.
        """
        frame = ctk.CTkFrame(
            self, **UIAssets.debug_frame_kwargs(palette_index),
        )
        frame.grid(
            row=row, column=column, rowspan=rowspan, columnspan=columnspan,
            sticky="nsew", padx=1, pady=1,
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
    # Quick visual check of the dashboard without going through main.py.
    app = MainWindow()
    app.mainloop()