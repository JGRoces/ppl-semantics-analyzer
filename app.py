"""
app.py

Streamlit GUI for the PPL Semantics Analyzer -- refactored to move away
from Streamlit's native sidebar/default styling and implement the
team's 10x10 CSS Grid mockup directly:

    div1 -> full-width header banner              (top)
    div3 -> left rail: concept pills + presets     (st.columns[0])
    div5 -> Source A code editor                   (st.columns[1])
    div6 -> Source B code editor                   (st.columns[2])
    div4 -> right rail: languages, timeout, Run    (st.columns[3])
    div7 -> analytics tabs, spanning under 5+6      (below the row)
    div2 -> full-width footer banner               (bottom)

All backend calls remain unchanged: `core.ast_analyzer.analyze_ast`
and `core.execution_runner.execute_code`. Styling lives entirely in
`core/ui_assets.py` -- this file contains layout and state logic only.

IMPORTANT BEHAVIOR CHANGE from the previous version: analysis and
execution are no longer re-run on every Streamlit rerun (e.g. every
keystroke). They run once, on demand, when the user clicks
"Run Analysis" (div4). Results are cached in `st.session_state` so the
three analytics tabs stay populated until the next run. This avoids
re-executing untrusted/looping code on every widget interaction.
"""

import streamlit as st
from code_editor import code_editor

from core.ast_analyzer import analyze_ast
from core.execution_runner import execute_code
from core.ui_assets import inject_custom_css, section_label, badge


st.set_page_config(
    page_title="PPL Semantics Analyzer",
    page_icon="\U0001F9E9",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LANGUAGE_DISPLAY_NAMES = {
    "python": "Python",
    "javascript": "JavaScript",
    "cpp": "C++",
}

# Ace editor language modes differ slightly from our internal keys.
ACE_LANGUAGE_MAP = {
    "python": "python",
    "javascript": "javascript",
    "cpp": "c_cpp",
}

DEFAULT_SNIPPETS = {
    "python": (
        "def factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    return n * factorial(n - 1)\n\n"
        "print(factorial(5))\n"
    ),
    "javascript": (
        "function factorial(n) {\n"
        "    if (n <= 1) { return 1; }\n"
        "    return n * factorial(n - 1);\n"
        "}\n"
        "console.log(factorial(5));\n"
    ),
    "cpp": (
        "#include <iostream>\n"
        "int factorial(int n) {\n"
        "    if (n <= 1) return 1;\n"
        "    return n * factorial(n - 1);\n"
        "}\n"
        "int main() {\n"
        "    std::cout << factorial(5) << std::endl;\n"
        "    return 0;\n"
        "}\n"
    ),
}

PPL_CONCEPT_OPTIONS = [
    "Type Systems",
    "Control Flow",
    "Parameter Passing",
    "Scope & Binding",
    "Error Handling",
]

BENCHMARK_PRESETS = ["Factorial (Recursion)", "Custom (blank)"]


# --------------------------------------------------------------------
# div1: Header banner
# --------------------------------------------------------------------
def render_header():
    """Render the full-width header banner (div1)."""
    st.markdown(
        """
        <div class="ppl-header-banner">
            <h1>PPL Semantics Analyzer</h1>
            <p>Programming Language Comparison and Demonstration System — Group 4</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------
# div2: Footer banner
# --------------------------------------------------------------------
def render_footer():
    """Render the full-width footer banner (div2)."""
    st.markdown(
        """
        <div class="ppl-footer-banner">
            <p>CSS125P — Principles of Programming Languages | Group 4 | Roces, Felipe, Lagarde, Bajao</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------
# div3: Left rail -- PPL concept pills + benchmark preset
# --------------------------------------------------------------------
def render_left_rail():
    """Render the left rail (div3): concept pills and benchmark preset.

    Returns:
        A dict with keys "selected_concepts" (list[str]) and "preset" (str).
    """
    st.markdown('<div class="ppl-panel">', unsafe_allow_html=True)

    section_label("PPL Concepts in Focus")
    selected_concepts = st.pills(
        "PPL concepts",
        PPL_CONCEPT_OPTIONS,
        selection_mode="multi",
        default=PPL_CONCEPT_OPTIONS,
        label_visibility="collapsed",
        key="concept_pills",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Benchmark Preset")
    preset = st.pills(
        "Benchmark preset",
        BENCHMARK_PRESETS,
        selection_mode="single",
        default=BENCHMARK_PRESETS[0],
        label_visibility="collapsed",
        key="preset_pills",
    )
    # st.pills with selection_mode="single" can return None if the user
    # somehow deselects; fall back to the first preset so downstream
    # code never has to handle a None preset.
    preset = preset or BENCHMARK_PRESETS[0]

    st.markdown("</div>", unsafe_allow_html=True)

    return {"selected_concepts": selected_concepts or [], "preset": preset}


# --------------------------------------------------------------------
# div4: Right rail -- languages, timeout, Run Analysis button
# --------------------------------------------------------------------
def render_right_rail():
    """Render the right rail (div4): language pickers, timeout, Run button.

    Returns:
        A dict with keys "language_a", "language_b", "timeout_seconds",
        and "run_clicked" (bool, True only on the render where the
        button was pressed).
    """
    st.markdown('<div class="ppl-panel">', unsafe_allow_html=True)

    section_label("Target Languages")
    language_options = list(LANGUAGE_DISPLAY_NAMES.keys())
    language_a = st.selectbox(
        "Source A language",
        language_options,
        format_func=lambda key: LANGUAGE_DISPLAY_NAMES[key],
        key="language_a",
    )
    language_b = st.selectbox(
        "Source B language",
        language_options,
        index=min(1, len(language_options) - 1),
        format_func=lambda key: LANGUAGE_DISPLAY_NAMES[key],
        key="language_b",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Execution Settings")
    timeout_seconds = st.slider(
        "Timeout (seconds)", min_value=1, max_value=15, value=5, key="timeout_seconds"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    run_clicked = st.button("\U0001F680 Run Analysis", type="primary", use_container_width=True)

    st.markdown(
        f'<p style="font-size:0.75rem; margin-top:0.5rem;">'
        f"Static analysis: Python uses a true AST parse {badge('AST')}. "
        f"JS/C++ use a regex approximation {badge('REGEX')}.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "language_a": language_a,
        "language_b": language_b,
        "timeout_seconds": timeout_seconds,
        "run_clicked": run_clicked,
    }


# --------------------------------------------------------------------
# div5 / div6: Code editors (streamlit-code-editor, IDE-style)
# --------------------------------------------------------------------
def render_code_editor(panel_label: str, language: str, preset: str, session_key: str) -> str:
    """Render one IDE-style code editor panel (div5 or div6).

    Uses the `code_editor` component (react-ace under the hood) for
    line numbers and syntax highlighting, which `st.text_area` lacks.

    State handling: the editor's content is cached in
    `st.session_state[session_key]`. It is reset to the language's
    default snippet whenever the selected language OR benchmark preset
    changes for this panel -- otherwise stale code in the wrong
    language would linger in the editor after a language switch.

    Args:
        panel_label: Heading shown above the editor (e.g. "Source A").
        language: Currently selected language key for this panel.
        preset: Currently selected benchmark preset name.
        session_key: Unique session_state key for this panel's code
            (e.g. "source_a", "source_b").

    Returns:
        The current code string in this editor.
    """
    reset_marker_key = f"{session_key}_reset_marker"
    reset_marker = (language, preset)

    if session_key not in st.session_state or st.session_state.get(reset_marker_key) != reset_marker:
        st.session_state[session_key] = (
            DEFAULT_SNIPPETS[language] if preset != "Custom (blank)" else ""
        )
        st.session_state[reset_marker_key] = reset_marker

    st.markdown('<div class="ppl-panel">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ppl-section-label">{panel_label} ({LANGUAGE_DISPLAY_NAMES[language]})</div>',
        unsafe_allow_html=True,
    )

    response = code_editor(
        st.session_state[session_key],
        lang=ACE_LANGUAGE_MAP.get(language, "python"),
        theme="default",
        height=320,
        options={"wrap": True, "showLineNumbers": True},
        key=f"{session_key}_editor_{language}_{preset}",
    )

    # The component only returns a non-empty "text" once the user
    # triggers an event (e.g. Ctrl+Enter or blur), per its response_mode.
    if response and response.get("type") and response.get("text") is not None:
        st.session_state[session_key] = response["text"]

    st.markdown("</div>", unsafe_allow_html=True)
    return st.session_state[session_key]


# --------------------------------------------------------------------
# div7: Analytics panel (tabs)
# --------------------------------------------------------------------
def render_analytics_panel(source_a, source_b, language_a, language_b, controls):
    """Render the analytics panel (div7): AST / Runtime / Verdict tabs.

    Results are only computed when the user has clicked "Run Analysis"
    at least once (tracked in `st.session_state["last_run"]`) -- this
    keeps the three tabs from silently re-running execution on every
    unrelated widget interaction.

    Args:
        source_a: Current Source A code.
        source_b: Current Source B code.
        language_a: Language key for Source A.
        language_b: Language key for Source B.
        controls: Dict from `render_right_rail()` (timeout, run_clicked)
            merged with `render_left_rail()` (selected_concepts).
    """
    if controls["run_clicked"]:
        with st.spinner("Running static analysis and execution..."):
            st.session_state["last_run"] = {
                "static_a": analyze_ast(source_a, language_a),
                "static_b": analyze_ast(source_b, language_b),
                "exec_a": execute_code(source_a, language_a, timeout=controls["timeout_seconds"]),
                "exec_b": execute_code(source_b, language_b, timeout=controls["timeout_seconds"]),
                "language_a": language_a,
                "language_b": language_b,
            }

    st.markdown('<div class="ppl-panel">', unsafe_allow_html=True)

    last_run = st.session_state.get("last_run")

    if last_run is None:
        st.info("Click **\U0001F680 Run Analysis** in the right-hand panel to see results here.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    tab_static, tab_runtime, tab_verdict = st.tabs(
        ["\U0001F333 AST Analysis", "\u23F1\uFE0F Runtime Execution", "\u2696\uFE0F PPL Verdict"]
    )

    with tab_static:
        _render_static_tab(last_run)

    with tab_runtime:
        _render_runtime_tab(last_run, controls["timeout_seconds"])

    with tab_verdict:
        _render_verdict_tab(last_run, controls["selected_concepts"])

    st.markdown("</div>", unsafe_allow_html=True)


def _render_static_tab(last_run):
    """Render Tab 1: static structural metrics for both cached snippets."""
    col_a, col_b = st.columns(2)

    for label, key, lang_key, col in (
        ("A", "static_a", "language_a", col_a),
        ("B", "static_b", "language_b", col_b),
    ):
        metrics = last_run[key]
        lang = last_run[lang_key]
        with col:
            st.markdown(f"**Snippet {label} — {LANGUAGE_DISPLAY_NAMES[lang]}**")

            if metrics["syntax_error"]:
                st.error(f"Syntax error: {metrics['syntax_error']}")
                continue

            st.markdown(badge(metrics["parse_method"].upper()), unsafe_allow_html=True)
            st.write("Lines:", metrics["line_count"])
            st.write("Functions:", metrics["function_names"] or "None")
            st.write("Recursive functions:", metrics["recursive_functions"] or "None")
            st.write("Variables:", metrics["variable_names"] or "None")
            st.write("Loops:", metrics["loop_count"])
            st.write(
                "Max scope depth:",
                metrics["max_scope_depth"] if metrics["max_scope_depth"] is not None else "N/A (regex fallback)",
            )
            st.write("Uses exception handling:", metrics["uses_exception_handling"])


def _render_runtime_tab(last_run, timeout_seconds):
    """Render Tab 2: subprocess execution output/timing for both cached snippets."""
    col_a, col_b = st.columns(2)

    for label, key, lang_key, col in (
        ("A", "exec_a", "language_a", col_a),
        ("B", "exec_b", "language_b", col_b),
    ):
        outcome = last_run[key]
        lang = last_run[lang_key]
        with col:
            st.markdown(f"**Snippet {label} — {LANGUAGE_DISPLAY_NAMES[lang]}**")

            if outcome["setup_error"]:
                st.warning(outcome["setup_error"])
                if outcome["stderr"]:
                    st.code(outcome["stderr"], language="text")
                continue

            if outcome["timed_out"]:
                st.warning(f"Timed out after {timeout_seconds}s")
            elif outcome["exit_code"] == 0:
                st.success(f"Exit code 0  |  {outcome['duration_ms']:.2f} ms")
            else:
                st.error(f"Exit code {outcome['exit_code']}  |  {outcome['duration_ms']:.2f} ms")

            if outcome["stdout"]:
                st.code(outcome["stdout"], language="text")
            if outcome["stderr"]:
                st.code(outcome["stderr"], language="text")


def _render_verdict_tab(last_run, selected_concepts):
    """Render Tab 3: a PPL concept-by-concept comparison summary."""
    metrics_a = last_run["static_a"]
    metrics_b = last_run["static_b"]
    lang_a = LANGUAGE_DISPLAY_NAMES[last_run["language_a"]]
    lang_b = LANGUAGE_DISPLAY_NAMES[last_run["language_b"]]

    st.subheader("Concept-by-Concept Comparison")

    if "Control Flow" in selected_concepts:
        st.markdown("**Control Flow: Iteration vs. Recursion**")
        a_style = "recursive" if metrics_a.get("recursive_functions") else "iterative/other"
        b_style = "recursive" if metrics_b.get("recursive_functions") else "iterative/other"
        st.write(f"Snippet A ({lang_a}) appears **{a_style}**. Snippet B ({lang_b}) appears **{b_style}**.")

    if "Error Handling" in selected_concepts:
        st.markdown("**Error Handling Taxonomy**")
        st.write(
            f"Snippet A {'uses' if metrics_a.get('uses_exception_handling') else 'does not use'} "
            f"try/catch-style exception handling. Snippet B "
            f"{'uses' if metrics_b.get('uses_exception_handling') else 'does not use'} it."
        )

    if "Scope & Binding" in selected_concepts:
        st.markdown("**Scope & Binding**")
        depth_a = metrics_a.get("max_scope_depth")
        depth_b = metrics_b.get("max_scope_depth")
        st.write(
            f"Snippet A scope depth: {depth_a if depth_a is not None else 'not available (regex fallback)'}. "
            f"Snippet B scope depth: {depth_b if depth_b is not None else 'not available (regex fallback)'}."
        )

    if "Type Systems" in selected_concepts:
        st.markdown("**Type Systems**")
        st.info(
            "Static/dynamic typing is language-level, not snippet-level "
            "(Python and JS are always dynamically typed; C++ is always "
            "statically typed) — TODO: replace with a language lookup "
            "table rather than per-snippet inference."
        )

    if "Parameter Passing" in selected_concepts:
        st.markdown("**Parameter Passing**")
        st.info(
            "TODO: not yet implemented. Requires inspecting function "
            "signatures for reference markers (`&` in C++, mutable vs. "
            "immutable argument types in Python/JS)."
        )


def main():
    """Application entry point, assembling all seven grid regions."""
    inject_custom_css()

    render_header()  # div1

    left_col, editor_a_col, editor_b_col, right_col = st.columns([2.5, 3, 3, 1.5])

    with left_col:
        left_controls = render_left_rail()  # div3

    with right_col:
        right_controls = render_right_rail()  # div4

    with editor_a_col:
        source_a = render_code_editor(
            "Source A", right_controls["language_a"], left_controls["preset"], "source_a"
        )  # div5

    with editor_b_col:
        source_b = render_code_editor(
            "Source B", right_controls["language_b"], left_controls["preset"], "source_b"
        )  # div6

    st.markdown("<br>", unsafe_allow_html=True)

    controls = {**left_controls, **right_controls}
    render_analytics_panel(
        source_a, source_b, right_controls["language_a"], right_controls["language_b"], controls
    )  # div7

    render_footer()  # div2


if __name__ == "__main__":
    main()
