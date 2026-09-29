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

Every color, font, and corner radius used in `ui/` **must** come from `ui/ui_assets.py` (`UIAssets.COLORS`, `UIAssets.FONTS`, or one of the `*_kwargs()` helpers). Do not hard-code a hex string or a `corner_radius` value directly inside a panel file — if the token you need doesn't exist yet, add it to `ui_assets.py` in your PR rather than inlining it. This is what keeps the flat/boxy look consistent across four people's panels.

---

## AI Usage Log

Per academic integrity policy, log any AI-assisted work here (or in a shared doc linked from this file).

| Date | Tool | Prompt (summary) | Output Summary | Modifications Made | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| YYYY-MM-DD | e.g. Claude | e.g. "Generate subprocess timeout handler" | e.g. Function with try/except TimeoutExpired | e.g. Adjusted default timeout to 5s | e.g. Matched rubric's error-handling requirement |
| 2026-09-29 | Codex | Add IDE-style line numbers to Editor A and B | Independent, scroll-aligned canvas gutters | Used shared theme tokens and native line geometry; added GUI checks | Make source lines easier to reference during demonstrations |
| 2026-09-29 | Codex | Complete the requested code explanations and presentation preparation | Function-level walkthrough and rehearsal guide | Documented actual implementation behavior, limitations, and verified demo paths | Help the team explain and rehearse the application |

---

## File Ownership & Task Distribution

> Update this table in your first PR so everyone knows their lane. `div` labels match the grid map documented at the top of `ui/main_window.py`.

| Module/File | Owner | Status |
| :--- | :--- | :--- |
| `main.py` (entry point — launcher → dashboard) | *(assign)* | Not started |
| `ui/ui_assets.py` (design tokens/theme, light + dark) | *(assign)* | Not started |
| `ui/launcher_window.py` (entry launcher window) | *(assign)* | Not started |
| `ui/main_window.py` (grid skeleton) | *(assign)* | Not started |
| `div1` Header (title, view tabs, dark-mode switch) | *(assign)* | Not started |
| `div2` Footer | *(assign)* | Not started |
| `div3` Sidebar 1 | *(assign)* | Not started |
| `div4` Editor A | *(assign)* | Not started |
| `div5` Editor B | *(assign)* | Not started |
| `div6` Results | *(assign)* | Not started |
| `div7` Analytics Title | *(assign)* | Not started |
| `div8` Tools Sidebar | *(assign)* | Not started |
| `core/ast_analyzer.py` | *(assign)* | Not started |
| `core/execution_runner.py` | *(assign)* | Not started |
| `tests/test_cases.py` | *(assign)* | Not started |
| `docs/documentation.md` (11 sections) | *(assign)* | Not started |

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
