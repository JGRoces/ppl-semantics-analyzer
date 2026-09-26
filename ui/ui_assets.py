"""
ui/ui_assets.py

Central design-system manager for the PPL Semantics Analyzer desktop UI.

This module is the single source of truth for color, typography, and
theming rules. No other module should hard-code a hex value, font tuple,
or corner radius — import from here instead.

Design language: 100% flat. Boxy. Sharp. No rounded corners, no
gradients, no drop shadows.
"""

import customtkinter as ctk


class UIAssets:
    """Design tokens and global theme enforcement for the app.

    Attributes:
        COLORS: Named color tokens. Mode-aware tokens (surfaces, borders,
            text) are (light_value, dark_value) tuples that CustomTkinter
            resolves against the current appearance mode; accent colors
            and a few "always white" tokens are plain hex strings used
            unchanged in both modes.
        FONTS: Named font tuples (family, size, weight) for UI text and
            code display.
        CORNER_RADIUS: The single global corner radius value (always 0).
        BORDER_WIDTH: The default hairline border width, in pixels.
    """

    # ------------------------------------------------------------------
    # Color Palette
    # ------------------------------------------------------------------
    # Mode-aware tokens are (light_value, dark_value) tuples. CustomTkinter
    # resolves a tuple automatically against the current appearance mode
    # and re-renders any widget holding one when ctk.set_appearance_mode()
    # is called — that's what makes the Dark Mode switch work without any
    # manual widget reconfiguration. Tokens that should look the same in
    # both modes (accent colors, "always white" text) stay a single hex
    # string, which CTk also accepts unchanged.
    COLORS = {
        # Absolute constants (not mode-aware; used to build the tuples below)
        "PURE_BLACK": "#000000",
        "BLACK": "#0A0A0A",
        "WHITE": "#FFFFFF",

        # Surfaces — Pure White bg in Light, Pure Black bg in Dark
        "BG_PRIMARY": ("#FFFFFF", "#0A0A0A"),
        "BG_SECONDARY": ("#FFFFFF", "#000000"),
        "SURFACE": ("#FFFFFF", "#0A0A0A"),
        "CODE_BG": ("#FFFFFF", "#000000"),
        "BORDER": ("#000000", "#FFFFFF"),

        # Text — Black text in Light, White text in Dark
        "TEXT_PRIMARY": ("#000000", "#FFFFFF"),
        "TEXT_MUTED": ("#5A5A5A", "#B5B5B5"),
        "TEXT_ON_ACCENT": "#FFFFFF",  # accent buttons stay dark-ish in both modes

        # Accents — used strategically, not decoratively. Same in both
        # modes so "blue means primary action" never changes meaning.
        "BLUE": "#2F6FED",    # primary actions (run, load, save)
        "RED": "#E53A3A",     # warnings, errors, destructive actions
        "GREEN": "#2FB350",   # success / valid states

        # Hover / pressed variants — stay flat, just deeper
        "BLUE_PRESSED": "#2558BE",
        "RED_PRESSED": "#B92E2E",
        "GREEN_PRESSED": "#249142",

        # Scaffolding tints — flat, muted, desaturated surfaces used ONLY
        # to make stub/placeholder panels visually distinguishable during
        # layout review. Each is (light_tint, dark_tint). Solid hex, no
        # alpha/gradient. Swap a panel's real fg_color to "SURFACE" once
        # it has real content.
        "TINT_BLUE": ("#DCE6FB", "#12203D"),
        "TINT_RED": ("#FBE0E0", "#3A1414"),
        "TINT_GREEN": ("#DFF3E4", "#12301C"),
        "TINT_NEUTRAL_A": ("#F2F2F2", "#161616"),
        "TINT_NEUTRAL_B": ("#E8E8E8", "#1F1F1F"),
    }

    # Cycled by debug_frame_kwargs() to give scaffolding panels distinct,
    # still-flat backgrounds so layout boundaries read clearly at a glance.
    DEBUG_PALETTE = [
        "TINT_BLUE",
        "TINT_RED",
        "TINT_GREEN",
        "TINT_NEUTRAL_A",
        "TINT_NEUTRAL_B",
    ]

    # ------------------------------------------------------------------
    # Typography
    # ------------------------------------------------------------------
    # CTk accepts a tuple of (family, size) or (family, size, weight).
    # Families use system-safe defaults; CustomTkinter substitutes a
    # fallback automatically if a family is unavailable on the host OS.
    FONTS = {
        "UI_FAMILY": "Segoe UI",
        "MONO_FAMILY": "Consolas",

        "H1": ("Segoe UI", 22, "bold"),
        "H2": ("Segoe UI", 16, "bold"),
        "BODY": ("Segoe UI", 13, "normal"),
        "LABEL": ("Segoe UI", 11, "normal"),
        "BUTTON": ("Segoe UI", 13, "bold"),
        "CODE": ("Consolas", 13, "normal"),
        "CODE_SMALL": ("Consolas", 11, "normal"),
    }

    # The one number that defines the "boxy" aesthetic. Every widget
    # factory below enforces this at the call site.
    CORNER_RADIUS = 0
    BORDER_WIDTH = 1

    @classmethod
    def apply_theme(cls) -> None:
        """Apply the global CustomTkinter appearance settings.

        CustomTkinter has no single switch for "corner_radius=0
        everywhere" — each widget instance takes its own corner_radius
        kwarg. This method sets what CAN be set globally (appearance
        mode, base color scale); the `*_kwargs()` helpers below are
        what actually enforce sharp corners on each widget. Defaults to
        Dark mode; call `set_dark_mode(False)` (e.g. from a toggle) to
        switch to Light at runtime.

        Args:
            None.

        Returns:
            None.
        """
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

    @classmethod
    def set_dark_mode(cls, enabled: bool) -> None:
        """Switch the global CustomTkinter appearance mode at runtime.

        Every widget built with a mode-aware (light, dark) color tuple
        from `COLORS` re-renders automatically when this is called — no
        manual widget reconfiguration needed.

        Args:
            enabled: True to switch to Dark mode, False for Light mode.

        Returns:
            None.
        """
        ctk.set_appearance_mode("Dark" if enabled else "Light")

    @staticmethod
    def center_window(window, width: int, height: int) -> None:
        """Center a Tk/CTk window on the primary monitor and set its size.

        Args:
            window: The Tk or CTk root window to position. Must expose
                `winfo_screenwidth()`, `winfo_screenheight()`, and
                `geometry()` (true of both `ctk.CTk` and `tk.Tk`).
            width: Desired window width, in pixels.
            height: Desired window height, in pixels.

        Returns:
            None.
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    @classmethod
    def switch_kwargs(cls) -> dict:
        """Return standard kwargs for a flat CTkSwitch (e.g. dark-mode toggle).

        Note: CTkSwitch's circular handle has no `corner_radius` control
        in CustomTkinter's public API (only `corner_radius` for the
        track is supported) — the handle stays round regardless. This
        is a known, accepted exception to the "no rounded corners" rule
        for this one control.

        Args:
            None.

        Returns:
            dict: Keyword arguments to unpack into a CTkSwitch
            constructor.
        """
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS["TINT_NEUTRAL_A"],
            "progress_color": cls.COLORS["BLUE"],
            "button_color": cls.COLORS["BORDER"],
            "button_hover_color": cls.COLORS["TEXT_MUTED"],
            "text_color": cls.COLORS["TEXT_PRIMARY"],
            "font": cls.FONTS["LABEL"],
        }

    @classmethod
    def frame_kwargs(cls, border: bool = True) -> dict:
        """Return standard kwargs for a flat, boxy CTkFrame.

        Args:
            border: Whether the frame should render a 1px hairline
                border. Defaults to True.

        Returns:
            dict: Keyword arguments to unpack into a CTkFrame
            constructor.
        """
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS["SURFACE"],
            "border_width": cls.BORDER_WIDTH if border else 0,
            "border_color": cls.COLORS["BORDER"],
        }

    @classmethod
    def debug_frame_kwargs(cls, index: int, border: bool = True) -> dict:
        """Return flat CTkFrame kwargs with a scaffolding tint for visibility.

        Cycles through `DEBUG_PALETTE` by index so adjacent stub panels in
        a grid layout are easy to tell apart during layout review. Still
        fully flat (corner_radius=0, solid fg_color) — this is a layout
        aid, not a themed final look.

        Args:
            index: Position of this panel in the layout (e.g. its
                enumeration order). Wraps around via modulo, so any
                non-negative int is safe to pass.
            border: Whether the frame should render a 1px hairline
                border. Defaults to True.

        Returns:
            dict: Keyword arguments to unpack into a CTkFrame
            constructor.
        """
        tint_key = cls.DEBUG_PALETTE[index % len(cls.DEBUG_PALETTE)]
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS[tint_key],
            "border_width": cls.BORDER_WIDTH if border else 0,
            "border_color": cls.COLORS["BORDER"],
        }

    @classmethod
    def button_kwargs(cls, variant: str = "primary") -> dict:
        """Return standard kwargs for a flat CTkButton in a given variant.

        Args:
            variant: One of "primary" (blue), "danger" (red), or
                "success" (green).

        Returns:
            dict: Keyword arguments to unpack into a CTkButton
            constructor.

        Raises:
            ValueError: If variant is not a recognized option.
        """
        variants = {
            "primary": (cls.COLORS["BLUE"], cls.COLORS["BLUE_PRESSED"]),
            "danger": (cls.COLORS["RED"], cls.COLORS["RED_PRESSED"]),
            "success": (cls.COLORS["GREEN"], cls.COLORS["GREEN_PRESSED"]),
        }
        if variant not in variants:
            raise ValueError(f"Unknown button variant: {variant!r}")

        fg_color, hover_color = variants[variant]
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": fg_color,
            "hover_color": hover_color,
            "text_color": cls.COLORS["TEXT_ON_ACCENT"],
            "font": cls.FONTS["BUTTON"],
            "border_width": 0,
        }

    @classmethod
    def textbox_kwargs(cls) -> dict:
        """Return standard kwargs for a flat CTkTextbox (code editors).

        Args:
            None.

        Returns:
            dict: Keyword arguments to unpack into a CTkTextbox
            constructor.
        """
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS["CODE_BG"],
            "text_color": cls.COLORS["TEXT_PRIMARY"],
            "border_width": cls.BORDER_WIDTH,
            "border_color": cls.COLORS["BORDER"],
            "font": cls.FONTS["CODE"],
        }

    @classmethod
    def label_kwargs(cls, style: str = "body") -> dict:
        """Return standard kwargs for a CTkLabel in a given text style.

        Args:
            style: One of "h1", "h2", "body", or "label".

        Returns:
            dict: Keyword arguments to unpack into a CTkLabel
            constructor.

        Raises:
            ValueError: If style is not a recognized option.
        """
        font_map = {
            "h1": cls.FONTS["H1"],
            "h2": cls.FONTS["H2"],
            "body": cls.FONTS["BODY"],
            "label": cls.FONTS["LABEL"],
        }
        if style not in font_map:
            raise ValueError(f"Unknown label style: {style!r}")

        return {
            "font": font_map[style],
            "text_color": cls.COLORS["TEXT_PRIMARY"],
        }