"""
ppl_concepts.py

Central catalog of Principles of Programming Languages (PPL) concepts
used across the app: sidebar selection, static analysis labeling, and
the PPL Verdict tab. Keeping this as the single source of truth avoids
concept definitions drifting apart between UI and analysis code.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PPLConcept:
    """Represents a single PPL concept the system can detect or compare.

    Args:
        key: Short machine-readable identifier (e.g. "recursion").
        label: Human-readable name shown in the UI.
        description: One-line explanation shown as a tooltip/help text.
    """
    key: str
    label: str
    description: str


PPL_CONCEPTS: List[PPLConcept] = [
    PPLConcept(
        key="paradigm",
        label="Programming Paradigm",
        description="Imperative, functional, object-oriented, or declarative style.",
    ),
    PPLConcept(
        key="typing",
        label="Type System",
        description="Static vs. dynamic typing, strong vs. weak typing.",
    ),
    PPLConcept(
        key="scope_binding",
        label="Scope & Binding",
        description="Lexical vs. dynamic scope, variable binding rules.",
    ),
    PPLConcept(
        key="parameter_passing",
        label="Parameter Passing",
        description="By value, by reference, or by object reference.",
    ),
    PPLConcept(
        key="error_handling",
        label="Error Handling Model",
        description="Exceptions, error codes, or result/option types.",
    ),
    PPLConcept(
        key="recursion_iteration",
        label="Recursion vs. Iteration",
        description="How repetition is expressed and whether tail calls are optimized.",
    ),
]


BENCHMARK_PRESETS = {
    "Factorial (Recursion vs. Iteration)": {
        "python_recursive": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(6))",
        "python_iterative": "def factorial(n):\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result\n\nprint(factorial(6))",
    },
    "Variable Scope Demonstration": {
        "python_recursive": "x = 10\n\ndef show():\n    x = 20\n    print(x)\n\nshow()\nprint(x)",
        "python_iterative": "x = 10\n\ndef show():\n    print(x)\n\nshow()",
    },
    "Error Handling: Division": {
        "python_recursive": "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None\n\nprint(safe_divide(10, 0))",
        "python_iterative": "def safe_divide(a, b):\n    if b == 0:\n        return None\n    return a / b\n\nprint(safe_divide(10, 0))",
    },
}


def get_concept_by_key(key: str) -> PPLConcept:
    """Look up a PPLConcept by its key.

    Args:
        key: The concept's machine-readable identifier.

    Returns:
        The matching PPLConcept.

    Raises:
        KeyError: If no concept with that key exists.
    """
    for concept in PPL_CONCEPTS:
        if concept.key == key:
            return concept
    raise KeyError(f"Unknown PPL concept key: {key}")
