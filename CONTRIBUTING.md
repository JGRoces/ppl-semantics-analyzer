# Contributing Guide — PPL Semantics Analyzer

Guidelines for our 4-person group. Please read before your first commit.

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

---

## AI Usage Log

Per academic integrity policy, log any AI-assisted work here (or in a shared doc linked from this file).

| Date | Tool | Prompt (summary) | Output Summary | Modifications Made | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| YYYY-MM-DD | e.g. Claude | e.g. "Generate subprocess timeout handler" | e.g. Function with try/except TimeoutExpired | e.g. Adjusted default timeout to 5s | e.g. Matched rubric's error-handling requirement |

---

## File Ownership & Task Distribution

| Module/File | Owner | Status |
| :--- | :--- | :--- |
| `app.py` (UI) | *(assign)* | Not started |
| `src/analyzers/static_ast.py` | *(assign)* | Not started |
| `src/runners/subprocess_runner.py` | *(assign)* | Not started |
| `src/utils/ppl_concepts.py` | *(assign)* | Not started |
| `tests/test_cases.py` | *(assign)* | Not started |
| `docs/documentation.md` (11 sections) | *(assign)* | Not started |

> Update this table in your first PR so everyone knows their lane.

---

## Pull Request Checklist

Before requesting review, confirm:

- [ ] Branch is up to date with `dev` (no merge conflicts)
- [ ] Code follows PEP 8 and includes docstrings
- [ ] New/changed logic has a corresponding test in `tests/test_cases.py`
- [ ] `pytest tests/test_cases.py` passes locally
- [ ] No direct changes to `main` or `dev`
- [ ] Commit messages follow the prefix standard
- [ ] AI Usage Log updated if AI tools were used
- [ ] PR description explains *what* changed and *why*
