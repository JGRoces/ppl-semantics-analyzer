# Contributing Guide — PPL Semantics Analyzer

Guidelines for our 4-person group. Please read before your first commit.

> 🔄 **Architectural pivot:** We've moved off Streamlit and onto a native desktop UI built with **CustomTkinter**. The old `app.py` presentation layer is being replaced by the `ui/` package — which now also includes an entry launcher (`ui/launcher_window.py`) shown before the main dashboard opens. `core/` (backend analysis + execution) is unaffected — if you were assigned a `core/` file before the pivot, nothing changes for you.

---

## Branching Model

We use a **strict 2-branch model**:

| Branch | Purpose | Direct pushes allowed? |
| :--- | :--- | :--- |
| `main` | Presentation/production-ready releases only | ❌ No |
| `dev` | Active integration branch | ❌ No |

All work happens on **feature branches** that merge into `dev` via Pull Request. `main` only receives merges from `dev` when we're ready to present.

> 🔒 **Protection expectation:** Both `main` and `dev` should be set as protected branches in GitHub settings (require PR review before merge, no force-push) once the repo is created.

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
| YYYY-MM-DD | e.g. Claude | e.g. "Generate subprocess timeout handler" | e.g. Function with try/except TimeoutExpired | e.g. Adjusted default timeout to 5s | e.g. Matched rubric's error-handling requirement |
| 2026-09-30 | Codex | Restore the screenshot and Car Rental design with a green terminal palette | Restored rounded controls and light/dark surface hierarchy | Kept menu navigation, expanded results, lesson summaries and PDF actions; made lesson badges green | Follow the user's updated visual direction while retaining completed functionality |
| 2026-09-30 | Codex | Finalize sidebar, workspace, and demonstration cards | Return-to-menu lifecycle, expanded results, lesson summaries, and PDF actions | Applied flat black/white surfaces with green/blue/red accents; added nine replaceable placeholder PDFs and focused GUI checks | Prepare the requested UI changes for review |
| 2026-09-30 | Codex | Diagnose workspace startup failure after a Windows clone | Native Tk scroll callback compatibility fix and explicit Windows setup commands | Updated gutter attachment/restoration and GUI regression coverage | Avoid unsupported CustomTkinter wrapper options and interpreter mismatches |
| 2026-09-29 | Codex | Add IDE-style line numbers to Editor A and B | Independent, scroll-aligned canvas gutters | Used shared theme tokens and native line geometry; added GUI checks | Make source lines easier to reference during demonstrations |
| 2026-09-29 | Codex | Complete the requested code explanations and presentation preparation | Function-level walkthrough and rehearsal guide | Documented actual implementation behavior, limitations, and verified demo paths | Help the team explain and rehearse the application |
| 2026-09-29 | Codex | Adapt the selected Java Car Rental UI designs to Python | Split launcher, shared palette, collapsible shell, lesson/report/guide pages | Kept the backend and gutters; retained native window controls; extended native GUI checks | Match the user's chosen visual direction without losing the working demo |
| 2026-09-29 | Codex | Use green accents, remove G4 badge, and make entry seamless | Green color tokens, larger header identity, and a persistent application root | Converted entry/workspace to child frames and checked native window identity and geometry | Preserve the chosen design while removing the close/reopen transition |

---

## File Ownership & Task Distribution

> Assign owners during team review. The user-approved redesign replaces numbered grid divisions with persistent dashboard pages. Central design tokens still apply.

| Module/File | Owner | Status |
| :--- | :--- | :--- |
| `main.py` / `ui/application.py` (persistent window) | *(assign)* | Implemented |
| `ui/ui_assets.py` (shared theme and styles) | *(assign)* | Implemented |
| `ui/launcher_window.py` (split welcome/setup screen) | *(assign)* | Implemented |
| `ui/main_window.py` (shell, navigation, workspace, lessons, reports, guide) | *(assign)* | Implemented |
| `ui/line_numbers.py` (editor gutters) | *(assign)* | Implemented |
| `core/ast_analyzer.py` | *(assign)* | Implemented; documented heuristic limits |
| `core/execution_runner.py` | *(assign)* | Implemented |
| `core/comparison.py` / `core/examples.py` | *(assign)* | Implemented |
| `tests/test_cases.py` / `tests/gui_smoke.py` | *(assign)* | Automated checks available |
| `docs/` | *(assign)* | Written; team review before submission |

---

## Pull Request Checklist

Before requesting review, confirm:

- [ ] Branch is up to date with `dev` (no merge conflicts)
- [ ] Code follows PEP 8 and includes docstrings
- [ ] New/changed logic has a corresponding test in `tests/test_cases.py`
- [ ] `pytest tests/test_cases.py` passes locally
- [ ] No direct changes to `main` or `dev`
- [ ] Commit messages follow the prefix standard
- [ ] UI changes use tokens from `ui/ui_assets.py` — no hard-coded colors, fonts, or corner radii
- [ ] AI Usage Log updated if AI tools were used
- [ ] PR description explains *what* changed and *why*
