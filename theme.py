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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

/* -------------------------------------------------------------
   BACKGROUND LAYER -- carefully separated so nothing collides.
   Rupee watermark: small, top-right corner, quiet.
   Monument: anchored strictly to the bottom edge, like a skyline.
   Pillars / circuit: far corners, low opacity, out of text's way.
   ------------------------------------------------------------- */
.rupee-watermark {{
    position: fixed; top: 60px; right: 40px;
    font-size: 220px; font-weight: 900; font-family: 'Playfair Display', Georgia, serif;
    color: rgba(201,162,39,0.07); z-index: 0; pointer-events: none; line-height: 1;
}}
.monument-bg {{
    position: fixed; bottom: -10px; right: -20px; left: auto; transform: none;
    width: 620px; max-width: 70vw; z-index: 0; opacity: 0.14; pointer-events: none;
}}
.monument-bg svg {{ width: 100%; height: auto; display: block; }}
.pillars-bg {{
    position: fixed; bottom: 0; left: -10px; width: 190px; z-index: 0; opacity: 0.10; pointer-events: none;
}}
.circuit-bg {{
    position: fixed; top: 90px; left: -20px; width: 220px; z-index: 0; opacity: 0.10; pointer-events: none;
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

/* -------------------------------------------------------------
   TYPOGRAPHY -- real fonts, proper hierarchy, higher legibility
   ------------------------------------------------------------- */
html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, sans-serif; }}

h1 {{
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #FFFCF3 !important; font-weight: 700 !important;
    letter-spacing: 0.3px !important; text-shadow: 0 2px 6px rgba(0,0,0,0.35);
}}
h2, h3 {{
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #FFFCF3 !important; font-weight: 600 !important;
    letter-spacing: 0.2px !important;
}}
p, span, div, label {{ letter-spacing: 0.1px; }}
[data-testid="stCaptionContainer"] {{ color: #E3DCC5 !important; font-size: 13.5px !important; line-height: 1.6 !important; }}

/* -------------------------------------------------------------
   CONTENT LAYER -- Streamlit's own containers, made translucent
   so the background shows through, with consistent card styling
   ------------------------------------------------------------- */
[data-testid="stAppViewContainer"] > .main {{ background: transparent; }}
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMetric"] {{
    background: rgba(110,104,79,0.90) !important;
    border: 1.5px solid rgba(201,162,39,0.5) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.22) !important;
}}
[data-testid="stMetric"] {{ padding: 16px 18px !important; }}
[data-testid="stMetricLabel"] {{
    color: #E3DCC5 !important; font-weight: 600 !important; letter-spacing: 0.6px !important;
    font-size: 11.5px !important; text-transform: uppercase !important;
}}
[data-testid="stMetricValue"] {{
    color: #FFFCF3 !important; font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    font-weight: 600 !important;
}}

/* dataframes / tables */
[data-testid="stDataFrame"] {{ border: 1.5px solid rgba(201,162,39,0.4) !important; border-radius: 10px !important; overflow: hidden; }}

/* dividers -> dashed gold rule instead of plain grey hr */
hr {{ border: none !important; border-top: 1.5px dashed rgba(201,162,39,0.5) !important; margin: 24px 0 !important; }}

/* buttons + inputs styled to match, consistent radius/weight throughout */
.stButton > button {{
    background: linear-gradient(160deg, #7A7457 0%, #625C46 100%) !important;
    color: #FFFCF3 !important; border: 1.5px solid #C9A227 !important; border-radius: 8px !important;
    font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}}
.stTextInput > div > div > input {{
    background: rgba(0,0,0,0.22) !important; color: #F5F1E8 !important;
    border: 1.5px solid rgba(201,162,39,0.5) !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}}

/* chip badges for groundedness / retrieval-mode indicators */
.chip {{
    display: inline-flex; align-items: center; gap: 6px; font-family: 'Inter', sans-serif;
    font-size: 12.5px; padding: 6px 15px; border-radius: 20px; font-weight: 600;
    border: 1.5px solid rgba(201,162,39,0.7); background: rgba(201,162,39,0.15); color: #E8C55C;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}}
.chip.good {{ border-color: rgba(95,168,107,0.8); background: rgba(95,168,107,0.15); color: #8FCB9C; }}
.chip.warn {{ border-color: rgba(224,138,111,0.8); background: rgba(224,138,111,0.15); color: #E8A98F; }}

/* the Advisor hero card */
.advisor-eyebrow {{
    font-family: 'Inter', sans-serif; font-size: 11.5px; letter-spacing: 2.4px; color: #E8C55C;
    text-transform: uppercase; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; font-weight: 700;
}}
.advisor-eyebrow::before, .advisor-eyebrow::after {{ content: ""; width: 26px; height: 1.5px; background: rgba(201,162,39,0.7); }}
.advisor-title-row {{ display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }}
.advisor-seal {{
    width: 54px; height: 54px; border-radius: 50%; border: 3px solid #E8C55C;
    display: inline-flex; align-items: center; justify-content: center; font-size: 27px; color: #FFFCF3; font-weight: 900;
    background: radial-gradient(circle, rgba(201,162,39,0.4) 0%, transparent 70%); flex-shrink: 0;
    box-shadow: 0 0 20px rgba(201,162,39,0.3);
}}
.advisor-title {{
    font-size: 28px; color: #FFFCF3; font-weight: 700; font-family: 'Playfair Display', Georgia, serif;
}}
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


# Original banner illustration: a human silhouette and an AI/robot
# silhouette seated at a table, with a small chart panel between them --
# built entirely from primitive shapes, in the same spirit as a
# "financial advisor meets AI" graphic, but not a copy of any specific
# artwork or stock image.
ADVISOR_BANNER_SVG = """
<svg width="900" height="220" viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg">
  <!-- table -->
  <rect x="330" y="150" width="240" height="10" fill="#E8C55C"/>
  <rect x="345" y="160" width="8" height="40" fill="#E8C55C"/>
  <rect x="547" y="160" width="8" height="40" fill="#E8C55C"/>

  <!-- AI / robot figure, left, seated, arm raised toward the chart -->
  <g fill="#E8C55C">
    <circle cx="180" cy="70" r="26"/>
    <rect x="168" y="40" width="5" height="16"/>
    <circle cx="170" cy="38" r="4"/>
    <rect x="160" y="96" width="40" height="55" rx="8"/>
    <rect x="150" y="151" width="22" height="45" rx="5"/>
    <rect x="188" y="151" width="22" height="45" rx="5"/>
    <!-- raised arm pointing toward chart -->
    <rect x="196" y="105" width="70" height="12" rx="6" transform="rotate(-18 196 105)"/>
    <circle cx="270" cy="88" r="8"/>
  </g>

  <!-- human figure, right, seated -->
  <g fill="#F5F1E8" opacity="0.92">
    <circle cx="710" cy="68" r="24"/>
    <path d="M 668 150 Q 668 100 710 98 Q 752 100 752 150 Z"/>
    <rect x="678" y="151" width="20" height="45" rx="5"/>
    <rect x="722" y="151" width="20" height="45" rx="5"/>
    <rect x="655" y="108" width="55" height="12" rx="6" transform="rotate(14 655 108)"/>
  </g>

  <!-- floating chart panel, centered above the table -->
  <g>
    <rect x="360" y="20" width="180" height="110" rx="8" fill="none" stroke="#E8C55C" stroke-width="2.5" opacity="0.85"/>
    <rect x="378" y="88" width="14" height="28" fill="#E8C55C"/>
    <rect x="400" y="70" width="14" height="46" fill="#E8C55C"/>
    <rect x="422" y="55" width="14" height="61" fill="#E8C55C"/>
    <rect x="444" y="76" width="14" height="40" fill="#E8C55C"/>
    <polyline points="378,60 400,45 422,50 444,32 466,38" fill="none" stroke="#8FCB9C" stroke-width="2.5"/>
  </g>
</svg>
"""

BANNER_CSS = """
<style>
.advisor-banner {
    width: 100%; border-radius: 14px; overflow: hidden; margin-bottom: 18px;
    background: linear-gradient(160deg, #7A7457 0%, #625C46 100%);
    border: 1.5px solid rgba(201,162,39,0.55);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    padding: 10px 0;
}
.advisor-banner svg { width: 100%; height: auto; display: block; }
</style>
"""


def banner_html() -> str:
    """A wide illustrated banner (human + AI at a table with a chart) for
    the very top of the page, above the title."""
    return BANNER_CSS + f'<div class="advisor-banner">{ADVISOR_BANNER_SVG}</div>'


def chip_html(label: str, kind: str = "") -> str:
    """kind: '' (neutral gold), 'good' (green), or 'warn' (rust)."""
    cls = f"chip {kind}".strip()
    return f'<span class="{cls}">{label}</span>'
