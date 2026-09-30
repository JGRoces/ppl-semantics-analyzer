# PPL Semantics Analyzer

An interactive desktop system for comparing **Python, JavaScript, and C++** through editable examples, structural analysis, and real execution.

Built for **CSS125P – Principles of Programming Languages**, **Group 4: Programming Language Comparison and Demonstration System**.

## Start here for the presentation

On the presentation Mac, run these commands from the repository directory:

```bash
venv/bin/python -m core.self_check
venv/bin/python main.py
```

The first command runs a real factorial program in each language, including C++ compilation. All three should print `PASS`. The second opens the launcher; choose two languages and click **Open workspace**. No browser, server, or internet connection is needed after installation.

Choose a lesson, click **Load lesson into both editors**, then **Run comparison**. Use **Static AST**, **Runtime**, and **PPL Verdict** to inspect structure, output/errors, and language concepts. Changing a language preserves the source; click **Load lesson** to replace it with the corresponding example. Loading a lesson intentionally replaces both editors and standard input.

- [Presentation and rehearsal guide](docs/presentation.md): a short demo sequence, expected outputs, team handoffs, and likely questions.
- [Required project documentation](docs/documentation.md): all 11 syllabus sections.
- [Detailed code walkthrough](docs/code_walkthrough.md): the logic of each module, function, and demo.
- [Contributor guidance](CONTRIBUTING.md): branch workflow, code conventions, ownership, and AI assistance log.

## Authors

| Name | Role | GitHub |
| :--- | :--- | :--- |
| Joseph Gabriel A. Roces | Lead Developer | [@JGRoces](https://github.com/JGRoces) |
| Marc Jansen D. Felipe | Developer | [@marcjfe](https://github.com/marcjfe) |
| Nikolai P. Lagarde | Developer | [@lagardenikolai](https://github.com/lagardenikolai) |
| Danaiah Niccola D. Bajao | Developer | Handle to be supplied by the team |

## What works

- Two independent source editors with line numbers, language selectors, and UTF-8 file loading. Python, JavaScript, and C++ syntax highlighting updates as you type, load lessons, or change languages, with colors for light and dark modes. Gutters stay aligned while editing and scrolling.
- Nine lessons: recursion, iteration, lexical scope, types/coercion, parameter passing, input validation, syntax errors, runtime errors, and timeouts.
- Python tokenization, AST display, structural metrics, and syntax/context validation without execution.
- Clearly labeled approximate structural analysis for JavaScript and C++.
- Real subprocess execution with standard input, stdout/stderr capture, exit status, timing, Stop, timeout, and bounded captured output.
- Separate C++ compile diagnostics and compilation timing.
- Responsive UI: background computation returns reports through a queue; only the main thread updates Tk.
- Language reference profiles and source-specific observations, including successful-output comparison.
- Markdown/JSON report export containing source, input, diagnostics, and all three views.
- Car Rental-inspired welcome screen, collapsible navigation, lesson cards, report page, and light/dark mode.

## Installation from a fresh clone

Python **3.10+ with Tk support** is required. JavaScript execution requires Node.js on `PATH`; C++ execution requires `g++` or `clang++` with C++17 support. Missing tools produce a setup diagnostic; Python analysis can still work.

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m core.self_check
python main.py
```

`venv` keeps dependencies local to the project. Activation makes `python` point to that environment. The requirements install CustomTkinter and pytest; the unused pandas dependency has been removed. The self-check verifies actual execution before opening the desktop application.

### Windows (PowerShell)

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m core.self_check
.\venv\Scripts\python.exe main.py
```

If `py` is unavailable but `python` works, use `python -m venv venv` for the first command. The explicit environment path avoids PowerShell activation restrictions and ensures installation and launch use the same interpreter. If launching from an editor, select `venv\Scripts\python.exe` as its Python interpreter.

If opening the workspace reports **`'yscrollcommand' is not a supported argument`**, update to a revision containing the gutter compatibility fix in `ui/line_numbers.py`, then rerun the installation and launch commands above. The gutter now attaches its scroll callback to the native Tk text widget. The runtime self-check does not exercise the GUI; test **Open workspace** too.

## Directory layout

```text
main.py                     Launcher → dashboard entry point
core/
  ast_analyzer.py            Tokenization, parsing, and structural evidence
  execution_runner.py        Local subprocess execution and resource limits
  examples.py                Nine lessons and expected results
  comparison.py              Comparison pipeline, language profiles, report text
  self_check.py              Actual runtime/compiler readiness check
ui/
  application.py             One persistent native window and page transition
  launcher_window.py         Split welcome screen and comparison choice cards
  main_window.py             Dashboard pages, workspace, and worker lifecycle
  ui_assets.py               Shared design tokens and widget style helpers
tests/
  test_cases.py              Automated backend, regression, and demo tests
  gui_smoke.py               Opt-in native GUI integration check
docs/
  documentation.md          Required 11-section submission write-up
  code_walkthrough.md       Detailed implementation explanations
  presentation.md           Rehearsal and oral-defense notes
```

Each stage has one responsibility. `core/` has no UI dependency, so tests can run without opening windows. The UI snapshots source and input, calls the comparison service, and displays the returned evidence.

## Architecture

```text
Launcher: choose languages and appearance
    ↓
Dashboard: source A + source B + shared standard input
    ↓
Worker: Python tokenizer/AST or JS/C++ surface analysis
    ↓
Optional execution: CPython / Node.js / C++17 compiler → native binary
    ↓
Queue → main GUI thread → Static AST / Runtime / PPL Verdict
    ↓
Optional Markdown or JSON report export
```

**Analyze only** performs inspection without running either snippet. **Run comparison** also launches the relevant toolchain. C++ type checks happen in the compiler; Python/JavaScript runtime errors come from the real interpreter/engine. The project does not implement a complete independent semantic checker for all three languages.

## Design philosophy

The UI takes inspiration from the team's Java Car Rental project: a split welcome screen, four-shade green brand mark, neutral top bar/sidebar, green active navigation, and rounded cards. The user-approved redesign replaces the earlier fixed 10×10 grid and sharp-corner rule.

- Light mode: gray page background, white cards, muted labels, subtle dividers.
- Dark mode: black page background and near-black surfaces with readable text.
- **Workspace** contains both line-numbered editors, execution controls, and expanded result tabs. Lessons use their preset standard input; there is no editable input or lesson-notes panel.
- Enable **Start with empty editors** on the launcher to open a clean workspace. **Clear results** removes diagnostics and the exportable report while keeping source; **Clear workspace** also empties both editors and preset input, preserving language and theme choices. Clearing is disabled during comparisons; use **Stop** and wait for completion first.
- **Demonstrations** presents nine lesson cards with concept summaries, **Load demonstration**, and **View Lesson**. Replace the placeholder PDFs in `docs/lessons/` using the filenames documented there.
- **Reports** shows the current source/input snapshot and supports Markdown/JSON export.
- **Back to Menu** cancels active work and returns to a fresh language selection screen in the same native window.
- Collapsing the sidebar gives the editors more room without reloading source.
- All fonts, colors, and radii remain centralized in `ui/ui_assets.py`.
- The theme follows the Car Rental references: rounded controls, gray page backgrounds and white cards in light mode, black backgrounds and near-black cards in dark mode, and terminal-green navigation and lesson accents. Red remains reserved for Stop/error actions.
- One persistent native window hosts both entry and workspace: opening diagnostics preserves position and size without closing/reopening.
- Native window controls preserve macOS resizing and focus behavior.

See [Design adaptation](docs/design_adaptation.md) for reference-to-Python mappings and implementation decisions.

## Verification

```bash
venv/bin/python -m pytest -q
venv/bin/python -m tests.gui_smoke
```

The first command runs automated tests, including all 27 lesson/language combinations and normal/error inputs. Tool-dependent tests skip explicitly if their runtime is missing. The second deliberately opens native windows and checks the launcher, worker, result tabs, file loading, export, errors, Stop, and recovery.

On Windows, use `.\venv\Scripts\python.exe -m pytest -q` and `.\venv\Scripts\python.exe -m tests.gui_smoke`. For a focused workspace/gutter check that requires no JavaScript runtime or C++ compiler, run `.\venv\Scripts\python.exe -m tests.gutter_smoke`. This opens the workspace with a wrapper that rejects `yscrollcommand`, then checks line alignment, scrolling, and callback restoration.

Verified on **2026-09-28** on the presentation Mac: Python 3.14.7, Node.js 26.9.0, Apple clang 21.0.0, CustomTkinter 5.2.2. See the testing section in the project documentation for recorded results. Desktop screenshot inspection was unavailable; native widget/callback tests were run.

## Limits to explain honestly

- **Python is parsed; JavaScript/C++ structure is estimated.** Surface patterns do not support their complete grammars. Unknown scope depth is shown as unknown; runtime/compiler diagnostics are obtained on Run.
- **Recursion detection finds candidates.** It recognizes simple same-name self-calls, not all possible aliases, mutual recursion, virtual dispatch, overload resolution, or rebinding.
- **Counts are descriptive.** Python and surface heuristics have different coverage. Unique variable spellings are not a full scoped symbol table.
- **Matching stdout for one input does not prove semantic equivalence.** Process timings include startup and are not rigorous performance benchmarks.
- **Run trusted classroom snippets only.** A temporary working directory, time limit, and output cap do not restrict filesystem/network access. Captured stdout and stderr are capped at 64 KiB each; their combined file size is polled against a 64 KiB stop threshold and may briefly overshoot. macOS/POSIX process groups clean up ordinary descendants; detached processes and Windows descendants are not fully contained.
- **The app is a comparison system.** It does not define a new language or implement a full compiler. Title/tool approval remains the instructor's decision.
