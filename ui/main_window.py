"""Car Rental-inspired dashboard shell around the existing PPL workflow.

A neutral top bar, collapsible navigation, and persistent content pages replace
fixed grid divisions. The worker, comparison service, editors, and reports keep
their existing behavior; changing pages never destroys or reloads source.
"""

import json
import os
import queue
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.comparison import compare_snippets, render_report, render_view
from core.examples import LANGUAGE_LABELS, LESSONS
from core.execution_runner import runtime_paths
from ui.line_numbers import LineNumberGutter
from ui.lesson_resources import LESSON_RESOURCES
from ui.ui_assets import UIAssets
from ui.syntax_highlighting import SyntaxHighlighter


class MainWindow(ctk.CTkFrame):
    """Present a comparison workbench, lesson library, and reports."""

    HEADER_TABS = ["Static AST", "Runtime", "PPL Verdict"]
    PAGE_TITLES = {
        "workspace": "Workspace",
        "lessons": "Demonstrations",
        "reports": "Reports",
    }

    def __init__(
        self,
        master,
        language_a: str = "Python",
        language_b: str = "JavaScript",
        dark_mode: bool = False,
        clean_start: bool = False,
    ) -> None:
        """Create the themed shell and load the initial recursion lesson.

        Args:
            master: The existing application window; no second Tk root is created.
            language_a: First language selected in the launcher.
            language_b: Second language selected in the launcher.
            dark_mode: Appearance carried over from the launcher.
            clean_start: Start with empty source and results instead of a lesson.
        Returns:
            None.
        """
        super().__init__(
            master,
            fg_color=UIAssets.COLORS["BG_PRIMARY"],
            corner_radius=UIAssets.SHELL_RADIUS,
        )
        self.report = None
        self.busy = False
        self.active_view = "Static AST"
        self.active_page = "workspace"
        self.sidebar_expanded = True
        self.messages = queue.Queue()
        self.cancel_event = threading.Event()
        self.poll_id = None
        self.run_bindings = []
        self.lesson_stdin = ""
        self.controls = []
        self.editors = []
        self.highlighters = []
        self.line_gutters = []
        self.language_menus = []
        self.results = []
        self.pages = {}
        self.nav_buttons = {}
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header(dark_mode)
        self._build_sidebar()
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=1, column=1, sticky="nsew", padx=20, pady=(18, 12))
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        self._build_workspace(language_a, language_b)
        self._build_library()
        self._build_reports()
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            font=UIAssets.FONTS["LABEL"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        )
        self.status_label.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 8)
        )
        self.run_bindings = [
            (sequence, master.bind(sequence, lambda event: self._start(True), add="+"))
            for sequence in ("<Control-Return>", "<Command-Return>")
        ]
        if clean_start:
            self._clear_workspace()
        else:
            self._load_lesson()
        self._show_page("workspace")

    def _build_header(self, dark_mode: bool) -> None:
        """Build a continuous surface top bar with group identity and actions.

        Args:
            dark_mode: Initial switch state.
        Returns:
            None.
        """
        header = ctk.CTkFrame(
            self,
            height=68,
            fg_color=UIAssets.COLORS["SURFACE"],
            corner_radius=UIAssets.SHELL_RADIUS,
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(2, weight=1)
        identity = ctk.CTkFrame(header, fg_color="transparent")
        identity.grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=12)
        self.brand_title = ctk.CTkLabel(
            identity, text="Paradigm Diagnostics", **UIAssets.label_kwargs("h1")
        )
        self.brand_title.pack(anchor="w")
        self.brand_subtitle = ctk.CTkLabel(
            identity,
            text="Principles of Programming Languages",
            font=UIAssets.FONTS["BODY"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        )
        self.brand_subtitle.pack(anchor="w")
        self.page_label = ctk.CTkLabel(
            header, text="Workspace", **UIAssets.label_kwargs("h2")
        )
        self.page_label.grid(row=0, column=2, sticky="e", padx=24)
        self.export_button = ctk.CTkButton(
            header,
            text="Export report",
            width=120,
            height=34,
            command=self._export,
            **UIAssets.button_kwargs("secondary"),
        )
        self.export_button.grid(row=0, column=3, padx=(0, 22))
        self.export_button.configure(state="disabled")
        self.appearance_switch = ctk.CTkSwitch(
            header,
            text="Dark mode",
            command=self._toggle_appearance,
            **UIAssets.switch_kwargs(),
        )
        self.appearance_switch.grid(row=0, column=4, padx=(0, 22))
        if dark_mode:
            self.appearance_switch.select()

    def _toggle_appearance(self) -> None:
        """Change appearance across every page and line-number gutter.

        Args:
            None.
        Returns:
            None.
        """
        root = self.winfo_toplevel()
        focused = root.focus_get()
        # CTk schedules a Windows title-bar focus restore; keep its target alive
        # even if the user immediately navigates away from this workspace.
        root.focus_set()
        UIAssets.set_dark_mode(bool(self.appearance_switch.get()))
        if focused is not None:
            root.after(2, lambda: focused.focus_set() if focused.winfo_exists() else None)
        for highlighter in self.highlighters:
            highlighter.refresh_palette()

    def _build_sidebar(self) -> None:
        """Create persistent, collapsible navigation with active green states.

        Args:
            None.
        Returns:
            None.
        """
        self.sidebar = ctk.CTkFrame(
            self,
            width=UIAssets.SIDEBAR_WIDTH,
            fg_color=UIAssets.COLORS["SURFACE"],
            corner_radius=UIAssets.SHELL_RADIUS,
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", pady=(1, 0))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(6, weight=1)
        self.sidebar_brand = ctk.CTkLabel(
            self.sidebar, text="DIAGNOSTICS", **UIAssets.label_kwargs("label")
        )
        self.sidebar_brand.grid(row=0, column=0, sticky="w", padx=20, pady=(22, 12))
        self.sidebar_toggle = ctk.CTkButton(
            self.sidebar,
            text="‹   Collapse sidebar",
            height=32,
            width=40,
            command=self._toggle_sidebar,
            **UIAssets.button_kwargs("quiet"),
        )
        self.sidebar_toggle.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 16))
        for row, (page, short) in enumerate(
            (("workspace", "W"), ("lessons", "D"), ("reports", "R")), start=2
        ):
            button = ctk.CTkButton(
                self.sidebar,
                text=f"{short}    {self.PAGE_TITLES[page]}",
                anchor="w",
                height=42,
                width=40,
                command=lambda target=page: self._show_page(target),
                **UIAssets.button_kwargs("quiet"),
            )
            button.grid(row=row, column=0, sticky="ew", padx=12, pady=3)
            self.nav_buttons[page] = (button, short)
        self.runtime_label = ctk.CTkLabel(
            self.sidebar,
            text="LOCAL TOOLCHAINS\n\n"
            + "\n".join(
                f"{label}: {'detected' if runtime_paths()[language] else 'missing'}"
                for label, language in LANGUAGE_LABELS.items()
            ),
            justify="left",
            anchor="w",
            font=UIAssets.FONTS["LABEL"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        )
        self.runtime_label.grid(row=7, column=0, sticky="w", padx=20, pady=18)
        self.back_button = ctk.CTkButton(
            self.sidebar,
            text="Back to Menu",
            anchor="w",
            height=42,
            width=40,
            command=self.master.back_to_menu,
            **UIAssets.button_kwargs("quiet"),
        )
        self.back_button.grid(row=8, column=0, sticky="ew", padx=12, pady=(0, 20))

    def _toggle_sidebar(self) -> None:
        """Collapse navigation without recreating pages or losing editor state.

        Args:
            None.
        Returns:
            None.
        """
        self.sidebar_expanded = not self.sidebar_expanded
        self.sidebar.configure(
            width=(
                UIAssets.SIDEBAR_WIDTH
                if self.sidebar_expanded
                else UIAssets.SIDEBAR_COLLAPSED
            )
        )
        self.sidebar_toggle.configure(
            text="‹   Collapse sidebar" if self.sidebar_expanded else "›"
        )
        self.sidebar_brand.configure(
            text="DIAGNOSTICS" if self.sidebar_expanded else "PPL"
        )
        self.sidebar_brand.grid_configure(padx=20 if self.sidebar_expanded else 16)
        self.back_button.configure(
            text="Back to Menu" if self.sidebar_expanded else "←",
            anchor="w" if self.sidebar_expanded else "center",
        )
        if self.sidebar_expanded:
            self.runtime_label.grid()
        else:
            self.runtime_label.grid_remove()
        for page, (button, short) in self.nav_buttons.items():
            button.configure(
                text=(
                    f"{short}    {self.PAGE_TITLES[page]}"
                    if self.sidebar_expanded
                    else short
                ),
                anchor="w" if self.sidebar_expanded else "center",
            )

    def _show_page(self, page: str) -> None:
        """Raise a persistent content page and update the active navigation.

        Args:
            page: Key in PAGE_TITLES.
        Returns:
            None.
        """
        self.active_page = page
        for key, frame in self.pages.items():
            if key == page:
                frame.grid()
            else:
                frame.grid_remove()
        self.page_label.configure(text=self.PAGE_TITLES[page])
        for key, (button, _) in self.nav_buttons.items():
            active = key == page
            button.configure(
                fg_color=UIAssets.COLORS["ACCENT" if active else "SURFACE"],
                hover_color=UIAssets.COLORS[
                    "ACCENT_PRESSED" if active else "TINT_ACCENT"
                ],
                text_color=UIAssets.COLORS[
                    "TEXT_ON_ACCENT" if active else "TEXT_MUTED"
                ],
            )
        if page == "reports":
            self._refresh_report_page()

    def _new_page(self, key: str):
        """Allocate a page in the common content area.

        Args:
            key: Navigation key identifying the page.
        Returns:
            A page frame that is retained when another page is shown.
        """
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        self.pages[key] = page
        return page

    def _heading(self, parent, title: str, subtitle: str):
        """Add a page title and a short explanatory subtitle.

        Args:
            parent: Page frame with an unused row zero.
            title: Page title.
            subtitle: Supporting description.
        Returns:
            Heading frame, allowing page-specific actions.
        """
        heading = ctk.CTkFrame(parent, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        heading.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(heading, text=title, **UIAssets.label_kwargs("h1")).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            heading,
            text=subtitle,
            font=UIAssets.FONTS["BODY"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        return heading

    def _build_workspace(self, language_a: str, language_b: str) -> None:
        """Compose the controls, two editors, and expanded result card.

        Args:
            language_a: First editor's initial language label.
            language_b: Second editor's initial language label.
        Returns:
            None.
        """
        self.workspace = self._new_page("workspace")
        self.workspace.grid_rowconfigure(2, weight=3)
        self.workspace.grid_rowconfigure(3, weight=2)
        heading = self._heading(
            self.workspace,
            "Comparison workspace",
            "One idea, two implementations. Inspect the source and compare what happens.",
        )
        self.clear_workspace_button = ctk.CTkButton(
            heading, text="Clear workspace", width=135, height=32,
            command=self._clear_workspace, **UIAssets.button_kwargs("secondary"),
        )
        self.clear_workspace_button.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))
        self.controls.append(self.clear_workspace_button)
        self._build_tools()
        editor_row = ctk.CTkFrame(self.workspace, fg_color="transparent")
        editor_row.grid(row=2, column=0, sticky="nsew", pady=12)
        editor_row.grid_columnconfigure((0, 1), weight=1, uniform="editors")
        editor_row.grid_rowconfigure(0, weight=1)
        self._build_editor(editor_row, "A", 0, language_a)
        self._build_editor(editor_row, "B", 1, language_b)
        self._build_results()

    def _build_tools(self) -> None:
        """Provide compact lesson, timeout, and execution controls in one card.

        Args:
            None.
        Returns:
            None.
        """
        bar = ctk.CTkFrame(self.workspace, **UIAssets.frame_kwargs())
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_columnconfigure(2, weight=1)
        self.lesson_menu = ctk.CTkOptionMenu(
            bar, values=list(LESSONS), width=180, **UIAssets.option_menu_kwargs()
        )
        self.lesson_menu.grid(row=0, column=0, padx=(12, 8), pady=10)
        self.controls.append(self.lesson_menu)
        self.load_button = self._action(
            bar, "Load lesson", self._load_lesson, 1, "secondary", 100
        )
        timeout = ctk.CTkFrame(bar, fg_color="transparent")
        timeout.grid(row=0, column=2, padx=8, sticky="w")
        ctk.CTkLabel(timeout, text="Limit (s)", **UIAssets.label_kwargs("label")).pack(
            side="left", padx=(0, 6)
        )
        self.timeout_menu = ctk.CTkOptionMenu(
            timeout,
            values=["1", "2", "5", "10"],
            width=58,
            command=self._edited,
            **UIAssets.option_menu_kwargs(),
        )
        self.timeout_menu.set("5")
        self.timeout_menu.pack(side="left")
        self.controls.append(self.timeout_menu)
        self.analyze_button = self._action(
            bar, "Analyze only", lambda: self._start(False), 3, "secondary", 108
        )
        self.run_button = self._action(
            bar, "Run comparison", lambda: self._start(True), 4, "primary", 138
        )
        self.stop_button = self._action(
            bar, "Stop", self._stop, 5, "danger", 58, managed=False
        )
        self.stop_button.configure(state="disabled")

    def _action(
        self,
        parent,
        text: str,
        command,
        column: int,
        variant: str,
        width: int,
        managed: bool = True,
    ):
        """Create a toolbar action and register execution-disabled controls.

        Args:
            parent: Toolbar container.
            text: Action label.
            command: Click callback.
            column: Grid column.
            variant: Shared button style.
            width: Requested button width.
            managed: Disable this action while a worker is active.
        Returns:
            The new button.
        """
        button = ctk.CTkButton(
            parent,
            text=text,
            width=width,
            height=32,
            command=command,
            **UIAssets.button_kwargs(variant),
        )
        button.grid(row=0, column=column, padx=(0, 8), pady=10)
        if managed:
            self.controls.append(button)
        return button

    def _build_editor(self, parent, label: str, column: int, language: str) -> None:
        """Build one source card with language selector and existing gutter.

        Args:
            parent: Two-column editor container.
            label: A or B.
            column: Column in the editor container.
            language: Initial display label.
        Returns:
            None.
        """
        panel = ctk.CTkFrame(parent, **UIAssets.frame_kwargs())
        panel.grid(
            row=0, column=column, sticky="nsew", padx=(0, 6) if column == 0 else (6, 0)
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        toolbar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            toolbar, text=f"Snippet {label}", **UIAssets.label_kwargs("h3")
        ).grid(row=0, column=0, padx=(0, 12))
        menu = ctk.CTkOptionMenu(
            toolbar,
            values=list(LANGUAGE_LABELS),
            width=120,
            command=self._edited,
            **UIAssets.option_menu_kwargs(),
        )
        menu.set(language if language in LANGUAGE_LABELS else "Python")
        menu.grid(row=0, column=1, sticky="w")
        index = len(self.editors)
        open_button = ctk.CTkButton(
            toolbar,
            text="Open…",
            width=64,
            command=lambda: self._open_source(index),
            **UIAssets.button_kwargs("quiet"),
        )
        open_button.grid(row=0, column=2, padx=(6, 0))
        editor_area = ctk.CTkFrame(panel, **UIAssets.frame_kwargs(border=False))
        editor_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        editor_area.grid_columnconfigure(1, weight=1)
        editor_area.grid_rowconfigure(0, weight=1)
        editor = ctk.CTkTextbox(
            editor_area, wrap="none", height=140, undo=True, **UIAssets.textbox_kwargs()
        )
        editor.configure(border_width=0)
        editor.grid(row=0, column=1, sticky="nsew")
        gutter = LineNumberGutter(editor_area, editor)
        gutter.grid(row=0, column=0, sticky="ns")
        editor.bind("<<Modified>>", lambda event: self._text_modified(editor))
        self.editors.append(editor)
        self.highlighters.append(SyntaxHighlighter(editor, menu.get))
        self.line_gutters.append(gutter)
        self.language_menus.append(menu)
        self.controls.extend([editor, menu, open_button])

    def _build_results(self) -> None:
        """Place view tabs and two output columns inside one result card.

        Args:
            None.
        Returns:
            None.
        """
        card = ctk.CTkFrame(self.workspace, **UIAssets.frame_kwargs())
        card.grid(row=3, column=0, rowspan=1, sticky="nsew")
        card.grid_columnconfigure((0, 1), weight=1, uniform="results")
        card.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 4))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Results & insights", **UIAssets.label_kwargs("h2")
        ).grid(row=0, column=0, sticky="w")
        # Separate buttons allow white selected text and dark inactive text in
        # light mode; a single shared text color would lose contrast on the selected accent.
        self.tab_strip = ctk.CTkFrame(header, fg_color="transparent")
        self.tab_strip.grid(row=0, column=1)
        self.clear_results_button = ctk.CTkButton(
            header, text="Clear results", width=105, height=28,
            command=self._clear_results, **UIAssets.button_kwargs("secondary"),
        )
        self.clear_results_button.grid(row=0, column=2, padx=(12, 0))
        self.controls.append(self.clear_results_button)
        self.view_buttons = {}
        for index, view in enumerate(self.HEADER_TABS):
            button = ctk.CTkButton(
                self.tab_strip,
                text=view,
                width=105,
                height=28,
                command=lambda selected=view: self._change_view(selected),
                **UIAssets.button_kwargs("quiet"),
            )
            button.grid(row=0, column=index, padx=(4, 0))
            self.view_buttons[view] = button
        self._change_view(self.active_view)
        self.summary_label = ctk.CTkLabel(
            card,
            text="",
            anchor="w",
            font=UIAssets.FONTS["LABEL"],
            text_color=UIAssets.COLORS["TEXT_MUTED"],
        )
        self.summary_label.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 6)
        )
        for index in range(2):
            textbox = ctk.CTkTextbox(
                card, height=118, wrap="word", **UIAssets.textbox_kwargs()
            )
            textbox.configure(border_width=0)
            textbox.grid(row=2, column=index, sticky="nsew", padx=10, pady=(0, 10))
            self.results.append(textbox)

    def _build_library(self) -> None:
        """Build role-card-inspired lesson choices with actual load actions.

        Args:
            None.
        Returns:
            None.
        """
        page = self._new_page("lessons")
        self._heading(
            page,
            "Demonstrations",
            "Choose a concept. Load its examples into your selected languages.",
        )
        page.grid_rowconfigure(1, weight=1)
        library = ctk.CTkScrollableFrame(page, fg_color="transparent")
        library.grid(row=1, column=0, sticky="nsew")
        library.grid_columnconfigure((0, 1), weight=1, uniform="lessons")
        self.lesson_cards = {}
        self.lesson_view_buttons = {}
        self.lesson_descriptions = {}
        for index, name in enumerate(LESSONS):
            card = ctk.CTkFrame(library, **UIAssets.frame_kwargs())
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(2, weight=1)
            ctk.CTkLabel(
                card,
                text=f"{index + 1:02}",
                width=36,
                height=32,
                corner_radius=UIAssets.CORNER_RADIUS,
                fg_color=UIAssets.COLORS["TINT_GREEN"],
                font=UIAssets.FONTS["H3"],
                text_color=UIAssets.COLORS["TEXT_PRIMARY"],
            ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))
            ctk.CTkLabel(card, text=name, **UIAssets.label_kwargs("h2")).grid(
                row=1, column=0, sticky="w", padx=18
            )
            description = ctk.CTkLabel(
                card,
                text=LESSON_RESOURCES[name]["summary"],
                width=1,
                wraplength=340,
                justify="left",
                anchor="nw",
                font=UIAssets.FONTS["BODY"],
                text_color=UIAssets.COLORS["TEXT_MUTED"],
            )
            description.grid(row=2, column=0, sticky="nsew", padx=18, pady=(6, 14))
            description.bind(
                "<Configure>",
                lambda event, label=description: self._resize_lesson_description(label),
            )
            self.lesson_descriptions[name] = description
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
            actions.grid_columnconfigure((0, 1), weight=1, uniform="lesson_actions")
            button = ctk.CTkButton(
                actions,
                text="Load demonstration",
                width=150,
                height=34,
                command=lambda selected=name: self._select_lesson(selected),
                **UIAssets.button_kwargs("secondary"),
            )
            button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
            view_button = ctk.CTkButton(
                actions,
                text="View Lesson",
                width=100,
                height=34,
                command=lambda selected=name: self._view_lesson(selected),
                **UIAssets.button_kwargs("secondary"),
            )
            view_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))
            self.controls.append(button)
            self.lesson_cards[name] = button
            self.lesson_view_buttons[name] = view_button

    @staticmethod
    def _resize_lesson_description(label: ctk.CTkLabel) -> None:
        """Wrap the summary to its available width in logical display pixels."""
        width = max(1, int(label.winfo_width() / label._get_widget_scaling()))
        if label.cget("wraplength") != width:
            label.configure(wraplength=width)

    def _view_lesson(self, name: str) -> None:
        """Open the selected local PDF with the platform's document handler.

        Args:
            name: Key in LESSON_RESOURCES.
        Returns:
            None; missing files and launch failures show a recoverable dialog.
        """
        path = (
            Path(__file__).resolve().parent.parent
            / "docs" / "lessons" / LESSON_RESOURCES[name]["pdf"]
        )
        if not path.is_file():
            messagebox.showerror(
                "Lesson PDF not found", f"Missing lesson file:\n{path}", parent=self
            )
            return
        try:
            if os.name == "nt":
                os.startfile(str(path))
            elif not webbrowser.open(path.as_uri()):
                raise OSError("No application could open the PDF.")
        except (OSError, webbrowser.Error) as exc:
            messagebox.showerror("Could not open lesson", str(exc), parent=self)

    def _select_lesson(self, name: str) -> None:
        """Load a library choice into the workspace without executing it.

        Args:
            name: Key in LESSONS.
        Returns:
            None.
        """
        if self.busy:
            return
        self.lesson_menu.set(name)
        self._load_lesson()
        self._show_page("workspace")

    def _build_reports(self) -> None:
        """Create the current-snapshot report page with an honest empty state.

        Args:
            None.
        Returns:
            None.
        """
        page = self._new_page("reports")
        self._heading(
            page,
            "Comparison report",
            "Review the latest source and input snapshot. Export it as Markdown or JSON.",
        )
        page.grid_rowconfigure(1, weight=1)
        self.report_preview = ctk.CTkTextbox(
            page, wrap="word", **UIAssets.textbox_kwargs()
        )
        self.report_preview.grid(row=1, column=0, sticky="nsew")
        self._refresh_report_page()

    def _refresh_report_page(self) -> None:
        """Show the current report or explain why no current evidence exists.

        Args:
            None.
        Returns:
            None.
        """
        if not hasattr(self, "report_preview"):
            return
        if self.busy:
            text = "A comparison is in progress. Its report will appear when processing finishes."
        elif self.report is None:
            text = "No comparison report yet.\n\nOpen Workspace and choose Analyze only or Run comparison.\n\nEditing source or input clears the previous report to keep the evidence current."
        else:
            text = render_report(self.report)
        self._set_text(self.report_preview, text, readonly=True)

    @staticmethod
    def _set_text(widget, text: str, readonly: bool = False) -> None:
        """Replace a textbox's contents, optionally making it read only.

        Args:
            widget: CTkTextbox to update on the GUI thread.
            text: Replacement contents.
            readonly: Disable editing after inserting.
        Returns:
            None.
        """
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.edit_modified(False)
        if readonly:
            widget.configure(state="disabled")

    def _load_lesson(self) -> None:
        """Load corresponding sources for both selected languages and stdin.

        Args:
            None.
        Returns:
            None.
        """
        if self.busy:
            return
        lesson = LESSONS[self.lesson_menu.get()]
        for editor, menu in zip(self.editors, self.language_menus):
            self._set_text(editor, lesson["sources"][LANGUAGE_LABELS[menu.get()]])
        self.lesson_stdin = lesson["stdin"]
        self._edited()
        self.status_label.configure(
            text=f"Loaded {self.lesson_menu.get()}. Edit either snippet, analyze, or run. Ctrl/⌘ + Enter runs both."
        )

    def _text_modified(self, widget) -> None:
        """Invalidate results after typing, paste, cut, undo, or redo.

        Args:
            widget: The source/input textbox whose modified flag changed.
        Returns:
            None. Resetting the flag generates another event, which is ignored.
        """
        if widget.edit_modified():
            widget.edit_modified(False)
            self._edited()

    def _edited(self, event=None) -> None:
        """Clear previous results so edited code cannot inherit stale evidence.

        Args:
            event: Optional Tk event or selector value, unused.
        Returns:
            None.
        """
        for highlighter in self.highlighters:
            highlighter.request()
        if self.busy:
            return
        self.report = None
        self._refresh_report_page()
        self.export_button.configure(state="disabled")
        self.summary_label.configure(
            text="Source/input changed — analyze or run to refresh results."
        )
        for textbox in self.results:
            self._set_text(
                textbox,
                "Results cleared. Analyze or run the current source and input.",
                readonly=True,
            )

    def _clear_results(self) -> None:
        """Clear diagnostics and export state, preserving source and settings."""
        if self.busy:
            return
        self.report = None
        self.export_button.configure(state="disabled")
        self._refresh_report_page()
        for textbox in self.results:
            self._set_text(textbox, "", readonly=True)
        self.summary_label.configure(text="Ready to analyze or run.")
        self.status_label.configure(text="Results cleared. Your source is unchanged.")

    def _clear_workspace(self) -> None:
        """Empty both editors and preset input; keep languages and appearance."""
        if self.busy:
            return
        for editor, highlighter in zip(self.editors, self.highlighters):
            self._set_text(editor, "")
            highlighter.request()
        self.lesson_stdin = ""
        self._clear_results()
        self._change_view("Static AST")
        self.status_label.configure(text="Empty workspace. Type code, open a file, or load a lesson.")
        self.highlighters[0].text.focus_set()

    def _start(self, run: bool) -> None:
        """Snapshot widgets and launch a single background comparison worker.

        Args:
            run: Execute the snippets after analysis when True.
        Returns:
            None.
        """
        if self.busy:
            return
        sources = [editor.get("1.0", "end-1c") for editor in self.editors]
        if any(len(source) > 100_000 for source in sources):
            messagebox.showerror(
                "Source too large",
                "Use snippets of at most 100,000 characters.",
                parent=self,
            )
            return
        languages = [LANGUAGE_LABELS[menu.get()] for menu in self.language_menus]
        stdin = self.lesson_stdin
        timeout = float(self.timeout_menu.get())
        self.busy = True
        self._refresh_report_page()
        self.cancel_event.clear()
        for control in self.controls:
            control.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.export_button.configure(state="disabled")
        self.summary_label.configure(
            text="Running comparison…" if run else "Analyzing source…"
        )
        self.status_label.configure(
            text="Working — C++ compilation has a separate budget. Stop cancels the current run."
        )
        for textbox in self.results:
            self._set_text(textbox, "Processing current snapshot…", readonly=True)
        # Keep the worker alive briefly after window close so its cancellation
        # handler can reap the child process before Python exits.
        threading.Thread(
            target=self._work,
            args=(sources, languages, stdin, timeout, run),
            daemon=False,
        ).start()
        self.poll_id = self.after(50, self._poll)

    def _work(
        self, sources: list, languages: list, stdin: str, timeout: float, run: bool
    ) -> None:
        """Compute a report without accessing any Tk objects.

        Args:
            sources: The two editor snapshots.
            languages: Corresponding normalized IDs.
            stdin: Shared input snapshot.
            timeout: Execution budget.
            run: Whether to launch processes.
        Returns:
            None; success or error is sent through the thread-safe queue.
        """
        try:
            report = compare_snippets(
                sources[0],
                languages[0],
                sources[1],
                languages[1],
                stdin,
                timeout,
                run,
                self.cancel_event,
            )
            self.messages.put((report, None))
        except Exception as exc:
            # The UI boundary must restore controls even after unexpected
            # parser/tool failures. The visible message retains the error type.
            self.messages.put((None, f"{type(exc).__name__}: {exc}"))

    def _poll(self) -> None:
        """Deliver worker results on the main thread and restore controls.

        Args:
            None.
        Returns:
            None.
        """
        self.poll_id = None
        try:
            report, error = self.messages.get_nowait()
        except queue.Empty:
            self.poll_id = self.after(50, self._poll)
            return
        self.busy = False
        for control in self.controls:
            control.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.report = report
        self._refresh_report_page()
        if error:
            self.summary_label.configure(
                text="Comparison failed — see diagnostic below."
            )
            for textbox in self.results:
                self._set_text(textbox, error, readonly=True)
            self.status_label.configure(
                text="Ready to retry after correcting the source or environment."
            )
            return
        self.export_button.configure(state="normal")
        states = [
            item["execution"]["status"] if item["execution"] else "analyzed"
            for item in report["snippets"]
        ]
        self.summary_label.configure(
            text=f"A: {states[0]}    |    B: {states[1]}    |    Open PPL Verdict for the comparison."
        )
        self.status_label.configure(
            text="Comparison complete. Results and exports describe this source/input snapshot."
        )
        self._change_view(self.active_view)

    def _change_view(self, view: str) -> None:
        """Render the chosen view from the most recent report snapshot.

        Args:
            view: One of the header tab labels.
        Returns:
            None.
        """
        self.active_view = view
        for key, button in self.view_buttons.items():
            active = key == view
            button.configure(
                fg_color=UIAssets.COLORS["ACCENT" if active else "TINT_NEUTRAL_A"],
                hover_color=UIAssets.COLORS[
                    "ACCENT_PRESSED" if active else "TINT_NEUTRAL_B"
                ],
                text_color=UIAssets.COLORS[
                    "TEXT_ON_ACCENT" if active else "TEXT_PRIMARY"
                ],
            )
        if self.report and not self.busy:
            for index, textbox in enumerate(self.results):
                self._set_text(
                    textbox, render_view(self.report, index, view), readonly=True
                )

    def _stop(self) -> None:
        """Signal the worker to stop its process and skip further execution.

        Args:
            None.
        Returns:
            None.
        """
        self.cancel_event.set()
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Stopping… waiting for process cleanup.")

    def _open_source(self, index: int) -> None:
        """Load a UTF-8 source file into one editor, inferring its language.

        Args:
            index: Destination editor index.
        Returns:
            None. File errors are shown as recoverable dialogs.
        """
        path = filedialog.askopenfilename(
            parent=self,
            title=f"Open snippet {'AB'[index]}",
            filetypes=[
                ("Source files", "*.py *.js *.cpp *.cc *.cxx"),
                ("All files", "*"),
            ],
        )
        if not path:
            return
        try:
            source_path = Path(path)
            if source_path.stat().st_size > 400_000:
                raise ValueError("Choose a source file smaller than 400 KB.")
            text = source_path.read_text(encoding="utf-8")
            if len(text) > 100_000:
                raise ValueError("Use at most 100,000 source characters.")
            self._set_text(self.editors[index], text)
            language = {
                ".py": "Python",
                ".js": "JavaScript",
                ".cpp": "C++",
                ".cc": "C++",
                ".cxx": "C++",
            }.get(source_path.suffix.lower())
            if language:
                self.language_menus[index].set(language)
            self._edited()
        except (OSError, UnicodeError, ValueError) as exc:
            messagebox.showerror("Could not open source", str(exc), parent=self)

    def _export(self) -> None:
        """Save a complete report, including original inputs, as Markdown/JSON.

        Args:
            None.
        Returns:
            None. Cancelling the file dialog leaves the report unchanged.
        """
        if self.report is None or self.busy:
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export comparison report",
            defaultextension=".md",
            initialfile="ppl-comparison.md",
            filetypes=[("Markdown", "*.md"), ("JSON", "*.json")],
        )
        if not path:
            return
        try:
            text = (
                json.dumps(self.report, indent=2, ensure_ascii=False) + "\n"
                if Path(path).suffix.lower() == ".json"
                else render_report(self.report)
            )
            Path(path).write_text(text, encoding="utf-8")
            self.status_label.configure(text=f"Report saved: {path}")
        except OSError as exc:
            messagebox.showerror("Could not save report", str(exc), parent=self)

    def destroy(self) -> None:
        """Cancel workspace work and detach callbacks before removing widgets.

        Args:
            None.
        Returns:
            None; workers finish cancellation without accessing Tk widgets.
        """
        self.cancel_event.set()
        for highlighter in self.highlighters:
            highlighter.close()
        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
            self.poll_id = None
        for sequence, binding in self.run_bindings:
            self.master.unbind(sequence, binding)
        super().destroy()

    def _close(self) -> None:
        """Cancel active work and remove Tk polling before closing the window.

        Args:
            None.
        Returns:
            None.
        """
        self.winfo_toplevel().destroy()
