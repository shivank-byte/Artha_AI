"""
theme.py
"Stone Grey" theme for the AI Inflation Advisor dashboard -- inspired by
the RBI Rs.500 note's color palette (officially named "Stone Grey" by RBI)
and general banknote design language: security threads, a denomination-style
corner box, guilloche-style fine linework, and an original hand-drawn
monument silhouette (built from primitive shapes, not traced from any
photo or the currency's own artwork -- see MONUMENT_SVG below).

No portrait, official emblem, or currency security-feature wording is
reproduced -- only the color palette and generic design *language* of a
banknote, which are not protected in the way a specific security document's
artwork and printed text are.

Usage: call inject_theme() once, near the top of app.py, right after
st.set_page_config().
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Original hand-drawn monument silhouette (dome, chhatris, crenellated wall,
# arched niches -- built from basic shapes, not a copy of any photo/artwork)
# ---------------------------------------------------------------------------
MONUMENT_SVG = """
<svg width="780" height="280" viewBox="0 0 700 280" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="150" width="700" height="130" fill="#C9A227"/>
  """ + "".join([f'<rect x="{x}" y="130" width="18" height="22" fill="#C9A227"/>' for x in range(10, 690, 34)]) + """
  <rect x="60" y="90" width="50" height="60" fill="#C9A227"/>
  <circle cx="85" cy="80" r="26" fill="#C9A227"/>
  <rect x="82" y="45" width="6" height="20" fill="#C9A227"/>
  <circle cx="85" cy="42" r="5" fill="#C9A227"/>
  <rect x="590" y="90" width="50" height="60" fill="#C9A227"/>
  <circle cx="615" cy="80" r="26" fill="#C9A227"/>
  <rect x="612" y="45" width="6" height="20" fill="#C9A227"/>
  <circle cx="615" cy="42" r="5" fill="#C9A227"/>
  <rect x="290" y="60" width="120" height="120" fill="#C9A227"/>
  <path d="M 290 60 Q 350 10 410 60 Z" fill="#C9A227"/>
  <circle cx="350" cy="30" r="34" fill="#C9A227"/>
  <rect x="345" y="-10" width="10" height="26" fill="#C9A227"/>
  <circle cx="350" cy="-14" r="7" fill="#C9A227"/>
  <circle cx="300" cy="55" r="16" fill="#C9A227"/>
  <circle cx="400" cy="55" r="16" fill="#C9A227"/>
  <path d="M 325 180 L 325 130 Q 350 100 375 130 L 375 180 Z" fill="#5C574C"/>
  """ + "".join([f'<path d="M {x} 180 L {x} 158 Q {x+12} 145 {x+24} 158 L {x+24} 180 Z" fill="#5C574C"/>'
                  for x in list(range(140, 280, 45)) + list(range(420, 570, 45))]) + """
</svg>
"""

# Original abstract "classical banking" motif -- a pediment (triangular roof)
# over evenly spaced columns, the generic architectural language of banks
# and treasuries worldwide, not any specific building or logo.
PILLARS_SVG = """
<svg width="260" height="180" viewBox="0 0 260 180" xmlns="http://www.w3.org/2000/svg">
  <polygon points="10,60 130,10 250,60" fill="#C9A227"/>
  <rect x="15" y="60" width="230" height="10" fill="#C9A227"/>
  """ + "".join([f'<rect x="{x}" y="75" width="16" height="95" fill="#C9A227"/>' for x in range(25, 240, 34)]) + """
  <rect x="10" y="170" width="240" height="10" fill="#C9A227"/>
</svg>
"""

# Original abstract "AI" motif -- nodes connected by lines, the generic
# visual language of a neural network / circuit, not any specific logo.
CIRCUIT_SVG = """
<svg width="280" height="220" viewBox="0 0 280 220" xmlns="http://www.w3.org/2000/svg">
  <g stroke="#C9A227" stroke-width="2" fill="none">
    <line x1="40" y1="40" x2="140" y2="90"/>
    <line x1="140" y1="90" x2="240" y2="50"/>
    <line x1="140" y1="90" x2="100" y2="170"/>
    <line x1="140" y1="90" x2="210" y2="160"/>
    <line x1="40" y1="40" x2="40" y2="130"/>
    <line x1="40" y1="130" x2="100" y2="170"/>
    <line x1="210" y1="160" x2="240" y2="50"/>
  </g>
  <g fill="#C9A227">
    <circle cx="40" cy="40" r="9"/>
    <circle cx="140" cy="90" r="12"/>
    <circle cx="240" cy="50" r="9"/>
    <circle cx="40" cy="130" r="8"/>
    <circle cx="100" cy="170" r="9"/>
    <circle cx="210" cy="160" r="8"/>
  </g>
</svg>
"""

THEME_CSS = f"""
<style>
/* huge ghost rupee watermark, centered */
.rupee-watermark {{
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    font-size: 520px; font-weight: 900; font-family: Georgia, serif;
    color: rgba(201,162,39,0.10); z-index: 0; pointer-events: none; line-height: 1;
}}

/* fixed, centered, full-page monument watermark -- sits behind everything */
.monument-bg {{
    position: fixed; top: 62%; left: 50%; transform: translate(-50%, -50%);
    width: 780px; z-index: 0; opacity: 0.18; pointer-events: none;
}}
.monument-bg svg {{ width: 100%; height: auto; }}

/* original abstract banking-pillar motif, bottom-left */
.pillars-bg {{
    position: fixed; bottom: 0; left: 0; width: 260px; z-index: 0; opacity: 0.14; pointer-events: none;
}}

/* original abstract AI circuit-node motif, top-right */
.circuit-bg {{
    position: fixed; top: 0; right: 0; width: 280px; z-index: 0; opacity: 0.14; pointer-events: none;
}}

/* dual gold+green security thread down the left margin */
.thread-gold {{
    position: fixed; top: 0; left: 10px; width: 3px; height: 100%;
    background: repeating-linear-gradient(180deg, #C9A227 0, #C9A227 5px, transparent 5px, transparent 11px);
    opacity: 0.6; z-index: 0; pointer-events: none;
}}
.thread-green {{
    position: fixed; top: 0; left: 18px; width: 3px; height: 100%;
    background: repeating-linear-gradient(180deg, #5FA86B 0, #5FA86B 5px, transparent 5px, transparent 11px);
    opacity: 0.5; z-index: 0; pointer-events: none;
}}

/* guilloche-style strip along the very top of the page */
.guilloche-top {{
    position: fixed; top: 0; left: 0; width: 100%; height: 8px;
    background: repeating-linear-gradient(90deg, #C9A227 0px, transparent 1.5px, transparent 4px, #C9A227 5.5px);
    opacity: 0.55; z-index: 999; pointer-events: none;
}}

/* let the monument show through: make Streamlit's own containers translucent */
[data-testid="stAppViewContainer"] > .main {{ background: transparent; }}
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMetric"] {{
    background: rgba(110,104,79,0.82) !important;
    border: 1.5px solid rgba(201,162,39,0.5) !important;
    border-radius: 10px !important;
}}
[data-testid="stMetric"] {{ padding: 14px 16px !important; }}
[data-testid="stMetricLabel"] {{ color: #D9D2BF !important; font-weight: 600; letter-spacing: 0.5px; }}
[data-testid="stMetricValue"] {{ color: #FFFCF3 !important; font-family: 'Courier New', monospace !important; }}

/* headers in a serif face, evoking engraved currency typography */
h1, h2, h3 {{ font-family: Georgia, 'Times New Roman', serif !important; color: #FFFCF3 !important; }}

/* dividers -> dashed gold rule instead of plain grey hr */
hr {{ border: none !important; border-top: 1.5px dashed rgba(201,162,39,0.5) !important; margin: 22px 0 !important; }}

/* buttons + inputs styled to match */
.stButton > button {{
    background: linear-gradient(160deg, #7A7457 0%, #625C46 100%) !important;
    color: #FFFCF3 !important; border: 1.5px solid #C9A227 !important; border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stTextInput > div > div > input {{
    background: rgba(0,0,0,0.2) !important; color: #F5F1E8 !important;
    border: 1.5px solid rgba(201,162,39,0.5) !important; border-radius: 8px !important;
}}

/* chip badges for groundedness / retrieval-mode indicators */
.chip {{
    display: inline-flex; align-items: center; gap: 6px; font-family: Arial, sans-serif;
    font-size: 12.5px; padding: 5px 14px; border-radius: 20px; font-weight: 600;
    border: 1.5px solid rgba(201,162,39,0.7); background: rgba(201,162,39,0.15); color: #E8C55C;
}}
.chip.good {{ border-color: rgba(95,168,107,0.8); background: rgba(95,168,107,0.15); color: #8FCB9C; }}
.chip.warn {{ border-color: rgba(224,138,111,0.8); background: rgba(224,138,111,0.15); color: #E8A98F; }}

/* the Advisor hero card */
.advisor-eyebrow {{
    font-family: Arial, sans-serif; font-size: 11px; letter-spacing: 2.2px; color: #E8C55C;
    text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; font-weight: 700;
}}
.advisor-eyebrow::before, .advisor-eyebrow::after {{ content: ""; width: 24px; height: 1.5px; background: rgba(201,162,39,0.7); }}
.advisor-title-row {{ display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }}
.advisor-seal {{
    width: 52px; height: 52px; border-radius: 50%; border: 3px solid #E8C55C;
    display: inline-flex; align-items: center; justify-content: center; font-size: 26px; color: #FFFCF3; font-weight: 900;
    background: radial-gradient(circle, rgba(201,162,39,0.4) 0%, transparent 70%); flex-shrink: 0;
}}
.advisor-title {{ font-size: 27px; color: #FFFCF3; font-weight: 700; font-family: Georgia, serif; }}
</style>
"""

BACKGROUND_LAYER_HTML = f"""
<div class="guilloche-top"></div>
<div class="thread-gold"></div>
<div class="thread-green"></div>
<div class="rupee-watermark">&#8377;</div>
<div class="monument-bg">{MONUMENT_SVG}</div>
<div class="pillars-bg">{PILLARS_SVG}</div>
<div class="circuit-bg">{CIRCUIT_SVG}</div>
"""


def inject_theme():
    """Call once near the top of app.py, right after st.set_page_config()."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown(BACKGROUND_LAYER_HTML, unsafe_allow_html=True)


def advisor_header_html() -> str:
    """The eyebrow + seal + title block for the 'Ask the AI Advisor'
    section -- a single self-contained HTML snippet (safe to render with
    st.markdown), since Streamlit doesn't allow wrapping native widgets
    inside custom HTML containers."""
    return """
    <div class="advisor-eyebrow">AI-Powered &middot; RAG-Grounded</div>
    <div class="advisor-title-row">
        <div class="advisor-seal">&#8377;</div>
        <div class="advisor-title">Ask the AI Advisor</div>
    </div>
    """


def chip_html(label: str, kind: str = "") -> str:
    """kind: '' (neutral gold), 'good' (green), or 'warn' (rust)."""
    cls = f"chip {kind}".strip()
    return f'<span class="{cls}">{label}</span>'
