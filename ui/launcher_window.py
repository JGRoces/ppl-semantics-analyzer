"""
ui/launcher_window.py

Entry launcher window for the PPL Semantics Analyzer — a small, centered
"diagnostics start" dialog shown before the main dashboard, in the style
of HWiNFO's launch screen. UI scaffolding only: the language combo boxes
are preloaded with static options and Start's only real action is to
close this window and hand off to MainWindow. No analysis/execution
logic lives here.

Grid map (10 rows x 10 columns, 0-indexed):

    div1  Center panel  : row=2, column=2, rowspan=6, columnspan=6
                           (title, language selects, Cancel / Start)

Everything outside div1 is bare canvas — intentional negative space
around the centered dialog, matching the launcher's minimal footprint.
"""

import customtkinter as ctk

from ui.ui_assets import UIAssets


class LauncherWindow(ctk.CTk):
    """Small centered launcher shown before the main dashboard.

    Attributes:
        div1_panel: The centered CTkFrame holding all launcher content.
        language_a_combo: Combo box for the first target language.
        language_b_combo: Combo box for the second target language.
        result: "start" if the user clicked Start Diagnostics, else
            "cancelled" (default, also set on window close / Cancel).
    """

    GRID_SIZE = 10

    # Preloaded options only — no validation or backend wiring here.
    LANGUAGE_OPTIONS = ["Python", "JavaScript", "C++"]

    def __init__(self) -> None:
        """Initialize the launcher window, theme, grid, and center panel.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__()

        UIAssets.apply_theme()

        self.result = "cancelled"

        self.title("PPL Semantics Analyzer — Launcher")
        self._window_width = 720
        self._window_height = 520
        UIAssets.center_window(self, self._window_width, self._window_height)
        self.resizable(False, False)
        self.configure(fg_color=UIAssets.COLORS["BG_PRIMARY"])

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._configure_grid()
        self._build_center_panel()
        self._build_appearance_switch()

    def _configure_grid(self) -> None:
        """Configure the 10x10 row/column weights on the root window.

        Args:
            None.

        Returns:
            None.
        """
        for index in range(self.GRID_SIZE):
            self.grid_columnconfigure(index, weight=1)
            self.grid_rowconfigure(index, weight=1)

    def _build_center_panel(self) -> None:
        """Build div1: the centered launcher card and its contents.

        Args:
            None.

        Returns:
            None.
        """
        self.div1_panel = ctk.CTkFrame(self, **UIAssets.frame_kwargs())
        self.div1_panel.grid(
            row=2, column=2, rowspan=6, columnspan=6, sticky="nsew",
        )

        # Inner content uses its own tight grid so it centers cleanly
        # regardless of div1's resolved pixel size.
        self.div1_panel.grid_columnconfigure(0, weight=1)
        for row in range(6):
            self.div1_panel.grid_rowconfigure(row, weight=1)

        title = ctk.CTkLabel(
            self.div1_panel,
            text="PARADIGM DIAGNOSTICS",
            **UIAssets.label_kwargs("h1"),
        )
        title.grid(row=0, column=0, pady=(28, 4), sticky="n")

        subtitle = ctk.CTkLabel(
            self.div1_panel,
            text="Select the languages to compare, then start.",
            **UIAssets.label_kwargs("body"),
        )
        subtitle.configure(text_color=UIAssets.COLORS["TEXT_MUTED"])
        subtitle.grid(row=1, column=0, pady=(0, 20), sticky="n")

        selects_row = ctk.CTkFrame(
            self.div1_panel, fg_color="transparent",
        )
        selects_row.grid(row=2, column=0, sticky="n")

        language_a_label = ctk.CTkLabel(
            selects_row, text="Target Language A", **UIAssets.label_kwargs("label"),
        )
        language_a_label.grid(row=0, column=0, padx=12, pady=(0, 4))

        language_b_label = ctk.CTkLabel(
            selects_row, text="Target Language B", **UIAssets.label_kwargs("label"),
        )
        language_b_label.grid(row=0, column=1, padx=12, pady=(0, 4))

        self.language_a_combo = ctk.CTkComboBox(
            selects_row,
            values=self.LANGUAGE_OPTIONS,
            corner_radius=UIAssets.CORNER_RADIUS,
            border_width=UIAssets.BORDER_WIDTH,
            fg_color=UIAssets.COLORS["SURFACE"],
            border_color=UIAssets.COLORS["BORDER"],
            button_color=UIAssets.COLORS["BLUE"],
            button_hover_color=UIAssets.COLORS["BLUE_PRESSED"],
            dropdown_fg_color=UIAssets.COLORS["SURFACE"],
            text_color=UIAssets.COLORS["TEXT_PRIMARY"],
            font=UIAssets.FONTS["BODY"],
        )
        self.language_a_combo.set(self.LANGUAGE_OPTIONS[0])
        self.language_a_combo.grid(row=1, column=0, padx=12, pady=(0, 8))

        self.language_b_combo = ctk.CTkComboBox(
            selects_row,
            values=self.LANGUAGE_OPTIONS,
            corner_radius=UIAssets.CORNER_RADIUS,
            border_width=UIAssets.BORDER_WIDTH,
            fg_color=UIAssets.COLORS["SURFACE"],
            border_color=UIAssets.COLORS["BORDER"],
            button_color=UIAssets.COLORS["BLUE"],
            button_hover_color=UIAssets.COLORS["BLUE_PRESSED"],
            dropdown_fg_color=UIAssets.COLORS["SURFACE"],
            text_color=UIAssets.COLORS["TEXT_PRIMARY"],
            font=UIAssets.FONTS["BODY"],
        )
        self.language_b_combo.set(self.LANGUAGE_OPTIONS[1])
        self.language_b_combo.grid(row=1, column=1, padx=12, pady=(0, 8))

        button_row = ctk.CTkFrame(self.div1_panel, fg_color="transparent")
        button_row.grid(row=4, column=0, pady=(24, 0), sticky="n")

        cancel_button = ctk.CTkButton(
            button_row,
            text="Cancel",
            command=self._on_cancel,
            width=140,
            **UIAssets.button_kwargs("danger"),
        )
        cancel_button.grid(row=0, column=0, padx=10)

        start_button = ctk.CTkButton(
            button_row,
            text="Start Diagnostics",
            command=self._on_start,
            width=180,
            **UIAssets.button_kwargs("primary"),
        )
        start_button.grid(row=0, column=1, padx=10)

        version_label = ctk.CTkLabel(
            self.div1_panel,
            text="v0.1.0 — UI scaffolding",
            **UIAssets.label_kwargs("label"),
        )
        version_label.configure(text_color=UIAssets.COLORS["TEXT_MUTED"])
        version_label.grid(row=5, column=0, pady=(20, 16), sticky="s")

    def _build_appearance_switch(self) -> None:
        """Build the Dark Mode toggle, pinned to the window's bottom-right.

        Placed directly on the root window (not inside div1) via
        `.place()` with relative coordinates, so it stays anchored to
        the corner regardless of div1's size.

        Args:
            None.

        Returns:
            None.
        """
        self.appearance_switch_var = ctk.StringVar(value="dark")
        self.appearance_switch = ctk.CTkSwitch(
            self,
            text="Dark Mode",
            variable=self.appearance_switch_var,
            onvalue="dark",
            offvalue="light",
            command=self._on_toggle_appearance,
            **UIAssets.switch_kwargs(),
        )
        self.appearance_switch.select()  # matches apply_theme()'s Dark default
        self.appearance_switch.place(relx=0.97, rely=0.96, anchor="se")

    def _on_toggle_appearance(self) -> None:
        """Flip the global CustomTkinter appearance mode from the switch.

        Args:
            None.

        Returns:
            None.
        """
        UIAssets.set_dark_mode(self.appearance_switch_var.get() == "dark")

    def get_selected_languages(self) -> tuple:
        """Return the two languages currently selected in the combo boxes.

        UI-layer convenience only — the caller decides what, if
        anything, to do with these values once backend wiring exists.

        Args:
            None.

        Returns:
            tuple: (language_a, language_b) as selected strings.
        """
        return (self.language_a_combo.get(), self.language_b_combo.get())

    def _on_start(self) -> None:
        """Mark the launcher's result as "start" and close the window.

        Args:
            None.

        Returns:
            None.
        """
        self.result = "start"
        self.destroy()

    def _on_cancel(self) -> None:
        """Mark the launcher's result as "cancelled" and close the window.

        Bound to both the Cancel button and the window's close (X)
        button, so either path leaves `self.result` consistent.

        Args:
            None.

        Returns:
            None.
        """
        self.result = "cancelled"
        self.destroy()


if __name__ == "__main__":
    # Quick visual check of the launcher without going through main.py.
    app = LauncherWindow()
    app.mainloop()
    print("Launcher result:", app.result)