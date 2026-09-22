# PPL Semantics Analyzer

> An interactive meta-system for analyzing, executing, and comparing core Principles of Programming Languages concepts — side by side.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-app-ff4b4b)
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
| Frontend UI | [Streamlit](https://streamlit.io/) |
| Static Analysis | Native Python `ast` module & tokenization |
| Dynamic Tracing | Native Python `subprocess` (isolated execution, timeout-enforced) |
| Testing | `pytest` |
| Version Control | Git — strict 2-branch model (`main` / `dev`) |

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

# 4. Run the app
streamlit run app.py
```

> 💡 The app will open automatically in your browser at `http://localhost:8501`.

---

## Directory Layout

> **Changed:** `src/analyzers` + `src/runners` have been consolidated into a single `core/` package, and the analyzers now support Python, JavaScript, and C++ (not just Python).

```
ppl-semantics-analyzer/
├── app.py                          # Streamlit UI — presentation layer only
├── requirements.txt                # Pinned dependencies
├── README.md
├── CONTRIBUTING.md
├── core/
│   ├── ast_analyzer.py             # Static analysis: true ast parse (Python) + regex fallback (JS/C++)
│   └── execution_runner.py         # Isolated, timeout-enforced execution (Python/Node/g++)
├── tests/
│   └── test_cases.py               # Required minimum test cases (normal + error)
└── docs/
    └── documentation.md            # 11-section syllabus documentation
```

**Why this layout?** Each stage of the PPL pipeline (*Source → Lexical/AST Analysis → Execution → Output*) is isolated into its own module. The UI (`app.py`) never performs analysis or execution directly — it only calls into `core/`. This means:
- A bug or infinite loop in a user's snippet can't crash the UI (subprocess isolation).
- Analysis logic can be unit-tested independently of Streamlit.
- Each group member can own one layer without merge conflicts.

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
 Comparative Metric Display (app.py — Static / Runtime / Verdict tabs)
```

| Stage | Module | Responsibility |
| :--- | :--- | :--- |
| Lexical/AST Analysis | `ast_analyzer.py` | True `ast` parse for Python (functions, recursion, loops, scope depth, exception usage); regex-token fallback for JavaScript/C++ |
| Execution | `execution_runner.py` | Runs the snippet in an isolated subprocess with a hard timeout; dispatches to the Python interpreter, Node.js, or a compiled g++ binary depending on language; captures stdout/stderr/duration in ms |
| Comparative Display | `app.py` | Renders side-by-side results across three tabs: Static AST Analysis, Runtime Execution, PPL Verdict |

---

## Known Limitations

- **Python's `ast` module only parses Python.** JavaScript and C++ snippets are analyzed with a regex-based token fallback instead of a true parse tree (see `core/ast_analyzer.py`). This is an approximation — it can miscount in edge cases (e.g. a keyword appearing inside a string) — and `max_scope_depth` is deliberately left `None` for these languages rather than guessed at with brace-counting.
- **The subprocess sandbox is teaching-grade, not production-grade.** It enforces a wall-clock timeout but does not fully restrict filesystem or network access. Do not point it at untrusted code outside a controlled demo environment.
- **Multi-language execution requires the matching runtime on the host machine.** JavaScript needs `node` on PATH; C++ needs `g++`. If either is missing, `execution_runner.py` reports a `setup_error` instead of crashing, but the language simply won't run on that machine until the toolchain is installed.
- **Type Systems and Parameter Passing concepts are not yet implemented** in the PPL Verdict tab — they're marked `TODO` in `app.py` pending a design decision (static language-level lookup table vs. per-snippet inference).

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
