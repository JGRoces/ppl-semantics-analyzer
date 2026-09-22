"""
core/ui_assets.py

Design system module for the PPL Semantics Analyzer. Injects a single
block of custom CSS that overrides Streamlit's default styling to
achieve a flat, black/white/green aesthetic that respects the
viewer's OS-level light/dark preference.

This module intentionally contains NO analysis or execution logic --
it is styling only, so a teammate reworking the palette never has to
touch `app.py`, and a teammate reworking layout logic never has to
touch CSS.

Usage in app.py:

    from core.ui_assets import inject_custom_css
    inject_custom_css()   # call once, near the top of main()
"""

import streamlit as st

# Design tokens, kept as module-level constants so any future JS/HTML
# snippets (e.g. the code editor's theme config) can reference the same
# values instead of duplicating hex codes in two places.
LIGHT_ACCENT = "#059669"
DARK_ACCENT = "#34D399"
LIGHT_ACCENT_SOFT = "#10B981"

FONT_SANS_STACK = (
    "'Inter', 'Geist', -apple-system, BlinkMacSystemFont, "
    "'Segoe UI', Roboto, sans-serif"
)
FONT_MONO_STACK = (
    "'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Consolas, "
    "'Liberation Mono', Menlo, monospace"
)


def inject_custom_css() -> None:
    """Inject the app's custom CSS into the current Streamlit page.

    Call this once near the top of the page render (ideally the first
    Streamlit call after `st.set_page_config`), before any other UI is
    drawn, so the override rules apply to everything rendered after.

    Returns:
        None. Writes directly into the page via `st.markdown`.
    """
    st.markdown(_build_css(), unsafe_allow_html=True)


def _build_css() -> str:
    """Assemble the full CSS block as a single string.

    Returns:
        A string containing a <style> tag with:
          - Google Fonts imports for Inter and JetBrains Mono
          - CSS custom properties (design tokens) for light mode by
            default, redefined under `@media (prefers-color-scheme:
            dark)` for dark mode
          - Flat-design overrides for Streamlit's default containers,
            buttons, tabs, inputs, and sidebar-adjacent elements
    """
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ------------------------------------------------------------
       Design tokens (light mode defaults)
       ------------------------------------------------------------ */
    :root {{
        --ppl-bg: #FFFFFF;
        --ppl-bg-container: #F7F7F7;
        --ppl-bg-container-alt: #F0F0F0;
        --ppl-text: #0A0A0A;
        --ppl-text-muted: #5A5A5A;
        --ppl-border: #E2E2E2;
        --ppl-accent: {LIGHT_ACCENT};
        --ppl-accent-soft: {LIGHT_ACCENT_SOFT};
        --ppl-accent-text: #FFFFFF;
        --ppl-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        --ppl-font-sans: {FONT_SANS_STACK};
        --ppl-font-mono: {FONT_MONO_STACK};
    }}

    /* ------------------------------------------------------------
       Design tokens (dark mode -- OS-level preference only, no
       manual toggle required)
       ------------------------------------------------------------ */
    @media (prefers-color-scheme: dark) {{
        :root {{
            --ppl-bg: #000000;
            --ppl-bg-container: #121212;
            --ppl-bg-container-alt: #1A1A1A;
            --ppl-text: #F5F5F5;
            --ppl-text-muted: #A0A0A0;
            --ppl-border: #2A2A2A;
            --ppl-accent: {DARK_ACCENT};
            --ppl-accent-soft: {DARK_ACCENT};
            --ppl-accent-text: #0A0A0A;
            --ppl-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
    }}

    /* ------------------------------------------------------------
       Base page
       ------------------------------------------------------------ */
    html, body, [class*="css"] {{
        font-family: var(--ppl-font-sans);
    }}

    .stApp {{
        background-color: var(--ppl-bg);
        color: var(--ppl-text);
    }}

    /* Trim Streamlit's default top padding so div1 sits flush */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--ppl-font-sans);
        color: var(--ppl-text);
        font-weight: 600;
        letter-spacing: -0.01em;
    }}

    p, span, label, div {{
        color: var(--ppl-text);
    }}

    /* ------------------------------------------------------------
       Flat containers -- used for div1/div2/div3/div4/div7 wrappers
       ------------------------------------------------------------ */
    .ppl-panel {{
        background-color: var(--ppl-bg-container);
        border: 1px solid var(--ppl-border);
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: var(--ppl-shadow);
    }}

    .ppl-panel-alt {{
        background-color: var(--ppl-bg-container-alt);
        border: 1px solid var(--ppl-border);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: var(--ppl-shadow);
    }}

    .ppl-header-banner {{
        background-color: var(--ppl-bg-container);
        border: 1px solid var(--ppl-border);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        box-shadow: var(--ppl-shadow);
        margin-bottom: 1rem;
    }}

    .ppl-header-banner h1 {{
        margin: 0;
        font-size: 1.5rem;
    }}

    .ppl-header-banner p {{
        margin: 0.15rem 0 0 0;
        color: var(--ppl-text-muted);
        font-size: 0.9rem;
    }}

    .ppl-footer-banner {{
        background-color: var(--ppl-bg-container);
        border: 1px solid var(--ppl-border);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        box-shadow: var(--ppl-shadow);
        margin-top: 1.5rem;
        text-align: center;
    }}

    .ppl-footer-banner p {{
        margin: 0;
        color: var(--ppl-text-muted);
        font-size: 0.8rem;
    }}

    .ppl-section-label {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--ppl-text-muted);
        margin-bottom: 0.5rem;
    }}

    /* ------------------------------------------------------------
       Accent elements
       ------------------------------------------------------------ */
    .ppl-accent-text {{
        color: var(--ppl-accent);
        font-weight: 600;
    }}

    .ppl-badge {{
        display: inline-block;
        background-color: var(--ppl-accent);
        color: var(--ppl-accent-text);
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        font-size: 0.7rem;
        font-weight: 600;
    }}

    /* ------------------------------------------------------------
       Buttons -- primary "Run Analysis" action gets the green accent;
       everything else stays flat/neutral
       ------------------------------------------------------------ */
    .stButton > button {{
        font-family: var(--ppl-font-sans);
        border-radius: 8px;
        border: 1px solid var(--ppl-border);
        background-color: var(--ppl-bg-container);
        color: var(--ppl-text);
        box-shadow: var(--ppl-shadow);
        transition: filter 0.15s ease;
    }}

    .stButton > button:hover {{
        filter: brightness(0.97);
        border-color: var(--ppl-accent);
    }}

    .stButton > button[kind="primary"] {{
        background-color: var(--ppl-accent);
        color: var(--ppl-accent-text);
        border: 1px solid var(--ppl-accent);
        font-weight: 600;
    }}

    .stButton > button[kind="primary"]:hover {{
        filter: brightness(1.08);
    }}

    /* ------------------------------------------------------------
       Tabs (div7) -- flat underline style, accent on active tab
       ------------------------------------------------------------ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        border-bottom: 1px solid var(--ppl-border);
    }}

    .stTabs [data-baseweb="tab"] {{
        font-family: var(--ppl-font-sans);
        font-weight: 500;
        color: var(--ppl-text-muted);
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--ppl-accent) !important;
        border-bottom: 2px solid var(--ppl-accent);
    }}

    /* ------------------------------------------------------------
       Inputs -- selects, radios, sliders, text areas
       ------------------------------------------------------------ */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {{
        font-family: var(--ppl-font-sans);
        background-color: var(--ppl-bg-container);
        border: 1px solid var(--ppl-border);
        border-radius: 8px;
        color: var(--ppl-text);
    }}

    .stTextArea textarea {{
        font-family: var(--ppl-font-mono) !important;
        background-color: var(--ppl-bg-container-alt);
        border: 1px solid var(--ppl-border);
        border-radius: 8px;
        color: var(--ppl-text);
    }}

    /* Radio pills -- used for PPL concept selectors instead of checkboxes */
    div[role="radiogroup"] {{
        gap: 0.35rem;
    }}

    div[role="radiogroup"] label {{
        background-color: var(--ppl-bg-container-alt);
        border: 1px solid var(--ppl-border);
        border-radius: 999px;
        padding: 0.3rem 0.8rem;
        font-size: 0.85rem;
        transition: border-color 0.15s ease;
    }}

    /* Sliders */
    .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background-color: var(--ppl-accent);
    }}

    /* ------------------------------------------------------------
       Code blocks / outputs (st.code) -- always monospace
       ------------------------------------------------------------ */
    .stCodeBlock, code, pre {{
        font-family: var(--ppl-font-mono) !important;
    }}

    /* ------------------------------------------------------------
       Native sidebar de-emphasis -- we are moving away from
       st.sidebar as the primary control surface, but if any native
       sidebar element remains mounted, keep it visually consistent
       rather than leaving Streamlit's default theme colors showing.
       ------------------------------------------------------------ */
    section[data-testid="stSidebar"] {{
        background-color: var(--ppl-bg-container);
        border-right: 1px solid var(--ppl-border);
    }}

    /* ------------------------------------------------------------
       Status/alert boxes -- flatten Streamlit's default gradients
       ------------------------------------------------------------ */
    div[data-testid="stAlert"] {{
        border-radius: 8px;
        box-shadow: var(--ppl-shadow);
        border: 1px solid var(--ppl-border);
    }}
    </style>
    """


def section_label(text: str) -> None:
    """Render a small uppercase section label using the design system.

    Convenience helper so callers don't need to remember the CSS class
    name for this repeated pattern (e.g. "LANGUAGES", "BENCHMARK
    PRESET" headings in the rails).

    Args:
        text: The label text, rendered as-is (already-uppercase looks
            best given the CSS applies letter-spacing/uppercase styling
            on top, but mixed case also works).
    """
    st.markdown(f'<div class="ppl-section-label">{text}</div>', unsafe_allow_html=True)


def badge(text: str) -> str:
    """Return an inline HTML badge span styled with the accent color.

    Args:
        text: Badge text (e.g. "AST", "REGEX", "TIMEOUT").

    Returns:
        An HTML string. Caller is responsible for rendering it via
        `st.markdown(..., unsafe_allow_html=True)`, typically combined
        with surrounding text in one markdown call.
    """
    return f'<span class="ppl-badge">{text}</span>'
