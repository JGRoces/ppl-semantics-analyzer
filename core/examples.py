"""Small, deterministic lessons for Group 4's live language comparison.

Each example has the same teaching purpose across languages. Expected outputs
are rehearsal/test fixtures, never substituted for real runtime results. Every
snippet is editable in the dashboard; use Load lesson to restore its original.
"""

from textwrap import dedent

LANGUAGE_LABELS = {"Python": "python", "JavaScript": "javascript", "C++": "cpp"}


def _source(text: str) -> str:
    """Normalize indentation of a readable embedded source example.

    Args:
        text: Multiline literal from this module.
    Returns:
        Left-aligned source with one trailing newline.
    """
    return dedent(text).strip() + "\n"


LESSONS = {
    "Recursion": {
        "concept": "Functions, selection, recursion",
        "explanation": "factorial(5) calls itself with a smaller argument until n <= 1. The base case returns 1; multiplication during return produces 120. Compare the syntax and direct-recursion evidence in Static AST.",
        "stdin": "", "expected": {"python": "120\n", "javascript": "120\n", "cpp": "120\n"},
        "sources": {
            "python": _source('''
                def factorial(n):
                    # Base case stops the chain of recursive calls.
                    if n <= 1:
                        return 1
                    return n * factorial(n - 1)

                print(factorial(5))
            '''),
            "javascript": _source('''
                function factorial(n) {
                    // The recursive step reduces the argument toward 1.
                    if (n <= 1) { return 1; }
                    return n * factorial(n - 1);
                }
                console.log(factorial(5));
            '''),
            "cpp": _source('''
                #include <iostream>
                int factorial(int n) {
                    if (n <= 1) { return 1; }
                    return n * factorial(n - 1);
                }
                int main() {
                    std::cout << factorial(5) << '\\n';
                }
            '''),
        },
    },
    "Iteration": {
        "concept": "Variables, assignment, loops",
        "explanation": "An accumulator starts at 0. The loop binds n to 1 through 5 and adds each value, giving 15. Repeated assignment changes a value without creating five distinct variable names.",
        "stdin": "", "expected": {"python": "15\n", "javascript": "15\n", "cpp": "15\n"},
        "sources": {
            "python": "total = 0\nfor n in range(1, 6):\n    total += n\nprint(total)\n",
            "javascript": "let total = 0;\nfor (let n = 1; n <= 5; n++) {\n    total += n;\n}\nconsole.log(total);\n",
            "cpp": "#include <iostream>\nint main() {\n    int total = 0;\n    for (int n = 1; n <= 5; n++) { total += n; }\n    std::cout << total << '\\n';\n}\n",
        },
    },
    "Lexical scope": {
        "concept": "Scope, shadowing, binding",
        "explanation": "The global value is 10. show() declares a local value of 20 with the same spelling. It prints 20, while the final print still sees the global 10. These are separate bindings; assigning the local name does not replace the global one.",
        "stdin": "", "expected": {"python": "20\n10\n", "javascript": "20\n10\n", "cpp": "20\n10\n"},
        "sources": {
            "python": "value = 10\ndef show():\n    value = 20\n    print(value)\nshow()\nprint(value)\n",
            "javascript": "const value = 10;\nfunction show() {\n    const value = 20;\n    console.log(value);\n}\nshow();\nconsole.log(value);\n",
            "cpp": "#include <iostream>\nint value = 10;\nvoid show() {\n    int value = 20;\n    std::cout << value << '\\n';\n}\nint main() {\n    show();\n    std::cout << value << '\\n';\n}\n",
        },
    },
    "Types and coercion": {
        "concept": "Type systems, operators, semantic errors",
        "explanation": "Each snippet attempts to combine string text with integer 2. Python raises TypeError at runtime. JavaScript's + coerces 2 to text and prints 52. C++ rejects std::string + int during compilation. Similar-looking operators have language-specific semantics.",
        "stdin": "", "expected": {"python": None, "javascript": "52\n", "cpp": None},
        "statuses": {"python": "runtime_error", "javascript": "success", "cpp": "compile_error"},
        "sources": {
            "python": 'text = "5"\nprint(text + 2)\n',
            "javascript": 'const text = "5";\nconsole.log(text + 2);\n',
            "cpp": '#include <iostream>\n#include <string>\nint main() {\n    std::string text = "5";\n    std::cout << text + 2 << \'\\n\';\n}\n',
        },
    },
    "Parameter passing": {
        "concept": "Parameters, mutation, rebinding, references",
        "explanation": "Python and JavaScript share access to the original container: appending 2 is visible, but rebinding the parameter to [99] is local, so the caller prints 1,2. The C++ int& parameter aliases the caller's integer: assignment changes it to 99. The examples contrast these mechanisms; they are not identical algorithms.",
        "stdin": "", "expected": {"python": "1,2\n", "javascript": "1,2\n", "cpp": "99\n"},
        "sources": {
            "python": "def change(items):\n    items.append(2)  # Mutate the shared list.\n    items = [99]  # Rebind only the local parameter.\n\nvalues = [1]\nchange(values)\nprint(','.join(map(str, values)))\n",
            "javascript": "function change(items) {\n    items.push(2); // Mutate the shared array.\n    items = [99]; // Rebind only the local parameter.\n}\nconst values = [1];\nchange(values);\nconsole.log(values.join(','));\n",
            "cpp": "#include <iostream>\nvoid change(int& value) {\n    value = 99; // Reference parameter aliases the caller's int.\n}\nint main() {\n    int value = 1;\n    change(value);\n    std::cout << value << '\\n';\n}\n",
        },
    },
    "Input and validation": {
        "concept": "Input, parsing values, selection, error handling",
        "explanation": "Supply one integer from 0 through 10. Each program validates its text and range, then prints its square. Try 7 for 49; try abc, 3.5 or 11 for a handled input error. Runtime stdin is finite text, so there is no interactive terminal prompt.",
        "stdin": "7\n", "expected": {"python": "49\n", "javascript": "49\n", "cpp": "49\n"},
        "sources": {
            "python": _source('''
                import re
                import sys
                try:
                    text = sys.stdin.read().strip()
                    if not re.fullmatch(r"[+-]?[0-9]+", text):
                        raise ValueError("Enter an integer from 0 to 10")
                    n = int(text)
                    if not 0 <= n <= 10:
                        raise ValueError("Enter an integer from 0 to 10")
                    print(n * n)
                except ValueError as error:
                    print("Input error:", error)
            '''),
            "javascript": _source('''
                const fs = require('fs');
                try {
                    const text = fs.readFileSync(0, 'utf8').trim();
                    const n = Number(text);
                    if (!/^[+-]?[0-9]+$/.test(text) || !Number.isInteger(n) || n < 0 || n > 10) {
                        throw new Error('Enter an integer from 0 to 10');
                    }
                    console.log(n * n);
                } catch (error) {
                    console.log('Input error: ' + error.message);
                }
            '''),
            "cpp": _source('''
                #include <iostream>
                #include <stdexcept>
                int main() {
                    try {
                        int n;
                        if (!(std::cin >> n) || n < 0 || n > 10) {
                            throw std::runtime_error("Enter an integer from 0 to 10");
                        }
                        std::cin >> std::ws;
                        if (!std::cin.eof()) {
                            throw std::runtime_error("Enter an integer from 0 to 10");
                        }
                        std::cout << n * n << '\\n';
                    } catch (const std::exception& error) {
                        std::cout << "Input error: " << error.what() << '\\n';
                    }
                }
            '''),
        },
    },
    "Syntax error": {
        "concept": "Grammar and diagnostics",
        "explanation": "A malformed function header violates each language's grammar. Python's parser reports it in Static AST; JavaScript and C++ errors come from the actual toolchain on Run. Surface metrics alone cannot validate their grammar.",
        "stdin": "", "expected": {"python": None, "javascript": None, "cpp": None},
        "statuses": {"python": "syntax_error", "javascript": "runtime_error", "cpp": "compile_error"},
        "sources": {"python": "def broken(:\n    return 1\n", "javascript": "function broken( {\n    return 1;\n}\n", "cpp": "int main( { return 0; }\n"},
    },
    "Runtime error": {
        "concept": "Valid syntax, failing execution",
        "explanation": "All three programs have valid syntax, then explicitly raise/throw an uncaught error. The child exits unsuccessfully and its diagnostics appear in Runtime while the application stays usable.",
        "stdin": "", "expected": {"python": None, "javascript": None, "cpp": None},
        "statuses": {"python": "runtime_error", "javascript": "runtime_error", "cpp": "runtime_error"},
        "sources": {"python": 'raise RuntimeError("Demo failure")\n', "javascript": 'throw new Error("Demo failure");\n', "cpp": '#include <stdexcept>\nint main() { throw std::runtime_error("Demo failure"); }\n'},
    },
    "Timeout": {
        "concept": "Nontermination and resource limits",
        "explanation": "An unconditional loop never reaches a terminating condition. The runner stops it at the selected timeout. A timeout is an observation within a budget, not a general proof that an arbitrary program cannot terminate.",
        "stdin": "", "expected": {"python": None, "javascript": None, "cpp": None},
        "statuses": {"python": "timeout", "javascript": "timeout", "cpp": "timeout"},
        "sources": {"python": "while True:\n    pass\n", "javascript": "while (true) {}\n", "cpp": "int main() {\n    volatile unsigned int counter = 0;\n    while (true) { ++counter; }\n}\n"},
    },
}
