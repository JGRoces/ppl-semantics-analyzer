"""Split welcome screen inspired by LoginGUI and SignUpChoiceGUI.

The branding/setup split and choice cards are adapted to language selection.
The application needs no accounts; Start passes saved settings to the dashboard.
"""

import customtkinter as ctk

from core.examples import LANGUAGE_LABELS
from ui.ui_assets import UIAssets


class LauncherWindow(ctk.CTkFrame):
    """Select a comparison pair before entering the diagnostics workspace."""

    LANGUAGE_OPTIONS = list(LANGUAGE_LABELS)

    def __init__(self, master, on_start, on_cancel) -> None:
        """Create the welcome page inside the application's persistent window.

        Args:
            master: Persistent application root.
            on_start: Callback receiving the selected language pair and theme.
            on_cancel: Callback closing the application.
        Returns:
            None.
        """
        super().__init__(
            master,
            fg_color=UIAssets.COLORS["BG_PRIMARY"],
            corner_radius=UIAssets.SHELL_RADIUS,
        )
        self.on_start = on_start
        self.on_cancel = on_cancel
        self.result = "cancelled"
        self.selected_languages = ("Python", "JavaScript")
        self.dark_mode = False
        self.grid_columnconfigure(0, weight=3, uniform="split")
        self.grid_columnconfigure(1, weight=2, uniform="split")
        self.grid_rowconfigure(0, weight=1)
        self._build_brand()
        self._build_setup()
        self.return_binding = master.bind(
            "<Return>", lambda event: self._on_start(), add="+"
        )

    def _build_brand(self) -> None:
        """Present the brand and a code example in the reference's left panel.

        Args:
            None.
        Returns:
            None.
        """
        self.brand_panel = ctk.CTkFrame(
            self,
            fg_color=UIAssets.COLORS["BG_PRIMARY"],
            corner_radius=UIAssets.SHELL_RADIUS,
        )
        self.brand_panel.grid(row=0, column=0, sticky="nsew")
        inner = ctk.CTkFrame(self.brand_panel, fg_color="transparent")
        inner.pack(expand=True, fill="x", padx=44, pady=30)
        UIAssets.accent_bar(inner).pack(anchor="w", pady=(0, 24))
        ctk.CTkLabel(
            inner, text="PARADIGM DIAGNOSTICS", **UIAssets.label_kwargs("h3")
        ).pack(anchor="w")
        ctk.CTkLabel(
            inner,
            text="Same idea.\nDifferent languages.",
            justify="left",
            **UIAssets.label_kwargs("display"),
        ).pack(anchor="w", pady=(22, 12))
        ctk.CTkLabel(
            inner,
            text="Explore the syntax. Observe the behavior.\nUnderstand what makes each language different.",
            justify="left",
            text_color=UIAssets.COLORS["TEXT_MUTED"],
            font=UIAssets.FONTS["BODY"],
        ).pack(anchor="w", pady=(0, 26))
        example = ctk.CTkFrame(
            inner,
            fg_color=UIAssets.COLORS["CHROME"],
            corner_radius=UIAssets.CARD_RADIUS,
        )
        example.pack(fill="x")
        ctk.CTkLabel(
            example,
            text="A SMALL PROGRAM. A BIG IDEA.",
            text_color=UIAssets.COLORS["CHROME_MUTED"],
            font=UIAssets.FONTS["LABEL"],
        ).pack(anchor="w", padx=22, pady=(18, 12))
        ctk.CTkLabel(
            example,
            text="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
            justify="left",
            font=UIAssets.FONTS["CODE"],
            text_color=UIAssets.COLORS["CODE_KEYWORD"],
        ).pack(anchor="w", padx=22, pady=(0, 18))
        ctk.CTkLabel(
            example,
            text="factorial(5)  →  120",
            font=UIAssets.FONTS["CODE"],
            text_color=UIAssets.COLORS["CODE_VALUE"],
        ).pack(anchor="w", padx=22, pady=(0, 20))
        ctk.CTkLabel(
            inner,
            text="PYTHON     /     JAVASCRIPT     /     C++",
            font=UIAssets.FONTS["LABEL"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        ).pack(anchor="w", pady=(24, 0))

    def _build_setup(self) -> None:
        """Build comparison choice cards, editable selectors, and Start/Cancel.

        Args:
            None.
        Returns:
            None.
        """
        self.setup_panel = ctk.CTkFrame(
            self,
            fg_color=UIAssets.COLORS["SURFACE"],
            corner_radius=UIAssets.SHELL_RADIUS,
        )
        self.setup_panel.grid(row=0, column=1, sticky="nsew")
        inner = ctk.CTkFrame(self.setup_panel, fg_color="transparent")
        inner.pack(expand=True, fill="x", padx=32, pady=26)
        ctk.CTkLabel(inner, text="Get started", **UIAssets.label_kwargs("h1")).pack(
            anchor="w"
        )
        ctk.CTkLabel(
            inner,
            text="Choose the languages you want to compare.",
            font=UIAssets.FONTS["BODY"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        ).pack(anchor="w", pady=(8, 24))
        self.pair_buttons = []
        for title, detail, pair in (
            (
                "Python + JavaScript",
                "Explore dynamic typing and coercion",
                ("Python", "JavaScript"),
            ),
            (
                "Python + C++",
                "Compare runtime and compile-time checks",
                ("Python", "C++"),
            ),
        ):
            button = ctk.CTkButton(
                inner,
                text=f"{title}   ›\n{detail}",
                height=72,
                anchor="w",
                command=lambda selected=pair: self._choose_pair(selected),
                **UIAssets.button_kwargs("secondary"),
            )
            button.pack(fill="x", pady=(0, 12))
            self.pair_buttons.append((button, pair))
        selectors = ctk.CTkFrame(inner, fg_color="transparent")
        selectors.pack(fill="x", pady=(10, 20))
        for column, name in enumerate(("Snippet A", "Snippet B")):
            selectors.grid_columnconfigure(column, weight=1)
            ctk.CTkLabel(selectors, text=name, **UIAssets.label_kwargs("label")).grid(
                row=0, column=column, sticky="w", pady=(0, 6)
            )
            menu = ctk.CTkOptionMenu(
                selectors,
                values=self.LANGUAGE_OPTIONS,
                width=130,
                command=self._sync_pair,
                **UIAssets.option_menu_kwargs(),
            )
            menu.grid(
                row=1, column=column, sticky="ew", padx=(0, 10) if column == 0 else 0
            )
            setattr(
                self, "language_a_combo" if column == 0 else "language_b_combo", menu
            )
        self._choose_pair(self.selected_languages)
        ctk.CTkButton(
            inner,
            text="Open workspace   →",
            height=42,
            command=self._on_start,
            **UIAssets.button_kwargs(),
        ).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(
            inner,
            text="Cancel",
            height=38,
            command=self._on_cancel,
            **UIAssets.button_kwargs("secondary"),
        ).pack(fill="x")
        ctk.CTkFrame(
            inner,
            height=1,
            fg_color=UIAssets.COLORS["BORDER"],
            corner_radius=UIAssets.SHELL_RADIUS,
        ).pack(fill="x", pady=(24, 18))
        self.appearance_switch_var = ctk.StringVar(value="light")
        self.appearance_switch = ctk.CTkSwitch(
            inner,
            text="Dark mode",
            variable=self.appearance_switch_var,
            onvalue="dark",
            offvalue="light",
            command=self._on_toggle_appearance,
            **UIAssets.switch_kwargs(),
        )
        self.appearance_switch.pack(anchor="w")
        ctk.CTkLabel(
            inner,
            text="Group 4  ·  Principles of Programming Languages",
            font=UIAssets.FONTS["LABEL"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        ).pack(anchor="w", pady=(20, 0))

    def _choose_pair(self, pair: tuple) -> None:
        """Select both languages from a comparison card.

        Args:
            pair: Two supported display labels.
        Returns:
            None.
        """
        self.language_a_combo.set(pair[0])
        self.language_b_combo.set(pair[1])
        self._sync_pair()

    def _sync_pair(self, value=None) -> None:
        """Highlight only the card matching the current selectors.

        Args:
            value: Optional selector callback value, unused.
        Returns:
            None.
        """
        selected = (self.language_a_combo.get(), self.language_b_combo.get())
        for button, pair in self.pair_buttons:
            button.configure(
                fg_color=UIAssets.COLORS[
                    "TINT_ACCENT" if pair == selected else "SURFACE"
                ],
                border_color=UIAssets.COLORS[
                    "ACCENT" if pair == selected else "BORDER"
                ],
            )

    def _on_toggle_appearance(self) -> None:
        """Apply the launcher appearance switch.

        Args:
            None.
        Returns:
            None.
        """
        UIAssets.set_dark_mode(self.appearance_switch_var.get() == "dark")

    def get_selected_languages(self) -> tuple:
        """Return the language labels saved during entry.

        Args:
            None.
        Returns:
            The pair copied before destroying Tk widgets.
        """
        return self.selected_languages

    def _on_start(self) -> None:
        """Pass settings to the persistent application window.

        Args:
            None.
        Returns:
            None.
        """
        self.selected_languages = (
            self.language_a_combo.get(),
            self.language_b_combo.get(),
        )
        self.dark_mode = self.appearance_switch_var.get() == "dark"
        if self.result == "start":
            return
        self.result = "start"
        self.master.unbind("<Return>", self.return_binding)
        self.on_start(self.selected_languages, self.dark_mode)

    def _on_cancel(self) -> None:
        """Close without opening a dashboard.

        Args:
            None.
        Returns:
            None.
        """
        self.result = "cancelled"
        self.on_cancel()
