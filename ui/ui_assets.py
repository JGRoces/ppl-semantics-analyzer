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
        COLORS: Named hex values for backgrounds, foregrounds, borders,
            text, and accent states.
        FONTS: Named font tuples (family, size, weight) for UI text and
            code display.
        CORNER_RADIUS: The single global corner radius value (always 0).
        BORDER_WIDTH: The default hairline border width, in pixels.
    """

    # ------------------------------------------------------------------
    # Color Palette
    # ------------------------------------------------------------------
    COLORS = {
        # Base
        "PURE_BLACK": "#000000",
        "BLACK": "#0A0A0A",
        "WHITE": "#FFFFFF",

        # Surfaces
        "BG_PRIMARY": "#0A0A0A",
        "BG_SECONDARY": "#000000",
        "SURFACE": "#0A0A0A",
        "BORDER": "#FFFFFF",

        # Text
        "TEXT_PRIMARY": "#FFFFFF",
        "TEXT_MUTED": "#B5B5B5",
        "TEXT_ON_ACCENT": "#FFFFFF",

        # Accents — used strategically, not decoratively
        "BLUE": "#2F6FED",    # primary actions (run, load, save)
        "RED": "#E53A3A",     # warnings, errors, destructive actions
        "GREEN": "#2FB350",   # success / valid states

        # Hover / pressed variants — stay flat, just deeper
        "BLUE_PRESSED": "#2558BE",
        "RED_PRESSED": "#B92E2E",
        "GREEN_PRESSED": "#249142",
    }

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
        what actually enforce sharp corners on each widget.

        Args:
            None.

        Returns:
            None.
        """
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

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
            "fg_color": cls.COLORS["PURE_BLACK"],
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
