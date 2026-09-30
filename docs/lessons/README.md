# Lesson PDFs

These nine bundled PDFs accompany the **Paradigm Diagnostics** project by
**Mapua University, CSS125P Group 4**. The project has been presented and graded.
The **View Lesson** action on each Demonstrations card opens its corresponding local PDF.
To update a lesson later, preserve its filename or update the mapping in
`ui/lesson_resources.py`.

| Card | PDF |
| --- | --- |
| Recursion | `recursion.pdf` |
| Iteration | `iteration.pdf` |
| Lexical scope | `lexical_scope.pdf` |
| Types and coercion | `types_and_coercion.pdf` |
| Parameter passing | `parameter_passing.pdf` |
| Input and validation | `input_and_validation.pdf` |
| Syntax error | `syntax_error.pdf` |
| Runtime error | `runtime_error.pdf` |
| Timeout | `timeout.pdf` |

Card summaries and filenames are defined in `ui/lesson_resources.py`. Paths are
resolved relative to the repository, regardless of the launch directory. Missing
files and opening failures produce a recoverable dialog. Windows uses the
registered document handler; other platforms request the local file URI through
the browser handler.

**Load demonstration** is a separate action: it loads the source variants and
finite input preset from `core/examples.py` into the workspace without executing
them. PDF contents are not parsed or executed by the application.

The finalization smoke script checks all nine paths and action/error routing with
external opening calls mocked; it does not validate PDF content or viewer rendering.
