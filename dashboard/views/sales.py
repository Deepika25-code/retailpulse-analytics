"""RetailPulse — Executive Sales Summary."""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from views.design import C, LAYOUT, kpi_card, page_header, section_title

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


def render():
    page_header("1", "Executive Sales Summary",
                "Revenue performance, transaction trends, and day-of-week patterns.")

    daily = pd.read_csv(os.path.join(DATA_DIR, "daily_sales_features.csv"), parse_dates=["Date"])

    total_rev  = daily["total_revenue"].sum()
    total_qty  = int(daily["total_quantity"].sum())
    total_txn  = int(daily["transaction_count"].sum())
    avg_order  = total_rev / total_txn if total_txn > 0 else 0
    avg_daily  = daily["total_revenue"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Total Revenue",       f"£{total_rev:,.0f}",  "All periods combined")
    kpi_card(c2, "Avg Daily Revenue",   f"£{avg_daily:,.0f}",  "Per trading day")
    kpi_card(c3, "Total Units Sold",    f"{total_qty:,}",       "Items dispatched")
    kpi_card(c4, "Total Transactions",  f"{total_txn:,}",       "Unique invoices")
    kpi_card(c5, "Avg Order Value",     f"£{avg_order:,.2f}",  "Revenue per invoice",
             value_color=C["blue"])

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Revenue trend ─────────────────────────────────────────────────────────
    section_title("Revenue Trend with Moving Average")
    ma_window = st.slider("Moving average window (days)", 7, 60, 30, key="s_ma")
    daily["MA"] = daily["total_revenue"].rolling(ma_window).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["total_revenue"],
        mode="lines", name="Daily Revenue",
        line=dict(color="#CBD5E1", width=1),
        fill="tozeroy", fillcolor="rgba(8,145,178,0.05)",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["MA"],
        mode="lines", name=f"{ma_window}-day Moving Avg",
        line=dict(color=C["teal"], width=2.5),
    ))
    layout = {**LAYOUT, "height": 360,
              "xaxis_title": "Date", "yaxis_title": "Revenue (£)",
              "legend": dict(orientation="h", yanchor="bottom", y=1.02,
                             xanchor="right", x=1,
                             font=dict(color="#111827", size=12))}
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    # ── Two columns ───────────────────────────────────────────────────────────
    l, r = st.columns(2)

    with l:
        section_title("Average Revenue by Day of Week")
        dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
        daily["dow_num"] = daily["Date"].dt.dayofweek
        dow = daily.groupby("dow_num")["total_revenue"].mean().reset_index()
        dow["day"] = dow["dow_num"].map(dow_map)
        max_val = dow["total_revenue"].max()
        bar_colors = [C["teal"] if v == max_val else "#94A3B8" for v in dow["total_revenue"]]
        fig2 = go.Figure(go.Bar(
            x=dow["day"], y=dow["total_revenue"],
            marker_color=bar_colors,
            text=dow["total_revenue"].apply(lambda v: f"£{v:,.0f}"),
            textposition="outside",
            textfont=dict(color="#111827", size=11),
        ))
        fig2.update_layout(**{**LAYOUT, "height": 320,
                               "yaxis_title": "Avg Revenue (£)",
                               "showlegend": False})
        st.plotly_chart(fig2, use_container_width=True)

    with r:
        section_title("Monthly Revenue")
        monthly = daily.groupby(daily["Date"].dt.to_period("M"))["total_revenue"].sum().reset_index()
        monthly["Date"] = monthly["Date"].dt.to_timestamp()
        monthly["label"] = monthly["Date"].dt.strftime("%b '%y")
        fig3 = go.Figure(go.Bar(
            x=monthly["label"], y=monthly["total_revenue"],
            marker_color=C["navy"],
            text=monthly["total_revenue"].apply(lambda v: f"£{v/1000:.0f}k"),
            textposition="outside",
            textfont=dict(color="#111827", size=11),
        ))
        fig3.update_layout(**{**LAYOUT, "height": 320,
                               "yaxis_title": "Revenue (£)",
                               "showlegend": False})
        st.plotly_chart(fig3, use_container_width=True)

    # ── Transaction volume ────────────────────────────────────────────────────
    section_title("Daily Transaction Volume")
    fig4 = go.Figure(go.Scatter(
        x=daily["Date"], y=daily["transaction_count"],
        mode="lines", fill="tozeroy",
        line=dict(color=C["green"], width=1.5),
        fillcolor="rgba(5,150,105,0.08)",
        name="Transactions",
    ))
    fig4.update_layout(**{**LAYOUT, "height": 230,
                           "xaxis_title": "Date", "yaxis_title": "No. of Transactions"})
    st.plotly_chart(fig4, use_container_width=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.download_button(
        label="Export Daily Sales Data (CSV)",
        data=daily.to_csv(index=False),
        file_name="daily_sales_export.csv", mime="text/csv",
    )

