"""RetailPulse — Shared design tokens used across all dashboard views."""

# ── Color palette ─────────────────────────────────────────────────────────────
C = {
    # Brand
    "navy":        "#0F2B4C",   # darkest brand blue — headers, sidebar
    "blue":        "#1D4ED8",   # links, accent highlights
    "teal":        "#0891B2",   # chart primary series

    # Semantic
    "green":       "#059669",   # positive / success
    "amber":       "#D97706",   # warning / reorder trigger
    "red":         "#DC2626",   # danger / stockout / high risk

    # Neutrals — maximum contrast on white/light bg
    "text_h":      "#111827",   # headings: almost black
    "text_b":      "#111827",   # body text: almost black
    "text_sub":    "#1F2937",   # sub-labels: very dark gray
    "text_hint":   "#374151",   # hints / captions: dark gray

    # Backgrounds
    "bg_page":     "#EEF2F7",   # page background
    "bg_card":     "#FFFFFF",   # card surface
    "border":      "#CBD5E1",   # card/table borders
    "bg_subtle":   "#F8FAFC",   # subtle alternating row tint
}

# ── Chart template ────────────────────────────────────────────────────────────
LAYOUT = dict(
    template="plotly_white",
    font=dict(
        family="Inter, Helvetica Neue, Arial, sans-serif",
        size=13,
        color="#111827",
    ),
    title_font=dict(size=15, color="#111827", family="Inter, sans-serif"),
    margin=dict(l=12, r=12, t=44, b=12),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    hoverlabel=dict(
        bgcolor="#FFFFFF",
        font_color="#111827",
        font_size=12,
        bordercolor="#CBD5E1",
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#E2E8F0",
        gridwidth=1,
        linecolor="#CBD5E1",
        tickfont=dict(color="#111827", size=11),
        title_font=dict(color="#111827", size=13, family="Inter"),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#E2E8F0",
        gridwidth=1,
        linecolor="#CBD5E1",
        tickfont=dict(color="#111827", size=11),
        title_font=dict(color="#111827", size=13, family="Inter"),
    ),
    legend=dict(
        font=dict(color="#111827", size=12),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#CBD5E1",
        borderwidth=1,
    ),
)

# ── Reusable card component ───────────────────────────────────────────────────
def kpi_card(col, label, value, sub="", value_color=None):
    """Render a KPI card in the given Streamlit column."""
    import streamlit as st
    v_color = value_color or "#111827"
    col.markdown(f"""
    <div style="
      background:#FFFFFF;
      border:1px solid #CBD5E1;
      border-radius:10px;
      padding:20px 14px;
      text-align:center;
      box-shadow:0 1px 4px rgba(15,23,42,0.07);
    ">
      <div style="
        font-size:0.7rem;
        font-weight:700;
        color:#374151;
        text-transform:uppercase;
        letter-spacing:0.07em;
        margin-bottom:8px;
      ">{label}</div>
      <div style="
        font-size:1.75rem;
        font-weight:700;
        color:{v_color};
        line-height:1.1;
        margin-bottom:5px;
      ">{value}</div>
      <div style="
        font-size:0.78rem;
        color:#4B5563;
        font-weight:500;
      ">{sub}</div>
    </div>""", unsafe_allow_html=True)


def page_header(module_num, title, subtitle):
    """Render the top dark banner for each page."""
    import streamlit as st
    st.markdown(f"""
    <div style="
      background:linear-gradient(135deg, #0F2B4C 0%, #1A3D6B 100%);
      border-radius:12px;
      padding:26px 32px;
      margin-bottom:28px;
      box-shadow:0 2px 8px rgba(15,23,42,0.15);
    ">
      <div style="
        color:rgba(203,213,225,0.9);
        font-size:0.72rem;
        font-weight:700;
        letter-spacing:0.12em;
        text-transform:uppercase;
        margin-bottom:6px;
      ">Module {module_num} of 4</div>
      <div style="
        color:#FFFFFF;
        font-size:1.75rem;
        font-weight:700;
        letter-spacing:-0.01em;
        margin-bottom:4px;
      ">{title}</div>
      <div style="
        color:#CBD5E1;
        font-size:0.88rem;
        font-weight:400;
      ">{subtitle}</div>
    </div>""", unsafe_allow_html=True)


def section_title(text):
    """Render a section subheading with high contrast."""
    import streamlit as st
    st.markdown(f"""
    <div style="
      font-size:0.95rem;
      font-weight:700;
      color:#111827;
      margin:8px 0 12px 0;
      padding-bottom:6px;
      border-bottom:2px solid #E2E8F0;
      letter-spacing:-0.01em;
    ">{text}</div>""", unsafe_allow_html=True)
