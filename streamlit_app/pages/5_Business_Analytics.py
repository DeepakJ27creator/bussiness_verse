"""
BusinessVerse - Page 5: Business Analytics
Interactive analytics with date/region/category filters.
Sales trends, profit analysis, customer analysis, product analysis, time series.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from streamlit_app.utils.db_manager import run_query, DB_PATH

st.set_page_config(page_title="Analytics · BusinessVerse", page_icon="📈", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in first.")
    st.stop()

st.markdown("""
<div class='bv-header'>
    <div>
        <h1>📈 Business Analytics</h1>
        <p>Interactive analysis of sales, profit, customers, and products</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.error("⚠️ Database not found. Please run the data generator first.")
    st.stop()

# ---------------------------------------------------------------------------
# Load full dataset for filtering
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_all_orders():
    sql = """
    SELECT o.order_id, o.order_date, o.quantity, o.revenue, o.profit,
           o.discount, o.region,
           c.segment AS customer_segment,
           p.category, p.sub_category, p.product_name
    FROM orders o
    JOIN products  p ON o.product_id  = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    """
    df = run_query(sql)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

df_all = load_all_orders()

if df_all.empty or "Error" in df_all.columns:
    st.error("Could not load data from database.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔽 Filters")

    min_date = df_all["order_date"].min().date()
    max_date = df_all["order_date"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date, key="analytics_date")

    all_regions = sorted(df_all["region"].unique())
    sel_regions = st.multiselect("Region", all_regions, default=all_regions, key="analytics_region")

    all_categories = sorted(df_all["category"].unique())
    sel_cats = st.multiselect("Category", all_categories, default=all_categories, key="analytics_cat")

    all_segments = sorted(df_all["customer_segment"].unique())
    sel_segs = st.multiselect("Customer Segment", all_segments, default=all_segments, key="analytics_seg")

# Apply filters
if len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

df = df_all[
    (df_all["order_date"].dt.date >= start_d) &
    (df_all["order_date"].dt.date <= end_d) &
    (df_all["region"].isin(sel_regions)) &
    (df_all["category"].isin(sel_cats)) &
    (df_all["customer_segment"].isin(sel_segs))
].copy()

st.markdown(f"*Showing **{len(df):,}** orders after applying filters.*")
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

if df.empty:
    st.warning("No data matches the selected filters. Please adjust.")
    st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sales Trends", "💰 Profit Analysis", "👥 Customer Analysis",
    "📦 Product Analysis", "⏱ Time Series"
])

# ---------------------------------------------------------------------------
# TAB 1: Sales Trends
# ---------------------------------------------------------------------------
with tab1:
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        total_revenue=("revenue","sum"),
        total_orders=("order_id","count"),
        avg_order_value=("revenue","mean"),
    ).reset_index()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Monthly Revenue Trend</div>", unsafe_allow_html=True)
        fig = px.area(monthly, x="month", y="total_revenue",
                       labels={"total_revenue":"Revenue ($)","month":"Month"},
                       color_discrete_sequence=["#2563EB"])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Sales by Region</div>", unsafe_allow_html=True)
        reg_df = df.groupby("region")["revenue"].sum().reset_index()
        fig2 = px.bar(reg_df, x="region", y="revenue",
                       color="region", color_discrete_sequence=px.colors.qualitative.Set2,
                       labels={"revenue":"Revenue ($)"})
        fig2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                            plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Revenue by Customer Segment</div>", unsafe_allow_html=True)
        seg_df = df.groupby("customer_segment")["revenue"].sum().reset_index()
        fig3 = px.pie(seg_df, values="revenue", names="customer_segment", hole=0.5,
                       color_discrete_sequence=["#2563EB","#16A34A","#D97706"])
        fig3.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Average Order Value by Month</div>", unsafe_allow_html=True)
        fig4 = px.line(monthly, x="month", y="avg_order_value",
                        labels={"avg_order_value":"Avg Order Value ($)","month":"Month"},
                        color_discrete_sequence=["#7C3AED"], markers=True)
        fig4.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                            plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2: Profit Analysis
# ---------------------------------------------------------------------------
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Profit by Category</div>", unsafe_allow_html=True)
        cat_profit = df.groupby("category").agg(revenue=("revenue","sum"), profit=("profit","sum")).reset_index()
        cat_profit["margin_pct"] = (cat_profit["profit"] / cat_profit["revenue"] * 100).round(2)
        fig_p1 = go.Figure()
        fig_p1.add_bar(x=cat_profit["category"], y=cat_profit["revenue"], name="Revenue",
                        marker_color="#3B82F6")
        fig_p1.add_bar(x=cat_profit["category"], y=cat_profit["profit"], name="Profit",
                        marker_color="#16A34A")
        fig_p1.update_layout(barmode="group", height=300, margin=dict(l=0,r=0,t=10,b=0),
                              plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_p1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Profit Margin % by Category</div>", unsafe_allow_html=True)
        fig_p2 = px.bar(cat_profit, x="category", y="margin_pct",
                         color="margin_pct", color_continuous_scale="RdYlGn",
                         labels={"margin_pct":"Margin (%)", "category":"Category"},
                         text="margin_pct")
        fig_p2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_p2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                              plot_bgcolor="white", paper_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig_p2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Discount vs Profit (Scatter)</div>", unsafe_allow_html=True)
    fig_p3 = px.scatter(df, x="discount", y="profit", color="category",
                         opacity=0.5, size_max=8,
                         labels={"discount":"Discount","profit":"Profit ($)"},
                         color_discrete_sequence=px.colors.qualitative.Set2)
    fig_p3.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0),
                          plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_p3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 3: Customer Analysis
# ---------------------------------------------------------------------------
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Orders by Customer Segment</div>", unsafe_allow_html=True)
        seg_orders = df.groupby("customer_segment")["order_id"].count().reset_index()
        seg_orders.columns = ["Segment","Orders"]
        fig_c1 = px.bar(seg_orders, x="Segment", y="Orders", color="Segment",
                         color_discrete_sequence=["#2563EB","#16A34A","#D97706"],
                         text="Orders")
        fig_c1.update_traces(textposition="outside")
        fig_c1.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                              plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
        st.plotly_chart(fig_c1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Revenue by Segment & Region</div>", unsafe_allow_html=True)
        heat_df = df.groupby(["customer_segment","region"])["revenue"].sum().reset_index()
        heat_pivot = heat_df.pivot(index="customer_segment", columns="region", values="revenue").fillna(0)
        fig_c2 = px.imshow(heat_pivot, color_continuous_scale="Blues",
                            labels=dict(color="Revenue ($)"), aspect="auto")
        fig_c2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_c2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 4: Product Analysis
# ---------------------------------------------------------------------------
with tab4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Product Sub-category Revenue</div>", unsafe_allow_html=True)
    sub_df = df.groupby(["category","sub_category"]).agg(
        revenue=("revenue","sum"), orders=("order_id","count")
    ).reset_index().sort_values("revenue", ascending=False).head(20)
    fig_pr = px.treemap(sub_df, path=["category","sub_category"], values="revenue",
                         color="revenue", color_continuous_scale="Blues",
                         labels={"revenue":"Revenue"})
    fig_pr.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_pr, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 15 Products — Revenue vs Orders</div>", unsafe_allow_html=True)
    prod_df = df.groupby("product_name").agg(
        revenue=("revenue","sum"), orders=("order_id","count")
    ).reset_index().sort_values("revenue", ascending=False).head(15)
    fig_pr2 = px.scatter(prod_df, x="orders", y="revenue", text="product_name",
                          size="revenue", color="revenue", color_continuous_scale="Blues",
                          labels={"orders":"Number of Orders","revenue":"Revenue ($)"})
    fig_pr2.update_traces(textposition="top center", textfont_size=9)
    fig_pr2.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=20),
                           plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_pr2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 5: Time Series
# ---------------------------------------------------------------------------
with tab5:
    df["week"] = df["order_date"].dt.to_period("W").apply(lambda r: r.start_time)
    df["dow"]  = df["order_date"].dt.day_name()
    df["hour_of_month"] = df["order_date"].dt.day

    weekly = df.groupby("week").agg(revenue=("revenue","sum"), orders=("order_id","count")).reset_index()

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Weekly Revenue Trend</div>", unsafe_allow_html=True)
    fig_ts = px.line(weekly, x="week", y="revenue",
                      labels={"week":"Week","revenue":"Revenue ($)"},
                      color_discrete_sequence=["#2563EB"])
    fig_ts.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_ts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_ts1, col_ts2 = st.columns(2)
    with col_ts1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Revenue by Day of Week</div>", unsafe_allow_html=True)
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow_df = df.groupby("dow")["revenue"].sum().reindex(dow_order).reset_index()
        fig_dow = px.bar(dow_df, x="dow", y="revenue",
                          labels={"dow":"Day","revenue":"Revenue ($)"},
                          color_discrete_sequence=["#3B82F6"])
        fig_dow.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
                               plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_dow, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ts2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Revenue by Day of Month</div>", unsafe_allow_html=True)
        dom_df = df.groupby("hour_of_month")["revenue"].sum().reset_index()
        fig_dom = px.line(dom_df, x="hour_of_month", y="revenue",
                           labels={"hour_of_month":"Day of Month","revenue":"Revenue ($)"},
                           color_discrete_sequence=["#7C3AED"], markers=True)
        fig_dom.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
                               plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_dom, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
