"""Lesson card summaries and replaceable local PDF filenames."""

LESSON_RESOURCES = {
    "Recursion": {
        "pdf": "recursion.pdf",
        "summary": "Recursion solves a problem by calling the same function with a smaller input until a base case is reached. Each call adds a stack frame; factorial combines the results as those calls return.",
    },
    "Iteration": {
        "pdf": "iteration.pdf",
        "summary": "Iteration repeats a block of code while a loop advances toward its stopping condition. This example updates an accumulator with the numbers 1 through 5 to produce 15.",
    },
    "Lexical scope": {
        "pdf": "lexical_scope.pdf",
        "summary": "Lexical scope determines which binding a name refers to from its location in the source. A local variable can shadow a global variable without changing the global value.",
    },
    "Types and coercion": {
        "pdf": "types_and_coercion.pdf",
        "summary": "Type rules determine which values an operator accepts and whether conversions happen automatically. Combining text with an integer illustrates JavaScript coercion, a Python runtime error, and a C++ compilation error.",
    },
    "Parameter passing": {
        "pdf": "parameter_passing.pdf",
        "summary": "Parameter passing determines how a function can affect its caller's data. Compare mutation and local rebinding of Python and JavaScript containers with assignment through a C++ reference.",
    },
    "Input and validation": {
        "pdf": "input_and_validation.pdf",
        "summary": "Input validation checks both the format and range of incoming data before using it. This demonstration uses the preset input 7, accepts integers from 0 through 10, and prints the square of valid input.",
    },
    "Syntax error": {
        "pdf": "syntax_error.pdf",
        "summary": "Syntax errors occur when source code violates a language's grammar. Compare Python parser diagnostics with errors reported by the JavaScript runtime and C++ compiler for malformed function headers.",
    },
    "Runtime error": {
        "pdf": "runtime_error.pdf",
        "summary": "A program can have valid syntax and still fail during execution. These examples raise an uncaught error so you can inspect diagnostics and unsuccessful exit statuses while the application remains usable.",
    },
    "Timeout": {
        "pdf": "timeout.pdf",
        "summary": "An unconditional loop can keep running without reaching a stopping condition. The execution time limit stops this demonstration and reports a timeout, which alone does not prove that an arbitrary program could never finish.",
    },
}
