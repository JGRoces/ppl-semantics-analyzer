"""Own one native window and swap welcome/workspace content inside it.

Keeping the same Tk root preserves the native window, position, focus context,
and event loop. The entry page remains visible while the workspace is built;
only its child widgets are replaced when the workspace is ready.
"""

import customtkinter as ctk

from ui.launcher_window import LauncherWindow
from ui.main_window import MainWindow
from ui.ui_assets import UIAssets


class Application(ctk.CTk):
    """Persistent window hosting the entry page and diagnostics workspace."""

    def __init__(self) -> None:
        """Create the native window once and mount the entry page.

        Args:
            None.
        Returns:
            None.
        """
        super().__init__()
        UIAssets.apply_theme()
        self.title("Paradigm Diagnostics")
        UIAssets.center_window(
            self,
            min(1280, self.winfo_screenwidth() - 40),
            min(860, self.winfo_screenheight() - 80),
        )
        self.minsize(1180, 760)
        self.configure(fg_color=UIAssets.COLORS["BG_PRIMARY"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.workspace = None
        self.launcher = LauncherWindow(self, self.open_workspace, self._close)
        self.launcher.grid(row=0, column=0, sticky="nsew")
        self.protocol("WM_DELETE_WINDOW", self._close)

    def open_workspace(self, languages: tuple, dark_mode: bool, clean_start: bool = False) -> None:
        """Replace entry content while preserving the native window and geometry.

        Args:
            languages: The two selected language display labels.
            dark_mode: The current appearance choice, carried into the workspace.
            clean_start: Open empty editors instead of the initial lesson.
        Returns:
            None. Repeated callbacks do not create duplicate workspaces.
        """
        if self.workspace is not None:
            return
        UIAssets.set_dark_mode(dark_mode)
        self.workspace = MainWindow(self, *languages, dark_mode=dark_mode, clean_start=clean_start)
        self.workspace.grid(row=0, column=0, sticky="nsew")
        self.workspace.tkraise()
        self.launcher.destroy()
        self.launcher = None
        self.workspace.editors[0].focus_set()

    def back_to_menu(self) -> None:
        """Dispose of the workspace and show a fresh language selection page.

        Args:
            None.
        Returns:
            None; the native application window stays open.
        """
        if self.workspace is None:
            return
        dark_mode = bool(self.workspace.appearance_switch.get())
        self.workspace.destroy()
        self.workspace = None
        self.launcher = LauncherWindow(self, self.open_workspace, self._close)
        self.launcher.appearance_switch_var.set("dark" if dark_mode else "light")
        self.launcher.dark_mode = dark_mode
        self.launcher.grid(row=0, column=0, sticky="nsew")
        self.launcher.tkraise()

    def _close(self) -> None:
        """Close the native window, allowing active diagnostics to clean up.

        Args:
            None.
        Returns:
            None.
        """
        if self.workspace is not None:
            self.workspace._close()
        else:
            self.destroy()
