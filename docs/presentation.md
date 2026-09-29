# Group 4 presentation and rehearsal guide

## Before presenting

Use the presentation Mac and run these commands from the project folder:

```bash
venv/bin/python -m core.self_check
venv/bin/python -m pytest -q
venv/bin/python main.py
```

The first command verifies actual execution in Python, Node, and C++. The second runs automated tests; on this Mac all three toolchains are available, so tool-dependent cases should not skip. The third opens the launcher. No network is needed for the installed app or bundled lessons.

Confirm text readability on the projector. Both editors have line numbers for referring to specific statements. Use horizontal scrolling for long source lines and each result column's vertical scrollbar for diagnostics. Export important runs as Markdown before the session so you have recorded examples available if needed.

## Suggested eight-minute sequence

| Time | Action | Explain |
| :--- | :--- | :--- |
| 0:00–0:45 | Introduce the title and Group 4 assignment | The system compares existing languages through editable source and measured behavior |
| 0:45–2:00 | Choose Python and JavaScript; run Recursion | Both print 120; explain parameters, base case, recursive step, and syntax differences |
| 2:00–3:00 | Open Static AST | Python has tokens and an actual tree; JS structural metrics are explicitly approximate |
| 3:00–4:15 | Load Types and coercion; Run; open Runtime | Python rejects string plus integer at runtime, JS prints 52 |
| 4:15–5:00 | Change B to C++; Load the same lesson; Run | C++ rejects the selected expression during compilation; point to compile diagnostics |
| 5:00–6:00 | Load Lexical scope or Parameter passing | Explain local binding versus global binding, or mutation versus parameter rebinding |
| 6:00–7:00 | Load Input and validation; run with 7, then abc | Show input, processing, output, and a handled error |
| 7:00–7:30 | Load Timeout; select one second; Run, or press Stop | A failing snippet does not prevent the dashboard from being used again |
| 7:30–8:00 | Show PPL Verdict and export a report | Separate language facts from observations; summarize verification and limitations |

Changing a language does not rewrite existing source automatically. Click **Load lesson into both editors** after changing languages when you want the matching example. Loading replaces both source editors and stdin.

## Suggested team handoffs

These are rehearsal roles, not changes to the repository's ownership assignments:

- Lead developer: introduce the architecture, explain the comparison service, and handle integration questions.
- Member 2: demonstrate lexical analysis, grammar, AST evidence, and the surface-analysis limitation.
- Member 3: demonstrate types, scope, recursion, and parameter passing using the lessons.
- Member 4: explain input validation, subprocess errors, tests, export, and conclusions.

Every member should run their demonstration personally before presenting. Avoid memorizing code without being able to explain why a condition or cleanup block exists.

## Likely questions

**Why is this Group 4 rather than a new interpreter?**  
It compares Python, JavaScript, and C++ through examples, analysis, and real execution. It uses their host toolchains and does not define a new programming language.

**What is syntax versus semantics?**  
Syntax describes valid structure. Semantics describes what that structure means. The coercion lesson shows why similar-looking operations can have different outcomes.

**Did you write a parser for all three languages?**  
No. Python uses its native tokenizer and AST. JavaScript/C++ structural counts use documented heuristics. Node and the C++ compiler provide actual source diagnostics during Run.

**Where does semantic analysis happen?**  
The application collects structural evidence and explains language rules. Context checks and actual compiler/runtime diagnostics supply additional evidence; C++ type checking is performed by the compiler. There is no complete custom semantic checker for all three languages.

**Does identical output prove equivalent programs?**  
It shows that two successful runs produced identical stdout for this particular input. It does not prove equal behavior for all inputs or account for every possible side effect.

**Is Python passed by reference?**  
Parameters bind to passed objects. Mutating a shared list is visible; rebinding the parameter is local. The lesson contrasts that behavior with an explicit C++ reference parameter.

**Why are JavaScript syntax errors shown under runtime diagnostics?**  
The app captures the result of launching Node. Node can reject syntax before executing the source, but that failure arrives through the process's stderr and nonzero exit status. Read the diagnostic to distinguish it from a later exception.

**Why use a worker thread and subprocess?**  
The worker keeps computation off the Tk event loop. The subprocess runs the snippet outside the app process and can be stopped. Only the main thread updates widgets.

**Is it a secure sandbox?**  
No. Time/output limits and a temporary working directory handle common classroom mistakes. They do not restrict filesystem/network access or fully contain hostile code. Use trusted snippets.

**Which language is fastest?**  
These timings are not enough to decide. They include process startup, C++ compilation is separate, and proper benchmarking requires repeated controlled measurements.

## Submission check

- Confirm the instructor-approved title and tools.
- Include all source, requirements, tests, README, and the 11-section documentation.
- Supply Danaiah's GitHub handle if the team wants it in the authors table.
- Keep the AI-assistance log and explain the reviewed implementation yourselves.
- Follow the project's feature-branch → dev → main review process for release.
