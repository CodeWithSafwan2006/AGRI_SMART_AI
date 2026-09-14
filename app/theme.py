"""AgriSmart visual tokens & modern luxury agricultural theme matching Lovable design system."""

import streamlit as st

# Organic Forest & Warm Cream Palette
BG_CREAM = "#f4f3eb"
FOREST_DARK = "#1f4e23"
FOREST_DEEP = "#112316"
SAGE_SOFT = "#dce6d6"
SAGE_DROPZONE = "#eef3ea"
CARD_BEIGE = "#ebe9de"
BORDER_MUTED = "#e1ded0"
TEXT_PRIMARY = "#1a2b1c"
TEXT_MUTED = "#626d63"
TEXT_LIGHT = "#f7f5f0"
TEXT_SAGE = "#a3b8a6"
ACCENT_GREEN = "#234927"

FONT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,600&"
    "family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
)


def inject_theme():
    st.markdown(
        f"""
<link href="{FONT_URL}" rel="stylesheet">
<style>
  :root {{
    --bg-cream: {BG_CREAM};
    --forest-dark: {FOREST_DARK};
    --forest-deep: {FOREST_DEEP};
    --sage-soft: {SAGE_SOFT};
    --card-beige: {CARD_BEIGE};
    --border-muted: {BORDER_MUTED};
    --text-primary: {TEXT_PRIMARY};
    --text-muted: {TEXT_MUTED};
    --text-light: {TEXT_LIGHT};
    --text-sage: {TEXT_SAGE};
  }}

  /* App Canvas */
  .stApp {{
    background-color: var(--bg-cream) !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }}

  /* Hide default streamlit chrome */
  #MainMenu, footer, header {{ visibility: hidden; height: 0; }}
  .block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
  }}

  /* Top Navigation Bar */
  .agri-nav-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.25rem;
    background: #f4f3eb;
    border-bottom: 1px solid var(--border-muted);
    margin-bottom: 1.5rem;
    border-radius: 12px;
  }}
  .agri-brand {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }}
  .agri-brand-icon {{
    background: var(--forest-dark);
    color: white;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
  }}
  .agri-brand-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
  }}
  .agri-brand-sub {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    text-transform: uppercase;
  }}
  .agri-nav-right {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
  }}
  .agri-status-pill {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    background: #e7e5d8;
    color: var(--forest-dark);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
  }}
  .agri-status-dot {{
    width: 7px;
    height: 7px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #10b981;
  }}
  .agri-user-pill {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #ffffff;
    border: 1px solid var(--border-muted);
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-primary);
  }}

  /* Typography */
  h1, h2, h3, .serif-heading {{
    font-family: 'Playfair Display', Georgia, serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
  }}
  .section-tag {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--forest-dark);
    text-transform: uppercase;
    margin-bottom: 0.25rem;
  }}
  .hero-tagline {{
    font-size: 1.05rem;
    color: var(--text-muted);
    line-height: 1.5;
  }}

  /* Cards & Panels */
  .agri-card {{
    background: #ffffff;
    border: 1px solid var(--border-muted);
    border-radius: 16px;
    padding: 1.35rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  }}
  .agri-card-sage {{
    background: var(--sage-soft);
    border: 1px solid #cbd8c5;
    border-radius: 16px;
    padding: 1.35rem 1.5rem;
  }}

  /* Dark Advisor Panel */
  .advisor-panel {{
    background: var(--forest-deep);
    color: var(--text-light);
    border-radius: 20px;
    padding: 1.75rem 1.5rem;
    box-shadow: 0 8px 24px rgba(17,35,22,0.12);
  }}
  .advisor-tag {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: #8bb38f;
    text-transform: uppercase;
  }}
  .advisor-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.45rem;
    color: var(--text-light);
    margin: 0.35rem 0 0.85rem 0;
    line-height: 1.25;
  }}
  .advisor-body {{
    color: var(--text-sage);
    font-size: 0.92rem;
    line-height: 1.6;
  }}
  .advisor-body strong {{
    color: #ffffff;
  }}
  .advisor-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.12);
    color: #d1e7d3;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
  }}

  /* Stat / Metrics Grid */
  .metrics-grid-4 {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.25rem 0;
  }}
  .metric-card-clean {{
    background: #ebe9de;
    border: 1px solid var(--border-muted);
    border-radius: 12px;
    padding: 1rem 1.15rem;
  }}
  .metric-card-label {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-transform: uppercase;
  }}
  .metric-card-val {{
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0.2rem 0;
  }}
  .metric-card-sub {{
    font-size: 0.78rem;
    color: var(--text-muted);
  }}

  /* File Uploader */
  div[data-testid="stFileUploader"] section {{
    background: {SAGE_DROPZONE} !important;
    border: 1.5px dashed rgba(31, 78, 35, 0.35) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
  }}

  /* Form Elements & Inputs */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {{
    background-color: #ffffff !important;
    border: 1px solid #dcd9cc !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
  }}
  
  /* Primary Action Buttons */
  .stButton > button {{
    background: var(--forest-dark) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 2px 4px rgba(31, 78, 35, 0.15) !important;
    transition: all 0.15s ease-in-out !important;
  }}
  .stButton > button:hover {{
    background: #173d1b !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(31, 78, 35, 0.2) !important;
  }}

  /* Tab Navigation Styling */
  .stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 1.5rem !important;
    border-bottom: 1px solid var(--border-muted) !important;
    padding-bottom: 0px !important;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 0.5rem !important;
    border: none !important;
  }}
  .stTabs [aria-selected="true"] {{
    color: var(--text-primary) !important;
    border-bottom: 2.5px solid var(--forest-dark) !important;
  }}

  /* Sidebar styling */
  [data-testid="stSidebar"] {{
    background: #ebe9de !important;
    border-right: 1px solid var(--border-muted) !important;
  }}
  [data-testid="stSidebar"] * {{
    color: var(--text-primary) !important;
  }}

  /* Responsive layout tweaks */
  @media (max-width: 900px) {{
    .metrics-grid-4 {{
      grid-template-columns: repeat(2, 1fr);
    }}
  }}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_top_navbar(
    farmer_name: str = "Farmer",
    village: str = "Pune",
    is_authenticated: bool = True,
):
    """Render the top navigation bar matching the Lovable preview design."""
    auth_pill = (
        f"""
        <div class="agri-user-pill">
            <span>👨‍🌾</span>
            <span>{farmer_name} · {village}</span>
        </div>
        """
        if is_authenticated
        else """
        <div class="agri-user-pill">
            <span>👤 Guest Mode</span>
        </div>
        """
    )

    st.markdown(
        f"""
        <div class="agri-nav-container">
          <div class="agri-brand">
            <div class="agri-brand-icon">🌿</div>
            <div>
              <div class="agri-brand-title">AgriSmart</div>
              <div class="agri-brand-sub">Field Intelligence</div>
            </div>
          </div>
          <div class="agri-nav-right">
            <div class="agri-status-pill">
              <span class="agri-status-dot"></span>
              <span>Field Online</span>
            </div>
            {auth_pill}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_header(farmer_name: str = "Farmer"):
    """Render the hero headline."""
    st.markdown(
        f"""
        <div style="margin-bottom: 1.75rem;">
          <div class="section-tag">GOOD MORNING, {farmer_name.upper()}</div>
          <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
            <h1 style="margin: 0; font-size: 2.35rem; line-height: 1.15;">See what your crop is telling you.</h1>
            <p class="hero-tagline" style="margin: 0; max-width: 420px;">Scan a leaf, understand the risk, and take the next right step for your field.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bottom_metrics(
    temp_c: float | None,
    humidity_pct: float | None,
    rain_pct: float | None,
    wind_kmh: float | None,
):
    """Render the 4-card metric grid at the bottom."""
    t_str = f"{temp_c:.0f}°C" if temp_c is not None else "--"
    h_str = f"{humidity_pct:.0f}%" if humidity_pct is not None else "--"
    r_str = f"{rain_pct:.0f}%" if rain_pct is not None else "--"
    w_str = f"{wind_kmh:.1f} km/h" if wind_kmh is not None else "--"

    st.markdown(
        f"""
        <div class="metrics-grid-4">
          <div class="metric-card-clean">
            <div class="metric-card-label">Field Temperature</div>
            <div class="metric-card-val">{t_str}</div>
            <div class="metric-card-sub">Current canopy ambient</div>
          </div>
          <div class="metric-card-clean">
            <div class="metric-card-label">Rain Probability (24h)</div>
            <div class="metric-card-val">{r_str}</div>
            <div class="metric-card-sub">Next 24-hour forecast</div>
          </div>
          <div class="metric-card-clean">
            <div class="metric-card-label">Air Humidity</div>
            <div class="metric-card-val">{h_str}</div>
            <div class="metric-card-sub">Relative leaf moisture</div>
          </div>
          <div class="metric-card-clean">
            <div class="metric-card-label">Wind Speed</div>
            <div class="metric-card-val">{w_str}</div>
            <div class="metric-card-sub">Spray drift assessment</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
