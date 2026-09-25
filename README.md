# PPL Semantics Analyzer

> An interactive meta-system for analyzing, executing, and comparing core Principles of Programming Languages concepts — side by side.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1f6feb)
![Status](https://img.shields.io/badge/status-in--development-yellow)
![License](https://img.shields.io/badge/license-academic--use-lightgrey)

Built for **CSS125P – Principles of Programming Languages**, Group 4 project: *Programming Language Comparison and Demonstration System*.

---

## Table of Contents

- [Authors](#authors)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [Directory Layout](#directory-layout)
- [System Architecture](#system-architecture)
- [Design System](#design-system)
- [Known Limitations](#known-limitations)
- [Documentation Sections](#documentation-sections-syllabus-requirement)
- [Testing](#testing)

---

## Authors

| Name | Role | GitHub |
| :--- | :--- | :--- |
| Joseph Gabriel A. Roces | Lead Developer | [@JGRoces](https://github.com/JGRoces) |
| Marc Jansen D. Felipe | Developer | [@marcjfe](https://github.com/marcjfe) |
| Nikolai P. Lagarde | Developer | [@lagardenikolai](https://github.com/lagardenikolai) |
| Danaiah Niccola D. Bajao | Developer | *(TBD)* |

> ⚠️ **Action needed:** Add Danaiah's GitHub handle before submission.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Core Language | Python 3.10+ |
| Desktop UI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (native `tkinter`-based GUI) |
| Static Analysis | Native Python `ast` module & tokenization |
| Dynamic Tracing | Native Python `subprocess` (isolated execution, timeout-enforced) |
| Testing | `pytest` |
| Version Control | Git — strict 2-branch model (`main` / `dev`) |

**Architectural pivot:** We moved off Streamlit's browser-based UI in favor of a native desktop app built with CustomTkinter. The `core/` backend (AST analysis, subprocess execution) is unchanged — only the presentation layer moved, from `app.py` (Streamlit) to the new `ui/` package (CustomTkinter).

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/JGRoces/ppl-semantics-analyzer.git
cd ppl-semantics-analyzer

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
# (requirements.txt now pulls in customtkinter instead of streamlit)
pip install customtkinter

# 4. Run the app
python main.py
```

💡 CustomTkinter opens a native desktop window — no browser, no local server, no port to remember.

---

## Directory Layout

**Changed:** the Streamlit `app.py` presentation layer has been replaced by a `ui/` package built on CustomTkinter. `core/` (backend analysis + execution) is untouched by this pivot.

```
ppl-semantics-analyzer/
├── main.py                         # Entry point — builds MainWindow and starts the mainloop
├── requirements.txt                # Pinned dependencies (customtkinter, not streamlit)
├── README.md
├── CONTRIBUTING.md
├── core/
│   ├── ast_analyzer.py             # Static analysis: true ast parse (Python) + regex fallback (JS/C++)
│   └── execution_runner.py         # Isolated, timeout-enforced execution (Python/Node/g++)
├── ui/
│   ├── ui_assets.py                # Design-token manager: colors, fonts, corner_radius=0 enforcement
│   └── main_window.py              # CTk root window: 10x10 grid skeleton, div frame placement
├── tests/
│   └── test_cases.py               # Required minimum test cases (normal + error)
└── docs/
    └── documentation.md            # 11-section syllabus documentation
```

**Why this layout?** Each stage of the PPL pipeline (*Source → Lexical/AST Analysis → Execution → Output*) stays isolated in its own module, and the UI never performs analysis or execution directly — it only calls into `core/`. This still means:
- A bug or infinite loop in a user's snippet can't crash the UI (subprocess isolation).
- Analysis logic can be unit-tested independently of the UI framework.
- Each group member can own one panel (`div`) or one backend module without merge conflicts.

---

## System Architecture

```
 Source Input (Snippet A / Snippet B, each with its own language)
          │
          ▼
 Lexical / AST Analysis  (core/ast_analyzer.py)
          │
          ▼
 Subprocess Execution    (core/execution_runner.py)
          │
          ▼
 Comparative Metric Display (ui/main_window.py — grid panels: editors, right rail, analytics)
```

| Stage | Module | Responsibility |
| :--- | :--- | :--- |
| Lexical/AST Analysis | `core/ast_analyzer.py` | True `ast` parse for Python (functions, recursion, loops, scope depth, exception usage); regex-token fallback for JavaScript/C++ |
| Execution | `core/execution_runner.py` | Runs the snippet in an isolated subprocess with a hard timeout; dispatches to the Python interpreter, Node.js, or a compiled g++ binary depending on language; captures stdout/stderr/duration in ms |
| Desktop UI | `ui/main_window.py` + `ui/ui_assets.py` | Renders the native window: header, code editors for Snippet A/B, left/right rails, and the analytics panel (Static AST / Runtime / PPL Verdict) |

---

## Design System

The UI follows a deliberately strict, flat aesthetic — no rounded corners, no gradients, no drop shadows. All tokens live in `ui/ui_assets.py` so no other module hard-codes a color or font:

- **Corners:** `corner_radius=0` on every frame, button, and textbox — sharp 90° edges throughout.
- **Palette:** Pure black/white base (`#000000` / `#0A0A0A` / `#FFFFFF`), with blue, red, and green reserved for primary, warning/destructive, and success actions respectively.
- **Typography:** A clean sans-serif (Segoe UI) for UI chrome; a monospace face (Consolas) for the code editors.

See `ui/ui_assets.py` for the full token set and the `UIAssets.apply_theme()` / `*_kwargs()` helpers that enforce it consistently.

---

## Known Limitations

- **Python's `ast` module only parses Python.** JavaScript and C++ snippets are analyzed with a regex-based token fallback instead of a true parse tree (see `core/ast_analyzer.py`). This is an approximation — it can miscount in edge cases (e.g. a keyword appearing inside a string) — and `max_scope_depth` is deliberately left `None` for these languages rather than guessed at with brace-counting.
- **The subprocess sandbox is teaching-grade, not production-grade.** It enforces a wall-clock timeout but does not fully restrict filesystem or network access. Do not point it at untrusted code outside a controlled demo environment.
- **Multi-language execution requires the matching runtime on the host machine.** JavaScript needs `node` on PATH; C++ needs `g++`. If either is missing, `execution_runner.py` reports a `setup_error` instead of crashing, but the language simply won't run on that machine until the toolchain is installed.
- **Type Systems and Parameter Passing concepts are not yet implemented** in the PPL Verdict panel (`div7`) — pending a design decision (static language-level lookup table vs. per-snippet inference).
- **The UI skeleton is layout-only for now.** `ui/main_window.py` currently places empty, labeled stub frames; wiring real widgets and backend calls into each `div` is tracked per-owner in `CONTRIBUTING.md`.

---

## Documentation Sections (Syllabus Requirement)

Full write-ups live in [`docs/documentation.md`](docs/documentation.md). Outline:

1. Project Title and Introduction
2. Problem Statement
3. General and Specific Objectives
4. Programming Language Concepts Applied
5. Language/Program Design
6. Keywords, Identifiers, Operators, Literals, Data Types, Statements, Expressions
7. Grammar / Syntax Rules
8. Program Architecture / Flow
9. Implementation Details
10. Testing and Results
11. Conclusion and Recommendations

---

## Testing

```bash
pytest tests/test_cases.py -v
```

Includes required minimum test cases covering both normal execution (recursion detection, successful subprocess run) and error handling (malformed syntax, runtime exception, timeout enforcement).
