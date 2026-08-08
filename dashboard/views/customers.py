"""RetailPulse — Customer Intelligence."""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from views.design import C, LAYOUT, kpi_card, page_header, section_title

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

SEG_COLORS = {
    "Champions":          C["navy"],
    "Loyal":              "#7C3AED",
    "Potential Loyalists": C["teal"],
    "Need Attention":     "#F59E0B",
    "At Risk":            C["amber"],
    "Dormant":            "#94A3B8",
}

RISK_COLORS = {
    "High Risk":   C["red"],
    "Medium Risk": C["amber"],
    "Low Risk":    C["green"],
}


def render():
    page_header("2", "Customer Intelligence",
                "RFM segmentation, behavioral clustering, and churn risk profiling.")

    segments = pd.read_csv(os.path.join(DATA_DIR, "customer_segments.csv"))
    churn_path = os.path.join(DATA_DIR, "customer_churn.csv")
    churn = pd.read_csv(churn_path) if os.path.exists(churn_path) else None

    total     = len(segments)
    avg_mon   = segments["monetary"].mean()
    avg_freq  = segments["frequency"].mean()
    avg_rec   = segments["recency"].mean()
    high_risk = len(churn[churn["churn_risk"] == "High Risk"]) if churn is not None else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Total Customers",    f"{total:,}",           "Unique buyer IDs")
    kpi_card(c2, "Avg Lifetime Value", f"£{avg_mon:,.0f}",     "Monetary (RFM)")
    kpi_card(c3, "Avg Order Frequency",f"{avg_freq:.1f}",      "Orders per customer")
    kpi_card(c4, "Avg Recency",        f"{avg_rec:.0f} days",  "Days since last order")
    kpi_card(c5, "High-Risk Churners", f"{high_risk:,}",       "Need intervention",
             value_color=C["red"])

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Segmentation & RFM distribution ───────────────────────────────────────
    l, r = st.columns(2)

    with l:
        section_title("Customer Segments — RFM Score-Based (6 tiers)")
        seg_counts = segments["kmeans_label"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Customers"]
        fig = go.Figure(go.Pie(
            labels=seg_counts["Segment"],
            values=seg_counts["Customers"],
            hole=0.52,
            marker=dict(
                colors=[SEG_COLORS.get(s, "#94A3B8") for s in seg_counts["Segment"]],
                line=dict(color="white", width=2.5),
            ),
            textfont=dict(color="#111827", size=11),
            hovertemplate="<b>%{label}</b><br>%{value:,} customers (%{percent})<extra></extra>",
        ))
        fig.update_layout(**{**LAYOUT, "height": 360, "showlegend": True,
                              "legend": dict(
                                  font=dict(color="#111827", size=11),
                                  orientation="v", x=1.02, y=0.5,
                              )})
        st.plotly_chart(fig, use_container_width=True)

    with r:
        section_title("RFM Score Distribution (Scale 3–15)")
        fig2 = go.Figure(go.Histogram(
            x=segments["rfm_score"], nbinsx=13,
            marker=dict(color=C["teal"], line=dict(color="white", width=1.5)),
            hovertemplate="Score: %{x}<br>Customers: %{y}<extra></extra>",
        ))
        fig2.update_layout(**{**LAYOUT, "height": 360,
                               "xaxis_title": "RFM Score",
                               "yaxis_title": "Number of Customers"})
        st.plotly_chart(fig2, use_container_width=True)

    # ── RFM scatter ───────────────────────────────────────────────────────────
    section_title("RFM Analysis — Recency vs. Monetary Value (bubble size = order frequency)")
    fig3 = px.scatter(
        segments, x="recency", y="monetary", color="kmeans_label",
        size="frequency", size_max=16, opacity=0.70,
        color_discrete_map=SEG_COLORS,
        labels={"recency":     "Recency (days since last purchase)",
                "monetary":    "Monetary Value (£)",
                "kmeans_label":"Segment",
                "frequency":   "Orders"},
    )
    fig3.update_traces(marker=dict(line=dict(width=0.5, color="white")))
    fig3.update_layout(**{**LAYOUT, "height": 420,
                           "legend": dict(
                               orientation="h", yanchor="bottom", y=1.02,
                               font=dict(color="#111827", size=12),
                           )})
    st.plotly_chart(fig3, use_container_width=True)

    # ── Segment table ─────────────────────────────────────────────────────────
    section_title("Segment Profile Summary")
    summary = segments.groupby("kmeans_label").agg(
        Customers=("Customer ID", "count"),
        Avg_Recency=("recency", "mean"),
        Avg_Orders=("frequency", "mean"),
        Avg_Spend=("monetary", "mean"),
        Avg_RFM=("rfm_score", "mean"),
    ).round(1).sort_values("Avg_Spend", ascending=False)
    summary.index.name = "Segment"
    summary.columns = ["Customers", "Avg Recency (days)", "Avg Orders", "Avg Spend (£)", "Avg RFM Score"]
    st.dataframe(summary.style.background_gradient(subset=["Avg Spend (£)"], cmap="Blues"),
                 use_container_width=True)

    # ── Export button ─────────────────────────────────────────────────────────
    st.download_button(
        label="Export Segment Data (CSV)",
        data=segments.to_csv(index=False),
        file_name="customer_segments_export.csv",
        mime="text/csv",
    )

    # ── Churn analysis ────────────────────────────────────────────────────────
    if churn is not None:
        st.markdown("---")
        section_title("Churn Risk Analysis")

        cl, cr = st.columns(2)
        with cl:
            risk_counts = churn["churn_risk"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Customers"]
            fig4 = go.Figure(go.Bar(
                x=risk_counts["Risk Level"],
                y=risk_counts["Customers"],
                marker_color=[RISK_COLORS.get(r, "#94A3B8") for r in risk_counts["Risk Level"]],
                text=risk_counts["Customers"].apply(lambda v: f"{v:,}"),
                textposition="outside",
                textfont=dict(color="#111827", size=12),
            ))
            fig4.update_layout(**{**LAYOUT, "height": 320, "showlegend": False,
                                   "yaxis_title": "Customers",
                                   "title": "Customers by Risk Tier"})
            st.plotly_chart(fig4, use_container_width=True)

        with cr:
            fig5 = go.Figure(go.Histogram(
                x=churn["churn_probability"], nbinsx=30,
                marker=dict(color=C["red"], line=dict(color="white", width=1)),
                hovertemplate="Probability: %{x:.2f}<br>Customers: %{y}<extra></extra>",
            ))
            fig5.update_layout(**{**LAYOUT, "height": 320,
                                   "xaxis_title": "Churn Probability",
                                   "yaxis_title": "Customers",
                                   "title": "Churn Probability Distribution"})
            st.plotly_chart(fig5, use_container_width=True)

        section_title("Top 15 Highest-Risk Customers")
        top_risk = (churn[churn["churn_risk"] == "High Risk"]
                    .nlargest(15, "churn_probability")
                    [["Customer ID", "recency", "frequency", "monetary",
                      "churn_probability", "churn_risk"]]
                    .reset_index(drop=True))
        top_risk.columns = ["Customer ID", "Recency (days)", "Orders",
                             "Spend (£)", "Churn Probability", "Risk Level"]
        st.dataframe(
            top_risk.style.background_gradient(subset=["Churn Probability"], cmap="Reds"),
            use_container_width=True,
        )

        st.download_button(
            label="Export Churn Data (CSV)",
            data=churn.to_csv(index=False),
            file_name="churn_analysis_export.csv",
            mime="text/csv",
        )
