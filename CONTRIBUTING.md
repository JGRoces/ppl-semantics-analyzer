# Contributing Guide — PPL Semantics Analyzer

Maintenance guidelines for the four-person **Mapua University, CSS125P Group 4** team. The project has been presented and graded; these conventions apply to subsequent changes.

**Current architecture:** `main.py` creates one `ui/application.py` native root. Entry and workspace are child frames; the dashboard contains Workspace, Demonstrations, and Reports. `core/` performs analysis, execution, and report rendering independently of Tk. A worker returns snapshots through a queue; only the main thread accesses widgets. Pygments provides editor coloring, while Python AST analysis and the host toolchains provide diagnostics.

---

## Branching Model

We use a **strict 2-branch model**:

| Branch | Purpose | Direct pushes allowed? |
| :--- | :--- | :--- |
| `main` | Presentation/production-ready releases only | ❌ No |
| `dev` | Active integration branch | ❌ No |

All work happens on **feature branches** that merge into `dev` via Pull Request. `main` only receives merges from `dev` when an integration release is ready.

> 🔒 **Protection expectation:** Both `main` and `dev` should be set as protected branches in GitHub settings (require PR review before merge, no force-push) for ongoing maintenance; this document does not verify remote protection settings.

Feature branch naming convention:

```
feature/<short-description>
fix/<short-description>
docs/<short-description>
```

Example: `feature/subprocess-timeout`, `fix/ast-scope-depth`, `docs/readme-architecture`

---

## Daily Git Workflow

```bash
# 1. Sync dev before starting new work
git checkout dev
git pull origin dev

# 2. Create a feature branch off dev
git checkout -b feature/my-change

# 3. Make your changes, then stage and commit
git add .
git commit -m "add: recursion detection to static analyzer"

# 4. Push your feature branch
git push origin feature/my-change

# 5. Open a Pull Request into dev on GitHub
#    (never merge directly — request review from at least one teammate)

# 6. After merge, clean up locally
git checkout dev
git pull origin dev
git branch -d feature/my-change
```

---

## Commit Message Standard

Prefix every commit message with one of the following:

| Prefix | Use for |
| :--- | :--- |
| `add:` | New files, functions, or features |
| `fix:` | Bug fixes |
| `update:` | Changes to existing behavior/logic |
| `docs:` | Documentation-only changes |
| `refactor:` | Code restructuring with no behavior change |
| `test:` | Adding or updating tests |

**Format:** `<prefix> <short, present-tense description>`

Example: `test: add timeout enforcement case for subprocess runner`

---

## Python Code Standards (PEP 8)

- Follow idiomatic Python — no Allman/BSD-style bracing (not applicable to Python, but applies to any embedded C-like snippets used as comparison examples).
- Standard 4-space indentation, no tabs.
- All functions require a docstring with:
  - A one-line summary
  - `Args:` section describing parameters
  - `Returns:` section describing the return value
  - `Raises:` section if applicable
- Prefer descriptive names over abbreviations (`snippet_a`, not `sa`).
- Run a formatter/linter (e.g., `black`, `flake8`) before opening a PR if available.

### UI-Specific Rule: No Hard-Coded Design Values

Every color, font, and corner radius used in `ui/` **must** come from `ui/ui_assets.py` (`UIAssets.COLORS`, `UIAssets.FONTS`, or one of the `*_kwargs()` helpers). Do not hard-code a hex string or a `corner_radius` value directly inside a panel file — if the token you need doesn't exist yet, add it to `ui_assets.py` in your PR rather than inlining it. This is what keeps the shared Car Rental-inspired visual language consistent across four people's panels.

---

## AI Usage Log

Per academic integrity policy, log any AI-assisted work here (or in a shared doc linked from this file).

| Date | Tool | Prompt (summary) | Output Summary | Modifications Made | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-09-30 | Codex | Add clear actions and an empty workspace launch option | Separate results/source clearing and clean startup | Added launcher toggle, busy-state guards, reset checks, and safe focus/highlighting cleanup | Allow a fresh workspace without restarting the application |
| 2026-09-30 | Codex | Add syntax highlighting to both source editors | Language-aware coloring for Python, JavaScript, and C++ | Added Pygments, shared light/dark syntax colors, debounced text tags, and native GUI checks | Improve readability while preserving source, undo history, and editor navigation |
| 2026-09-30 | Codex | Align demonstration descriptions with their concept cards | Responsive text wrapping and consistent action alignment | Used available card width with display scaling, aligned content with a grid, and verified resizing in GUI checks | Make descriptions use the card space and keep buttons aligned |
| 2026-09-30 | Codex | Refresh all remaining Markdown after presentation and grading | Current architecture, setup, UI lifecycle, and recorded verification | Added Mapua University; removed deleted-file links and obsolete UI instructions; preserved historical assistance entries | Keep the completed project documentation aligned with the source |
| 2026-09-30 | Codex | Restore the screenshot and Car Rental design with a green terminal palette | Restored rounded controls and light/dark surface hierarchy | Kept menu navigation, expanded results, lesson summaries and PDF actions; made lesson badges green | Follow the user's updated visual direction while retaining completed functionality |
| 2026-09-30 | Codex | Finalize sidebar, workspace, and demonstration cards | Return-to-menu lifecycle, expanded results, lesson summaries, and PDF actions | Applied flat black/white surfaces with green/blue/red accents; added nine replaceable placeholder PDFs and focused GUI checks | Prepare the requested UI changes for review |
| 2026-09-30 | Codex | Diagnose workspace startup failure after a Windows clone | Native Tk scroll callback compatibility fix and explicit Windows setup commands | Updated gutter attachment/restoration and GUI regression coverage | Avoid unsupported CustomTkinter wrapper options and interpreter mismatches |
| 2026-09-29 | Codex | Add IDE-style line numbers to Editor A and B | Independent, scroll-aligned canvas gutters | Used shared theme tokens and native line geometry; added GUI checks | Make source lines easier to reference during demonstrations |
| 2026-09-29 | Codex | Complete the requested code explanations and presentation preparation | Function-level walkthrough and rehearsal guide | Documented actual implementation behavior, limitations, and verified demo paths | Help the team explain and rehearse the application |
| 2026-09-29 | Codex | Adapt the selected Java Car Rental UI designs to Python | Split launcher, shared palette, collapsible shell, lesson/report/guide pages | Kept the backend and gutters; retained native window controls; extended native GUI checks | Match the user's chosen visual direction without losing the working demo |
| 2026-09-29 | Codex | Use green accents, remove G4 badge, and make entry seamless | Green color tokens, larger header identity, and a persistent application root | Converted entry/workspace to child frames and checked native window identity and geometry | Preserve the chosen design while removing the close/reopen transition |

---

## File Ownership & Task Distribution

> Individual maintenance owners have not been recorded. The table inventories implemented modules without inferring authorship. Central design tokens apply to all UI changes.

| Module/File | Owner | Status |
| :--- | :--- | :--- |
| `main.py` / `ui/application.py` (persistent window) | *(assign)* | Implemented |
| `ui/ui_assets.py` (shared theme and styles) | *(assign)* | Implemented |
| `ui/launcher_window.py` (split welcome/setup screen) | *(assign)* | Implemented |
| `ui/main_window.py` (shell, workspace, demonstrations, reports, worker lifecycle) | *(assign)* | Implemented |
| `ui/line_numbers.py` (editor gutters) | *(assign)* | Implemented |
| `ui/syntax_highlighting.py` / `ui/lesson_resources.py` | *(assign)* | Implemented |
| `core/ast_analyzer.py` | *(assign)* | Implemented; documented heuristic limits |
| `core/execution_runner.py` | *(assign)* | Implemented |
| `core/comparison.py` / `core/examples.py` | *(assign)* | Implemented |
| `tests/test_cases.py` / four `tests/*smoke.py` scripts | *(assign)* | Backend tests and opt-in native checks available |
| `docs/` | *(assign)* | Updated for the presented and graded application |

---

## Local verification and dependency updates

Install `requirements.txt` after syncing dependency changes. It includes CustomTkinter, Pygments, and pytest. On Windows, use `.\venv\Scripts\python.exe -m pip install -r requirements.txt` and launch with `.\venv\Scripts\python.exe main.py` to avoid interpreter mismatches. macOS/Linux can use `venv/bin/python` for the same commands.

Run `python -m pytest -q` for backend tests and `python -m core.self_check` for real toolchain execution. For native UI changes, select the relevant `python -m tests.gui_smoke`, `tests.gutter_smoke`, `tests.finalization_smoke`, or `tests.syntax_smoke` module. These open windows and are separate from pytest. PDF action tests mock external viewers; do not report them as PDF visual checks.

Keep documentation aligned with actual source behavior: lesson input is preset, dashboard navigation preserves state, Back to Menu disposes of it, and Pygments coloring is not a parser. Retain documented limitations of approximate JavaScript/C++ analysis and local subprocess execution.

## Pull Request Checklist

Before requesting review, confirm:

- [ ] Branch is up to date with `dev` (no merge conflicts)
- [ ] Code follows PEP 8 and includes docstrings
- [ ] Behavioral changes have appropriate backend or native GUI regression coverage
- [ ] `python -m pytest -q` passes locally; tool-dependent skips are reported
- [ ] Relevant native smoke scripts pass for UI changes
- [ ] Dependency changes are in `requirements.txt`; install with the interpreter used to launch
- [ ] No direct changes to `main` or `dev`
- [ ] Commit messages follow the prefix standard
- [ ] UI changes use tokens from `ui/ui_assets.py` — no hard-coded colors, fonts, or corner radii
- [ ] AI Usage Log updated if AI tools were used
- [ ] PR description explains *what* changed and *why*
