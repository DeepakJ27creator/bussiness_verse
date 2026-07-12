"""
BusinessVerse - Page 1: Dashboard
Professional KPI cards, revenue trends, top products, regional breakdown.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from streamlit_app.utils.db_manager import (
    get_kpis, query_monthly_revenue, query_top_products,
    query_region_sales, query_category_performance, query_recent_transactions
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard · BusinessVerse", page_icon="🏠", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------
if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in first.")
    st.stop()

# ---------------------------------------------------------------------------
# Helper: format currency
# ---------------------------------------------------------------------------
def fmt_currency(val: float) -> str:
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:,.2f}"

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class='bv-header'>
    <div>
        <h1>📊 Dashboard</h1>
        <p>Business performance overview · Real-time analytics</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
kpis         = get_kpis()
monthly_rev  = query_monthly_revenue()
top_products = query_top_products(10)
region_sales = query_region_sales()
category_df  = query_category_performance()
recent_tx    = query_recent_transactions(20)

if kpis["total_orders"] == 0:
    st.info("📭 No data found. Please run the data generator first:\n```\npython streamlit_app/utils/data_generator.py\n```")
    st.stop()

# ---------------------------------------------------------------------------
# KPI Cards (row 1)
# ---------------------------------------------------------------------------
st.markdown("### Key Performance Indicators")

kpi_cols = st.columns(4)

kpi_data = [
    ("blue",   "💰", "Total Revenue",   fmt_currency(kpis["total_revenue"]),  "+12.4%"),
    ("green",  "📦", "Total Orders",    f"{kpis['total_orders']:,}",           "+8.1%"),
    ("amber",  "👥", "Total Customers", f"{kpis['total_customers']:,}",        "+5.3%"),
    ("purple", "💹", "Total Profit",    fmt_currency(kpis["total_profit"]),    "+9.7%"),
]

for col, (color, icon, label, value, delta) in zip(kpi_cols, kpi_data):
    with col:
        st.markdown(f"""
        <div class='kpi-card {color}'>
            <div class='kpi-icon'>{icon}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-delta positive'>▲ {delta} vs last period</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: Monthly Revenue Trend + Regional Breakdown
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Monthly Revenue & Profit Trend</div>", unsafe_allow_html=True)

    if not monthly_rev.empty:
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=monthly_rev["month"], y=monthly_rev["total_revenue"],
            name="Revenue", mode="lines+markers",
            line=dict(color="#2563EB", width=2.5),
            marker=dict(size=5, color="#2563EB"),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.07)"
        ))
        fig_rev.add_trace(go.Scatter(
            x=monthly_rev["month"], y=monthly_rev["total_profit"],
            name="Profit", mode="lines+markers",
            line=dict(color="#16A34A", width=2, dash="dot"),
            marker=dict(size=4, color="#16A34A"),
        ))
        fig_rev.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.05, x=0),
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickprefix="$", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_rev, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Region-wise Revenue</div>", unsafe_allow_html=True)

    if not region_sales.empty:
        fig_region = go.Figure(go.Pie(
            labels=region_sales["region"],
            values=region_sales["total_revenue"],
            hole=0.55,
            marker=dict(colors=["#2563EB","#3B82F6","#60A5FA","#93C5FD","#BFDBFE"]),
            textinfo="percent+label",
            textfont=dict(size=11),
        ))
        fig_region.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False,
        )
        st.plotly_chart(fig_region, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 3: Top Products + Category Performance
# ---------------------------------------------------------------------------
col_l2, col_r2 = st.columns([1.3, 1])

with col_l2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 10 Products by Revenue</div>", unsafe_allow_html=True)

    if not top_products.empty:
        fig_top = go.Figure(go.Bar(
            x=top_products["total_revenue"].values[::-1],
            y=top_products["product_name"].values[::-1],
            orientation="h",
            marker=dict(
                color=top_products["total_revenue"].values[::-1],
                colorscale=[[0, "#BFDBFE"], [1, "#1D4ED8"]],
            ),
            text=[f"${v:,.0f}" for v in top_products["total_revenue"].values[::-1]],
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig_top.update_layout(
            height=380, margin=dict(l=0, r=50, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_top, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_r2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Category Performance</div>", unsafe_allow_html=True)

    if not category_df.empty:
        fig_cat = go.Figure(go.Bar(
            x=category_df["category"],
            y=category_df["total_revenue"],
            marker=dict(color=["#2563EB","#16A34A","#D97706","#7C3AED","#DB2777"]),
            text=[fmt_currency(v) for v in category_df["total_revenue"]],
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig_cat.update_layout(
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", showticklabels=False),
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 4: Monthly Orders Bar + Region Table
# ---------------------------------------------------------------------------
col_l3, col_r3 = st.columns([1, 1])

with col_l3:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Monthly Order Volume</div>", unsafe_allow_html=True)
    if not monthly_rev.empty:
        fig_ord = go.Figure(go.Bar(
            x=monthly_rev["month"], y=monthly_rev["total_orders"],
            marker=dict(color="#3B82F6", opacity=0.85),
        ))
        fig_ord.update_layout(
            height=260, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_ord, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_r3:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Region Summary</div>", unsafe_allow_html=True)
    if not region_sales.empty:
        disp = region_sales.copy()
        disp["total_revenue"] = disp["total_revenue"].apply(fmt_currency)
        disp["total_profit"]  = disp["total_profit"].apply(fmt_currency)
        disp.columns = ["Region", "Revenue", "Profit", "Orders"]
        st.dataframe(disp, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 5: Recent Transactions
# ---------------------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Recent Transactions</div>", unsafe_allow_html=True)

if not recent_tx.empty:
    disp_tx = recent_tx.copy()
    disp_tx["revenue"] = disp_tx["revenue"].apply(lambda v: f"${v:,.2f}")
    disp_tx["profit"]  = disp_tx["profit"].apply(lambda v: f"${v:,.2f}")
    st.dataframe(
        disp_tx[["order_id","customer","product","category","order_date",
                 "quantity","revenue","profit","region"]],
        use_container_width=True, hide_index=True
    )
st.markdown("</div>", unsafe_allow_html=True)
