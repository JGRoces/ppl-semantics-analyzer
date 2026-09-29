# Implementation walkthrough

This guide explains the major code blocks and decisions so each team member can present the implementation. Read it beside the source files. Function docstrings describe arguments and return values; comments explain decisions that would otherwise be easy to misunderstand.

## 1. Entry point and launcher

`main.py:main()` creates one `Application` root and runs one event loop. `ui/application.py` mounts the welcome page inside that window. When Open workspace is clicked, `LauncherWindow._on_start()` reads the language and theme choices and calls `Application.open_workspace()`. That method builds the workspace as another child frame, raises it in the same grid cell, and destroys only the old entry widgets. The native window, geometry, and event loop remain intact. Cancel closes the root; closing during diagnostics invokes the workspace's process-cleanup path.

`LauncherWindow` and `MainWindow` are now `CTkFrame` pages, not separate roots. Return on the entry page is unbound during the transition, and the workspace installs its Ctrl/⌘ + Enter shortcut on the persistent root. The selected theme is applied without resetting the root to light mode.

`LauncherWindow` builds a split branding/setup screen inspired by the Java LoginGUI. `_choose_pair()` fills both language selectors from a preset card; `_sync_pair()` highlights the card matching the current choices. Its two menus restrict input to supported language labels. `_on_toggle_appearance()` changes the shared theme. `_on_start()` passes settings to the root controller; `_on_cancel()` closes without launching the dashboard. `get_selected_languages()` returns the saved selections.

## 2. Static analysis: `core/ast_analyzer.py`

### Request validation and independent results

`analyze_ast()` requires text, normalizes the language ID, and rejects unsupported languages. It creates a fresh result dictionary for every request. Lists cannot leak from one editor into the other. Empty text produces an explicit diagnostic. Python goes to `_analyze_python()`; JavaScript and C++ go to `_analyze_surface()`.

### Python lexical evidence

`tokenize.generate_tokens()` scans a text stream. Each token contains a kind, spelling, and source position. The implementation removes comments and line-separator bookkeeping from the preview, retains indentation evidence, and identifies keyword spellings. It counts all retained tokens but shows only the first 60 so the result remains readable. Tokenization failures are followed by parsing, which normally provides a clearer source diagnostic.

### Parsing and context checks

`ast.parse()` turns source into a tree of language constructs. A function becomes a function-definition node, an assignment becomes an assignment node, and an expression is represented by its operands and operator.

`compile(tree, ..., 'exec')` checks contextual restrictions without evaluating the code. This catches a top-level `return`, for example, even though a tree can be built for it. Syntax errors include a line and column. Successful validation does not guarantee successful execution: a division by zero can still fail later.

### Structural traversal

`ast.walk()` visits the tree. The conditions collect function names, lambdas, loop nodes, conditional nodes, assignment targets, parameters, import aliases, and exception target names. A set removes repeated variable spellings before sorting the output. Thus five assignments to `total` still count as one unique spelling. This is a documented metric, not a complete scoped symbol table.

`_python_function_is_recursive()` searches a function's body for calls to the same name. It deliberately skips separately nested function/class/lambda bodies. It does not resolve aliases or prove which object a name will denote at runtime, so the UI calls these **recursion candidates**.

`_python_scope_depth()` uses a stack of node/depth pairs. Entering a function, class, lambda, or comprehension increments structural depth. A loop or `if` does not increment it. This describes nesting syntax; it does not implement every rule of Python name lookup.

### JavaScript/C++ surface analysis

`_strip_comments_and_strings()` masks quoted text and comments in one left-to-right pattern scan while retaining newlines and positions. This prevents a URL such as a quoted `https://...` from accidentally treating the rest of its line as a comment.

`_analyze_surface()` collects remaining surface tokens and uses language-specific patterns for common named brace-bodied functions and simple variable declarations. For a candidate function, it scans braces to isolate that definition's body before looking for a same-name call. A call from `main()` is therefore not mistaken for recursion inside the helper.

This is still an approximation. JavaScript regex literals and template interpolation, C++ raw strings/macros, nested name binding, and complicated declarations are not fully understood. The code does not claim to validate these languages or compute their scope depth. Run delegates real source checking to their toolchains.

## 3. Execution: `core/execution_runner.py`

### Tool detection and result contract

`runtime_paths()` uses the current Python executable and searches PATH for Node and a C++ compiler. `_empty_result()` gives every run independent diagnostic fields. The `status` explains the outcome; `stdout`, `stderr`, timing, flags, and compilation fields preserve evidence.

`execute_code()` validates source, stdin, language, and a positive finite timeout. It returns a setup diagnostic when a tool is missing. A temporary directory holds the source and becomes the child's working directory. Ordinary relative writes therefore stay away from the project, but absolute paths and networking are not restricted.

### Language adapters

- Python writes a `.py` file and launches the current interpreter. `-u` keeps printed text available before a timeout; `-I` ignores user site packages and Python environment overrides.
- JavaScript writes a `.js` file and launches Node. It uses the real engine, not a JavaScript emulator written by the group.
- C++ writes a `.cpp` file, compiles with `-std=c++17`, and executes the resulting binary only after successful compilation. Compilation gets a separate budget and timing field. A rejected program is a compile error, not a missing-tool error.

### Input, output, and process polling

`_run_process()` writes supplied stdin to a temporary file and rewinds it. The child reads finite data followed by EOF, so it does not wait for an interactive terminal.

Stdout and stderr go to separate temporary files. This avoids pipe-buffer deadlocks and holding arbitrarily large output in memory. A loop checks cancellation, combined output size, process exit, and elapsed wall-clock time every 10 ms. The first applicable condition determines the status. Captured text is decoded with replacement for invalid bytes.

The output threshold is polled, so writes can briefly overshoot it. Captured stdout and stderr are each truncated to 64 KiB. This is a practical classroom limit, not a strict filesystem quota.

`finally` runs cleanup regardless of success or error. `_stop_process()` kills the process group on macOS/POSIX and the direct child on Windows. `wait()` reaps the direct child. The temporary directory is then removed. This does not guarantee containment of deliberately detached processes.

## 4. Comparison: `core/comparison.py`

`PROFILES` stores language reference facts separately from snippet metrics. For example, Python's dynamic typing is a language fact; the number of functions found in a particular source is an observation.

`compare_snippets()` receives two sources and languages plus shared stdin and the chosen budget. It analyzes each source. In static-only mode it creates no child processes. In Run mode it executes valid candidates and records diagnostics. A Python syntax failure skips execution of that snippet without preventing the other side from being processed.

Stdout is compared only if **both** processes succeeded. Two empty failure outputs do not count as equivalent behavior. Even identical successful stdout establishes only one observation for those inputs. The report retains source, stdin, timing budget, creation time, and both results so exports are reproducible snapshots.

`render_view()` formats one side of one result tab:

- Static AST explains the method, metrics, uncertainty, token evidence, and tree/pattern output.
- Runtime displays status, exit code, stdout, diagnostics, and separate process/compile times.
- PPL Verdict combines language reference facts with structural evidence and the limited output comparison.

`render_report()` builds Markdown containing source, stdin, and all three views. It chooses a code fence longer than any backtick sequence in the report so source text cannot accidentally close its own code block. JSON export uses the original dictionary directly.

## 5. Lesson logic: `core/examples.py`

`LANGUAGE_LABELS` maps friendly labels such as C++ to internal IDs such as `cpp`. `LESSONS` stores explanatory text, language variants, default stdin, and expected outputs/statuses. The dashboard always executes the source; expected results are used by tests, never displayed as if measured. `_source()` removes indentation introduced by Python multiline literals.

### Recursion

For argument five, factorial calls factorial with four, then three, two, and one. The base case returns one. Returning outward multiplies by two, three, four, and five, producing 120. All three examples implement that recurrence; C++ also needs an entry function and explicit parameter/return types.

### Iteration

An accumulator starts at zero. Each loop adds the next integer from one through five. Its values become 1, 3, 6, 10, and 15. This demonstrates mutable state and repeated control flow without a recursive call.

### Lexical scope

A global name denotes 10. Inside `show`, a separate local declaration with the same spelling denotes 20. The function prints its local value; the final output reads the global value. The outputs are 20 and 10, illustrating shadowing rather than global reassignment.

### Types and coercion

Each program attempts string text plus integer two. Python raises a TypeError at runtime; JavaScript converts the numeric operand for concatenation and prints 52; the selected C++ `std::string + int` expression fails compilation. This illustrates when an operation is checked and what the operator means, not a universal ranking of type systems.

### Parameter passing

Python and JavaScript pass access to the existing list/array into a function. Appending two mutates that object. Assigning the parameter a different container afterward changes only the local binding, so the caller still sees 1,2. C++ deliberately demonstrates a different mechanism: an `int&` parameter aliases the caller's integer, so assigning 99 changes that integer. These examples compare mechanisms rather than identical algorithms.

### Input and validation

Read all input, check that it represents an integer, enforce the range zero through ten, then square it. Seven produces 49. Malformed, fractional, empty, or out-of-range input is handled with an input-error message. The C++ version also checks for trailing non-whitespace after reading its integer.

### Error demonstrations

Syntax error has a deliberately malformed header. Runtime error uses valid syntax followed by an explicit uncaught error. Timeout uses a loop without a terminating condition. These separate grammatical failure, execution failure, and exceeding an observation budget. A timeout alone is not a proof of nontermination for arbitrary source.

## 6. Dashboard: `ui/main_window.py`

`__init__()` creates state, the queue, a cancellation event, and the dashboard shell. `_new_page()` allocates persistent pages in a common content area. `_show_page()` switches visibility and updates the active navigation; it never destroys editors. `_toggle_sidebar()` reduces the sidebar width and hides longer labels, giving the editors more room without losing source.

The `_build_*` methods create the header, sidebar, workspace, lesson library, report page, and guide. `_heading()` standardizes page titles. `_action()` styles toolbar buttons and registers controls to disable while work runs. `_select_lesson()` loads a library choice and returns to the workspace. `_refresh_report_page()` shows the current snapshot, a processing message, or an empty state so navigation cannot reveal stale results. `_toggle_appearance()` applies the selected theme. `_set_text()` replaces text and optionally makes it read-only.

`_load_lesson()` selects sources matching both language menus and fills shared stdin. `_text_modified()` handles the native modified flag for typing, paste, cut, undo, and redo. `_edited()` discards old results, preventing changed source from being displayed alongside stale evidence.

`_start()` snapshots widget contents on the GUI thread, validates source size, disables editing controls, and starts one worker. `_work()` calls the UI-independent comparison service and sends either its report or a readable exception to the queue. It never touches Tk.

`_poll()` runs through Tk's `after()` scheduling. If no result is ready, it schedules another check. On completion it restores controls and renders the selected view. `_change_view()` only reformats the stored report; switching tabs does not execute code again.

`_stop()` sets the cancellation event. `_close()` sets the same event and removes the polling callback before destroying the window. The worker is non-daemon so it has an opportunity to clean up its child before Python exits.

`_open_source()` reads a bounded UTF-8 file and infers language from familiar extensions. `_export()` asks for a destination and saves Markdown or JSON. Cancelling either dialog does nothing; file errors remain recoverable dialogs.

## 7. Line numbers: `ui/line_numbers.py`

Each editor shares a container with its own `LineNumberGutter`. The gutter uses a canvas; numbers never become part of source, copied text, execution input, or exported code.

The constructor finds the editor's native Tk Text child to obtain its actual origin and font. It subscribes to edits and layout changes and wraps the vertical-scroll callback. `_on_scroll()` first calls the original scrollbar callback, then schedules a redraw. Keeping that original callback is necessary for the scrollbar thumb to stay correct.

`_request_redraw()` combines repeated events into one idle callback, allowing Tk to finish laying out text. `_redraw()` uses the final logical line number to choose a width, starts at the top visible line, and calls `dlineinfo()` for each visible line. It offsets those coordinates by the difference between the text and canvas origins. Consequently numbers remain aligned after scrolling, resizing, and changes in padding or display scaling.

The gutter grows to fit three- or four-digit line numbers and shrinks when lines are deleted. An empty document still displays line one. Horizontal scrolling changes the source viewport but not the gutter. Appearance/scaling callbacks redraw the native canvas using shared design tokens; `destroy()` cancels scheduled work and removes event hooks.

## 8. Design tokens and verification

`UIAssets` centralizes colors, fonts, subtle borders, and rounded card/button radii, adapting the Java UIAssets design. The `accent_bar()` factory builds a mark using four shades of green. Its style factories return argument dictionaries used by widget constructors; appearance-aware color pairs select the light or dark value. The new gutter adds one background token and reuses the editor font and muted text color.

`core.self_check:main()` runs a real factorial snippet in each language and checks for 120. Locating an executable alone would not prove a compiler can build a program.

`tests/test_cases.py` covers normal examples, invalid inputs, structural regressions, tool failures, timeouts, cancellation, output limits, static-only behavior, and report content. `tests/gui_smoke.py` opens real native windows to exercise integration, including line-number alignment, scrolling, edits, theme changes, file loading, execution, error recovery, and export.

## 9. Green accents and header identity

`ACCENT`, `ACCENT_PRESSED`, and `TINT_ACCENT` are semantic theme keys used for primary actions, selected navigation, and selection cards. Their values are green; named `BRAND_GREEN_1` through `BRAND_GREEN_4` color the existing entry mark without changing its shape. The code preview uses green keyword/value tokens. Existing warning/error colors retain their meanings. The header removes the G4 badge and uses the H1 and BODY typography tokens for the product title and subtitle.
