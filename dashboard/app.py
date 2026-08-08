"""RetailPulse Analytics — Main Entry Point."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="RetailPulse Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* ── Base ── */
  html, body, .stApp {
    background: #EEF2F7;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #0F172A;
  }

  .block-container {
    padding: 1.75rem 2rem 3rem 2rem;
    max-width: 1440px;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F2B4C 0%, #1A3D6B 100%);
    border-right: none;
  }

  /* Sidebar ALL text visible on dark background */
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div,
  [data-testid="stSidebar"] label {
    color: #CBD5E1 !important;
  }

  /* Radio buttons — clear white text */
  [data-testid="stSidebar"] [data-testid="stRadio"] label span {
    color: #F1F5F9 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
  }

  /* Selected radio item */
  [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
  }

  /* ── Headings in main content ── */
  h1, h2, h3, h4 {
    color: #0F172A !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
  }

  /* ── Streamlit native metric ── */
  [data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
  }
  [data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* ── Divider ── */
  hr { border-color: #CBD5E1 !important; }

  /* ── Tables / DataFrames ── */
  .stDataFrame { border-radius: 10px; overflow: hidden; }

  /* ── Hide Streamlit chrome ── */
  footer, #MainMenu, header { visibility: hidden; }

  /* ── Plotly chart containers ── */
  .js-plotly-plot { border-radius: 10px; }

  /* ── Slider label ── */
  [data-testid="stSlider"] label {
    color: #1E293B !important;
    font-weight: 600 !important;
  }

  /* ── All widget labels high contrast ── */
  .stSelectbox label, .stMultiSelect label, .stTextInput label,
  .stNumberInput label, .stTextArea label, .stDateInput label,
  .stCheckbox label, .stRadio label {
    color: #1E293B !important;
    font-weight: 600 !important;
  }

  /* ── Download buttons ── */
  .stDownloadButton button {
    color: #1E293B !important;
    font-weight: 600 !important;
    border: 1px solid #CBD5E1 !important;
    background: #FFFFFF !important;
  }
  .stDownloadButton button:hover {
    background: #F1F5F9 !important;
    border-color: #0891B2 !important;
    color: #0891B2 !important;
  }

  /* ── Markdown text always dark ── */
  .stMarkdown p, .stMarkdown li, .stMarkdown span {
    color: #1E293B;
  }

  /* ── Tab widget labels ── */
  .stTabs [data-baseweb="tab"] {
    color: #334155 !important;
    font-weight: 600 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Sidebar branding ──────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:12px 0 18px 0;border-bottom:1px solid rgba(255,255,255,0.12);margin-bottom:16px;">
  <div style="color:#FFFFFF;font-size:1.25rem;font-weight:700;letter-spacing:-0.01em;">
    RetailPulse
  </div>
  <div style="color:#94A3B8;font-size:0.72rem;margin-top:3px;
              text-transform:uppercase;letter-spacing:0.1em;font-weight:500;">
    Analytics Platform
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div style="color:#94A3B8;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:8px;">Modules</div>', unsafe_allow_html=True)

page = st.sidebar.radio(
    label="Navigation",
    options=[
        "Executive Sales Summary",
        "Customer Intelligence",
        "Demand Forecasting",
        "Inventory Optimization",
    ],
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("""
<div style="margin-top:32px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.10);">
  <div style="color:#64748B;font-size:0.7rem;line-height:1.8;">
    <div style="color:#94A3B8;font-size:0.68rem;text-transform:uppercase;
                letter-spacing:0.08em;font-weight:600;margin-bottom:6px;">Dataset</div>
    Online Retail II<br>
    <span style="color:#CBD5E1;">UCI ML Repository</span><br><br>
    <div style="color:#94A3B8;font-size:0.68rem;text-transform:uppercase;
                letter-spacing:0.08em;font-weight:600;margin-bottom:6px;">Coverage</div>
    Dec 2009 – Dec 2011<br>
    <span style="color:#CBD5E1;">1,033,034 transactions</span><br>
    <span style="color:#CBD5E1;">5,878 unique customers</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Page routing ─────────────────────────────────────────────────────────────
if page == "Executive Sales Summary":
    from views import sales;     sales.render()
elif page == "Customer Intelligence":
    from views import customers; customers.render()
elif page == "Demand Forecasting":
    from views import forecast;  forecast.render()
elif page == "Inventory Optimization":
    from views import inventory; inventory.render()
