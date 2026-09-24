# PPL Semantics Analyzer

> A desktop-based educational application designed to allow users to enter and compare source-code snippets from different programming languages.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-2fa5d6)
![Status](https://img.shields.io/badge/status-in--development-yellow)
![License](https://img.shields.io/badge/license-academic--use-lightgrey)

Built for **CSS125P – Principles of Programming Languages**, Group 4 project: *Programming Language Comparison and Demonstration System*[cite: 1, 3].

---

## Table of Contents

- [Authors](#authors)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [System Architecture](#system-architecture)
- [Known Limitations](#known-limitations)
- [Testing](#testing)

---

## Authors

| Name | Role | GitHub |
| :--- | :--- | :--- |
| Joseph Gabriel A. Roces | Lead Developer | [@JGRoces](https://github.com/JGRoces) |
| Marc Jansen D. Felipe | Developer | [@marcjfe](https://github.com/marcjfe) |
| Nikolai P. Lagarde | Developer | [@lagardenikolai](https://github.com/lagardenikolai) |
| Danaiah Niccola D. Bajao | Developer | *(TBD)* |

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Core Language | Python 3.10+ |
| Frontend UI | CustomTkinter (Desktop GUI) |
| Static Analysis | Native Python `ast` module (Python) & Regex Fallback (JS/C++) |
| Dynamic Execution | Native Python `subprocess` (isolated execution, timeout-enforced) |
| Testing | `pytest` |

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone [https://github.com/JGRoces/ppl-semantics-analyzer.git](https://github.com/JGRoces/ppl-semantics-analyzer.git)
cd ppl-semantics-analyzer

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the Desktop Application
python app.py
System ArchitectureThe graphical user interface is separated from the analysis and execution components so that the core processing operates independently of the presentation layer.   Plaintext USER
  │
  ▼
 CustomTkinter GUI (Source Code A / Source Code B)[cite: 3]
  │
  ├──► Static Analysis (core/ast_analyzer.py)[cite: 3]
  │
  └──► Runtime Execution (core/execution_runner.py)[cite: 3]
  │
  ▼
 Result Processing (Static Analysis / Runtime / PPL Comparison)[cite: 3]
Supported LanguagesPython: Analyzed using the built-in ast module to construct an Abstract Syntax Tree for accurate structural metrics[cite: 3].JavaScript & C++: Analyzed using a regex-based fallback approach to identify common source structures[cite: 3].Known LimitationsRegex Fallback: Because JavaScript and C++ use a regex-based fallback approach rather than a full language parser, structural analysis results for these languages are approximate[cite: 3].Local Toolchains Required: Multi-language execution requires the matching runtime on the host machine. JavaScript needs node on PATH; C++ needs g++ to compile before execution.TestingExecute the automated test suite to verify static analysis detection, subprocess isolation, and timeout enforcement[cite: 3]:Bashpytest tests/test_cases.py -v