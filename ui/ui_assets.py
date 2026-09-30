"""Shared visual tokens adapted from the team's Java Car Rental UIAssets.

The Python implementation keeps the reference's neutral page/surface hierarchy,
green navigation, terminal-green entry accents, typography scale, and rounded controls.
CustomTkinter resolves (light, dark) pairs instead of Java theme listeners.
"""

import customtkinter as ctk


class UIAssets:
    """Single source of truth for colors, fonts, radii and shared widget styles."""

    COLORS = {
        "PURE_BLACK": "#000000",
        "BLACK": "#0E0E0E",
        "WHITE": "#FFFFFF",
        "BG_PRIMARY": ("#EFEFEF", "#000000"),
        "BG_SECONDARY": ("#FFFFFF", "#0E0E0E"),
        "SURFACE": ("#FFFFFF", "#0E0E0E"),
        "CODE_BG": ("#FFFFFF", "#0E0E0E"),
        "GUTTER_BG": ("#F7F7F8", "#121212"),
        "BORDER": ("#DADADA", "#262626"),
        "TEXT_PRIMARY": ("#111111", "#F0F0F0"),
        "TEXT_MUTED": ("#6B6B6B", "#A0A0A0"),
        "TEXT_PLACEHOLDER": ("#969696", "#696969"),
        "TEXT_ON_ACCENT": "#FFFFFF",
        "ACCENT": "#15803D",
        "ACCENT_PRESSED": "#166534",
        "GREEN": "#16A34A",
        "BRAND_GREEN_1": "#166534",
        "BRAND_GREEN_2": "#15803D",
        "BRAND_GREEN_3": "#22C55E",
        "BRAND_GREEN_4": "#86EFAC",
        "GREEN_PRESSED": "#15803D",
        "BLUE": "#2563EB",
        "RED": "#DC2626",
        "RED_PRESSED": "#B91C1C",
        "TINT_ACCENT": ("#DCFCE7", "#12301E"),
        "TINT_GREEN": ("#DCFCE7", "#122C1D"),
        "TINT_BLUE": ("#DBEAFE", "#172554"),
        "TINT_RED": ("#FEE2E2", "#351717"),
        "TINT_NEUTRAL_A": ("#F5F5F5", "#1C1C1C"),
        "TINT_NEUTRAL_B": ("#E8E8E8", "#282828"),
        "CHROME": "#121212",
        "CHROME_BORDER": "#262626",
        "CHROME_TEXT": "#F0F0F0",
        "CHROME_MUTED": "#A0A0A0",
        "CODE_KEYWORD": "#4ADE80",
        "CODE_VALUE": "#86EFAC",
    }
    SYNTAX_COLORS = {
        "keyword": ("#166534", "#4ADE80"),
        "string": ("#15803D", "#86EFAC"),
        "comment": ("#6B6B6B", "#A0A0A0"),
        "number": ("#B91C1C", "#FCA5A5"),
        "function": ("#1D4ED8", "#93C5FD"),
    }
    FONTS = {
        "UI_FAMILY": "Segoe UI",
        "MONO_FAMILY": "Consolas",
        "DISPLAY": ("Segoe UI", 34, "bold"),
        "H1": ("Segoe UI", 22, "bold"),
        "H2": ("Segoe UI", 15, "bold"),
        "H3": ("Segoe UI", 13, "bold"),
        "BODY": ("Segoe UI", 13, "normal"),
        "LABEL": ("Segoe UI", 11, "normal"),
        "BUTTON": ("Segoe UI", 13, "bold"),
        "INPUT": ("Segoe UI", 14, "normal"),
        "STAT": ("Segoe UI", 32, "bold"),
        "CODE": ("Consolas", 13, "normal"),
        "CODE_SMALL": ("Consolas", 11, "normal"),
    }
    CORNER_RADIUS = 8
    CARD_RADIUS = 12
    SHELL_RADIUS = 0
    BORDER_WIDTH = 1
    SIDEBAR_WIDTH = 208
    SIDEBAR_COLLAPSED = 68
    DEBUG_PALETTE = ["TINT_ACCENT", "TINT_GREEN", "TINT_BLUE", "TINT_RED"]

    @classmethod
    def apply_theme(cls) -> None:
        """Start in the reference project's light appearance.

        Args:
            None.
        Returns:
            None; callers may immediately restore a user's chosen mode.
        """
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("green")

    @classmethod
    def set_dark_mode(cls, enabled: bool) -> None:
        """Switch all appearance-aware widgets together.

        Args:
            enabled: Whether to select dark appearance.
        Returns:
            None.
        """
        ctk.set_appearance_mode("Dark" if enabled else "Light")

    @staticmethod
    def center_window(window, width: int, height: int) -> None:
        """Center the native window on its current screen.

        Args:
            window: Tk root to position.
            width: Desired width in logical pixels.
            height: Desired height in logical pixels.
        Returns:
            None.
        """
        x = max(0, (window.winfo_screenwidth() - width) // 2)
        y = max(0, (window.winfo_screenheight() - height) // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    @classmethod
    def frame_kwargs(cls, border: bool = True) -> dict:
        """Style a surface card with a subtle border.

        Args:
            border: Whether the card needs a visible divider.
        Returns:
            CTkFrame constructor arguments.
        """
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS["SURFACE"],
            "border_width": cls.BORDER_WIDTH if border else 0,
            "border_color": cls.COLORS["BORDER"],
        }

    @classmethod
    def button_kwargs(cls, variant: str = "primary") -> dict:
        """Style an action, outlined secondary control, or quiet navigation item.

        Args:
            variant: primary, success, danger, secondary, or quiet.
        Returns:
            CTkButton constructor arguments.
        Raises:
            ValueError: An unknown variant was requested.
        """
        variants = {
            "primary": ("ACCENT", "ACCENT_PRESSED", "TEXT_ON_ACCENT"),
            "success": ("GREEN", "GREEN_PRESSED", "TEXT_ON_ACCENT"),
            "danger": ("TINT_RED", "TINT_RED", "RED"),
            "secondary": ("SURFACE", "TINT_NEUTRAL_A", "TEXT_PRIMARY"),
            "quiet": ("SURFACE", "TINT_ACCENT", "TEXT_MUTED"),
        }
        if variant not in variants:
            raise ValueError(f"Unknown button variant: {variant}")
        base, hover, text = variants[variant]
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS[base],
            "hover_color": cls.COLORS[hover],
            "text_color": cls.COLORS[text],
            "font": cls.FONTS["BUTTON"],
            "border_width": cls.BORDER_WIDTH if variant == "secondary" else 0,
            "border_color": cls.COLORS["BORDER"],
        }

    @classmethod
    def textbox_kwargs(cls) -> dict:
        """Style an editor or output area with shared monospace typography.

        Args:
            None.
        Returns:
            CTkTextbox constructor arguments.
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
    def option_menu_kwargs(cls) -> dict:
        """Style a neutral selector so primary actions retain visual emphasis.

        Args:
            None.
        Returns:
            CTkOptionMenu constructor arguments.
        """
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS["TINT_NEUTRAL_A"],
            "button_color": cls.COLORS["TINT_NEUTRAL_A"],
            "button_hover_color": cls.COLORS["TINT_NEUTRAL_B"],
            "dropdown_fg_color": cls.COLORS["SURFACE"],
            "dropdown_text_color": cls.COLORS["TEXT_PRIMARY"],
            "dropdown_hover_color": cls.COLORS["TINT_ACCENT"],
            "text_color": cls.COLORS["TEXT_PRIMARY"],
            "font": cls.FONTS["BODY"],
        }

    @classmethod
    def switch_kwargs(cls) -> dict:
        """Style the appearance switch with the shared green accent.

        Args:
            None.
        Returns:
            CTkSwitch constructor arguments.
        """
        return {
            "corner_radius": cls.CORNER_RADIUS,
            "fg_color": cls.COLORS["TINT_NEUTRAL_B"],
            "progress_color": cls.COLORS["ACCENT"],
            "button_color": cls.COLORS["WHITE"],
            "button_hover_color": cls.COLORS["TINT_NEUTRAL_A"],
            "text_color": cls.COLORS["TEXT_PRIMARY"],
            "font": cls.FONTS["LABEL"],
        }

    @classmethod
    def label_kwargs(cls, style: str = "body") -> dict:
        """Select a named typography level.

        Args:
            style: A lowercase key from FONTS (e.g. display, h1, body, label).
        Returns:
            CTkLabel constructor arguments.
        Raises:
            ValueError: The style does not name a font tuple.
        """
        font = cls.FONTS.get(style.upper())
        if not isinstance(font, tuple):
            raise ValueError(f"Unknown text style: {style}")
        return {"font": font, "text_color": cls.COLORS["TEXT_PRIMARY"]}

    @classmethod
    def accent_bar(cls, parent):
        """Build the four shades of green for the terminal-inspired brand mark.

        Args:
            parent: Widget containing the mark.
        Returns:
            A small frame ready for grid/pack placement.
        """
        bar = ctk.CTkFrame(
            parent, fg_color="transparent", corner_radius=cls.SHELL_RADIUS
        )
        for index, color in enumerate(
            ("BRAND_GREEN_1", "BRAND_GREEN_2", "BRAND_GREEN_3", "BRAND_GREEN_4")
        ):
            ctk.CTkFrame(
                bar,
                width=18,
                height=4,
                fg_color=cls.COLORS[color],
                corner_radius=cls.SHELL_RADIUS,
            ).grid(row=0, column=index, padx=(0, 3))
        return bar
