"""Interactive Group 4 dashboard using the team's original eight-panel grid.

The root still uses the original 10x10 coordinates: header (0,0,2,10),
analytics title (2,1,1,9), sidebar (2,0,7,1), tools (3,1,6,2), editors
(3,3,4,3)/(3,6,4,3), results (7,3,2,6), footer (9,0,1,10).

Only the main thread touches Tk widgets. A worker receives immutable text
snapshots and returns a report through a Queue; after() polls that queue.
"""

import json
import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.comparison import compare_snippets, render_report, render_view
from core.examples import LANGUAGE_LABELS, LESSONS
from core.execution_runner import runtime_paths
from ui.ui_assets import UIAssets


class MainWindow(ctk.CTk):
    """Display editable sources, deterministic lessons, and measured results."""

    GRID_SIZE = 10
    HEADER_TABS = ["Static AST", "Runtime", "PPL Verdict"]

    def __init__(self, language_a: str = "Python", language_b: str = "JavaScript",
                 dark_mode: bool = True) -> None:
        """Build the dashboard and load the initial recursion lesson.

        Args:
            language_a: First launcher language label.
            language_b: Second launcher language label.
            dark_mode: Appearance selected in the launcher.
        Returns:
            None.
        """
        super().__init__()
        UIAssets.apply_theme()
        UIAssets.set_dark_mode(dark_mode)
        self.title("PPL Semantics Analyzer — Group 4")
        UIAssets.center_window(self, min(1440, self.winfo_screenwidth() - 40),
                               min(900, self.winfo_screenheight() - 80))
        self.minsize(1180, 720)
        self.configure(fg_color=UIAssets.COLORS["BG_PRIMARY"])
        self.report = None
        self.busy = False
        self.active_view = "Static AST"
        self.messages = queue.Queue()
        self.cancel_event = threading.Event()
        self.poll_id = None
        self.controls = []
        self.editors = []
        self.language_menus = []
        self.results = []
        self._configure_grid()
        self._build_header(dark_mode)
        self._build_sidebar()
        self._build_tools()
        self._build_editor("A", 3, language_a)
        self._build_editor("B", 6, language_b)
        self._build_results()
        self.div2_footer = self._frame(9, 0, 1, 10)
        self.status_label = ctk.CTkLabel(self.div2_footer, text="Ready", anchor="w",
                                        **UIAssets.label_kwargs("label"))
        self.status_label.pack(fill="x", padx=12, pady=4)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Control-Return>", lambda event: self._start(True))
        self.bind("<Command-Return>", lambda event: self._start(True))
        self._load_lesson()

    def _configure_grid(self) -> None:
        """Assign resize weights without moving the agreed panel coordinates.

        Args:
            None.
        Returns:
            None.
        """
        for column in range(self.GRID_SIZE):
            self.grid_columnconfigure(column, weight=1 if 3 <= column <= 8 else 0)
        self.grid_columnconfigure(0, minsize=100)
        self.grid_columnconfigure(1, minsize=115)
        self.grid_columnconfigure(2, minsize=115)
        self.grid_columnconfigure(9, minsize=12)
        for row in range(self.GRID_SIZE):
            self.grid_rowconfigure(row, weight=1 if 3 <= row <= 8 else 0)
        self.grid_rowconfigure(2, minsize=48)

    def _frame(self, row: int, column: int, rowspan: int, columnspan: int):
        """Create a flat panel at the established grid position.

        Args:
            row: Top grid row.
            column: Left grid column.
            rowspan: Number of rows to occupy.
            columnspan: Number of columns to occupy.
        Returns:
            The themed and gridded frame.
        """
        frame = ctk.CTkFrame(self, **UIAssets.frame_kwargs())
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                   sticky="nsew", padx=1, pady=1)
        return frame

    def _build_header(self, dark_mode: bool) -> None:
        """Build the title, functional view selector, and appearance toggle.

        Args:
            dark_mode: Initial appearance state.
        Returns:
            None.
        """
        self.div1_header = self._frame(0, 0, 2, 10)
        self.div1_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.div1_header, text="PARADIGM DIAGNOSTICS",
                     **UIAssets.label_kwargs("h1")).grid(row=0, column=0, padx=18, pady=16, sticky="w")
        self.tab_strip = ctk.CTkSegmentedButton(
            self.div1_header, values=self.HEADER_TABS, command=self._change_view,
            corner_radius=UIAssets.CORNER_RADIUS, font=UIAssets.FONTS["BODY"],
            fg_color=UIAssets.COLORS["SURFACE"], selected_color=UIAssets.COLORS["BLUE"],
            selected_hover_color=UIAssets.COLORS["BLUE_PRESSED"],
            unselected_color=UIAssets.COLORS["SURFACE"],
            unselected_hover_color=UIAssets.COLORS["TINT_NEUTRAL_A"],
            text_color=UIAssets.COLORS["TEXT_PRIMARY"],
        )
        self.tab_strip.set(self.active_view)
        self.tab_strip.grid(row=0, column=1, padx=12)
        self.appearance_switch = ctk.CTkSwitch(
            self.div1_header, text="Dark Mode", command=self._toggle_appearance,
            **UIAssets.switch_kwargs(),
        )
        if dark_mode:
            self.appearance_switch.select()
        self.appearance_switch.grid(row=0, column=2, padx=18)
        self.div7_analytics_title = self._frame(2, 1, 1, 9)
        self.summary_label = ctk.CTkLabel(
            self.div7_analytics_title, text="", anchor="w",
            **UIAssets.label_kwargs("body"),
        )
        self.summary_label.pack(fill="x", padx=12, pady=8)

    def _toggle_appearance(self) -> None:
        """Apply the theme selected by the switch.

        Args:
            None.
        Returns:
            None.
        """
        UIAssets.set_dark_mode(bool(self.appearance_switch.get()))

    def _build_sidebar(self) -> None:
        """Show project identity and the host's detected language tools.

        Args:
            None.
        Returns:
            None.
        """
        self.div3_sidebar_1 = self._frame(2, 0, 7, 1)
        ctk.CTkLabel(self.div3_sidebar_1, text="GROUP 4\n\nPPL\nCOMPARISON",
                     **UIAssets.label_kwargs("label")).pack(padx=8, pady=16)
        for language, path in runtime_paths().items():
            ctk.CTkLabel(self.div3_sidebar_1,
                         text=f"{language.upper()}\n{'Detected' if path else 'Missing'}",
                         wraplength=90, **UIAssets.label_kwargs("label")).pack(padx=6, pady=12)
        ctk.CTkLabel(self.div3_sidebar_1, text="Source\n↓\nTokens\n↓\nStructure\n↓\nExecution\n↓\nComparison",
                     **UIAssets.label_kwargs("label")).pack(padx=8, pady=24)

    def _build_tools(self) -> None:
        """Populate the tools panel with lesson, input, and execution controls.

        Args:
            None.
        Returns:
            None.
        """
        self.div8_tools_sidebar = ctk.CTkScrollableFrame(self, **UIAssets.frame_kwargs())
        self.div8_tools_sidebar.grid(row=3, column=1, rowspan=6, columnspan=2,
                                    sticky="nsew", padx=1, pady=1)
        parent = self.div8_tools_sidebar
        ctk.CTkLabel(parent, text="DEMONSTRATIONS", **UIAssets.label_kwargs("h2")).pack(padx=8, pady=(12, 6))
        self.lesson_menu = ctk.CTkOptionMenu(parent, values=list(LESSONS), **UIAssets.option_menu_kwargs())
        self.lesson_menu.pack(fill="x", padx=8, pady=4)
        self.controls.append(self.lesson_menu)
        self.load_button = self._button(parent, "Load lesson into both editors", self._load_lesson)
        self.lesson_text = ctk.CTkTextbox(parent, height=150, wrap="word", **UIAssets.textbox_kwargs())
        self.lesson_text.pack(fill="x", padx=8, pady=6)
        ctk.CTkLabel(parent, text="Shared standard input", **UIAssets.label_kwargs("label")).pack(padx=8, anchor="w")
        self.stdin_box = ctk.CTkTextbox(parent, height=60, **UIAssets.textbox_kwargs())
        self.stdin_box.pack(fill="x", padx=8, pady=4)
        self.stdin_box.bind("<<Modified>>", lambda event: self._text_modified(self.stdin_box))
        self.controls.append(self.stdin_box)
        ctk.CTkLabel(parent, text="Execution timeout (seconds)", **UIAssets.label_kwargs("label")).pack(padx=8, anchor="w")
        self.timeout_menu = ctk.CTkOptionMenu(parent, values=["1", "2", "5", "10"],
                                             command=self._edited, **UIAssets.option_menu_kwargs())
        self.timeout_menu.set("5")
        self.timeout_menu.pack(fill="x", padx=8, pady=4)
        self.controls.append(self.timeout_menu)
        self.analyze_button = self._button(parent, "Analyze only", lambda: self._start(False))
        self.run_button = self._button(parent, "Run comparison", lambda: self._start(True), "success")
        self.stop_button = self._button(parent, "Stop", self._stop, "danger", managed=False)
        self.stop_button.configure(state="disabled")
        self.export_button = self._button(parent, "Export report…", self._export, managed=False)
        self.export_button.configure(state="disabled")
        ctk.CTkLabel(parent, text="Run trusted classroom code only.\nProcess isolation is not a security sandbox.",
                     wraplength=210, **UIAssets.label_kwargs("label")).pack(padx=8, pady=10)

    def _button(self, parent, text: str, command, variant: str = "primary", managed: bool = True):
        """Build a themed tools button, optionally disabled during execution.

        Args:
            parent: Widget container.
            text: Button label.
            command: Click callback.
            variant: Design-token action color.
            managed: Whether execution should disable this control.
        Returns:
            The button widget.
        """
        button = ctk.CTkButton(parent, text=text, command=command, **UIAssets.button_kwargs(variant))
        button.pack(fill="x", padx=8, pady=4)
        if managed:
            self.controls.append(button)
        return button

    def _build_editor(self, label: str, column: int, language: str) -> None:
        """Build a source editor and independent language/file controls.

        Args:
            label: A or B.
            column: Starting root grid column.
            language: Initial display label selected in the launcher.
        Returns:
            None.
        """
        panel = self._frame(3, column, 4, 3)
        setattr(self, f"div{4 if label == 'A' else 5}_editor_{label.lower()}", panel)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(panel, **UIAssets.frame_kwargs(border=False))
        toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        toolbar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(toolbar, text=f"SNIPPET {label}", **UIAssets.label_kwargs("label")).grid(row=0, column=0, padx=(0, 8))
        menu = ctk.CTkOptionMenu(toolbar, values=list(LANGUAGE_LABELS), width=120,
                                command=self._edited, **UIAssets.option_menu_kwargs())
        menu.set(language if language in LANGUAGE_LABELS else "Python")
        menu.grid(row=0, column=1, sticky="w")
        index = len(self.editors)
        open_button = ctk.CTkButton(toolbar, text="Open…", width=64,
                                    command=lambda: self._open_source(index), **UIAssets.button_kwargs())
        open_button.grid(row=0, column=2, padx=(8, 0))
        editor = ctk.CTkTextbox(panel, wrap="none", height=240, undo=True, **UIAssets.textbox_kwargs())
        editor.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        editor.bind("<<Modified>>", lambda event: self._text_modified(editor))
        self.editors.append(editor)
        self.language_menus.append(menu)
        self.controls.extend([editor, menu, open_button])

    def _build_results(self) -> None:
        """Build aligned, scrollable result columns below both editors.

        Args:
            None.
        Returns:
            None.
        """
        self.div6_results = self._frame(7, 3, 2, 6)
        self.div6_results.grid_rowconfigure(1, weight=1)
        for index in range(2):
            self.div6_results.grid_columnconfigure(index, weight=1, uniform="results")
            ctk.CTkLabel(self.div6_results, text=f"RESULT {'AB'[index]}",
                         **UIAssets.label_kwargs("label")).grid(row=0, column=index, sticky="w", padx=8, pady=4)
            textbox = ctk.CTkTextbox(self.div6_results, wrap="word", height=210,
                                    **UIAssets.textbox_kwargs())
            textbox.grid(row=1, column=index, sticky="nsew", padx=8, pady=(0, 8))
            self.results.append(textbox)
            self._set_text(textbox, "Load or enter source, then Analyze only or Run comparison.", readonly=True)

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
        self._set_text(self.stdin_box, lesson["stdin"])
        self._set_text(self.lesson_text, lesson["concept"] + "\n\n" + lesson["explanation"], readonly=True)
        self._edited()
        self.status_label.configure(text=f"Loaded {self.lesson_menu.get()}. Edit either snippet, analyze, or run. Ctrl/⌘ + Enter runs both.")

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
        if self.busy:
            return
        self.report = None
        self.export_button.configure(state="disabled")
        self.summary_label.configure(text="Source/input changed — analyze or run to refresh results.")
        for textbox in self.results:
            self._set_text(textbox, "Results cleared. Analyze or run the current source and input.", readonly=True)

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
            messagebox.showerror("Source too large", "Use snippets of at most 100,000 characters.", parent=self)
            return
        languages = [LANGUAGE_LABELS[menu.get()] for menu in self.language_menus]
        stdin = self.stdin_box.get("1.0", "end-1c")
        timeout = float(self.timeout_menu.get())
        self.busy = True
        self.cancel_event.clear()
        for control in self.controls:
            control.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.export_button.configure(state="disabled")
        self.summary_label.configure(text="Running comparison…" if run else "Analyzing source…")
        self.status_label.configure(text="Working — C++ compilation has a separate budget. Stop cancels the current run.")
        for textbox in self.results:
            self._set_text(textbox, "Processing current snapshot…", readonly=True)
        # Keep the worker alive briefly after window close so its cancellation
        # handler can reap the child process before Python exits.
        threading.Thread(target=self._work, args=(sources, languages, stdin, timeout, run), daemon=False).start()
        self.poll_id = self.after(50, self._poll)

    def _work(self, sources: list, languages: list, stdin: str, timeout: float, run: bool) -> None:
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
            report = compare_snippets(sources[0], languages[0], sources[1], languages[1],
                                      stdin, timeout, run, self.cancel_event)
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
        if error:
            self.summary_label.configure(text="Comparison failed — see diagnostic below.")
            for textbox in self.results:
                self._set_text(textbox, error, readonly=True)
            self.status_label.configure(text="Ready to retry after correcting the source or environment.")
            return
        self.export_button.configure(state="normal")
        states = [item["execution"]["status"] if item["execution"] else "analyzed" for item in report["snippets"]]
        self.summary_label.configure(text=f"A: {states[0]}    |    B: {states[1]}    |    Open PPL Verdict for the comparison.")
        self.status_label.configure(text="Comparison complete. Results and exports describe this source/input snapshot.")
        self._change_view(self.active_view)

    def _change_view(self, view: str) -> None:
        """Render the chosen view from the most recent report snapshot.

        Args:
            view: One of the header tab labels.
        Returns:
            None.
        """
        self.active_view = view
        if self.report and not self.busy:
            for index, textbox in enumerate(self.results):
                self._set_text(textbox, render_view(self.report, index, view), readonly=True)

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
        path = filedialog.askopenfilename(parent=self, title=f"Open snippet {'AB'[index]}",
                                          filetypes=[("Source files", "*.py *.js *.cpp *.cc *.cxx"), ("All files", "*")])
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
            language = {".py": "Python", ".js": "JavaScript", ".cpp": "C++", ".cc": "C++", ".cxx": "C++"}.get(source_path.suffix.lower())
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
        path = filedialog.asksaveasfilename(parent=self, title="Export comparison report", defaultextension=".md",
                                            initialfile="ppl-comparison.md",
                                            filetypes=[("Markdown", "*.md"), ("JSON", "*.json")])
        if not path:
            return
        try:
            text = (json.dumps(self.report, indent=2, ensure_ascii=False) + "\n"
                    if Path(path).suffix.lower() == ".json" else render_report(self.report))
            Path(path).write_text(text, encoding="utf-8")
            self.status_label.configure(text=f"Report saved: {path}")
        except OSError as exc:
            messagebox.showerror("Could not save report", str(exc), parent=self)

    def _close(self) -> None:
        """Cancel active work and remove Tk polling before closing the window.

        Args:
            None.
        Returns:
            None.
        """
        self.cancel_event.set()
        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
        self.destroy()
