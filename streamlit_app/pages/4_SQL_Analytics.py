"""
BusinessVerse - Page 4: SQL Analytics
Run pre-built and custom SQL queries against the business database.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from streamlit_app.utils.db_manager import (
    run_query, query_monthly_revenue, query_top_products,
    query_region_sales, query_category_performance,
    query_customer_purchase_frequency, query_best_performing_category,
    get_kpis, DB_PATH
)

st.set_page_config(page_title="SQL Analytics · BusinessVerse", page_icon="🗄️", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in first.")
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class='bv-header'>
    <div>
        <h1>🗄️ SQL Analytics</h1>
        <p>Query the business database with pre-built and custom SQL</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Check DB exists
if not DB_PATH.exists():
    st.error("⚠️ Database not found. Please run `python streamlit_app/utils/data_generator.py` to create it.")
    st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Monthly Revenue", "🏆 Top Products", "🌍 Region Sales",
    "📂 Categories", "👤 Customers", "💻 Custom SQL"
])

# --- Monthly Revenue ---
with tab1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Monthly Revenue & Profit</div>", unsafe_allow_html=True)

    st.code("""
SELECT strftime('%Y-%m', order_date) AS month,
       SUM(revenue)                  AS total_revenue,
       SUM(profit)                   AS total_profit,
       COUNT(order_id)               AS total_orders
FROM orders
GROUP BY month ORDER BY month;
    """, language="sql")

    df_mr = query_monthly_revenue()
    if not df_mr.empty:
        fig = go.Figure()
        fig.add_bar(x=df_mr["month"], y=df_mr["total_revenue"], name="Revenue",
                    marker_color="#2563EB", opacity=0.8)
        fig.add_bar(x=df_mr["month"], y=df_mr["total_profit"], name="Profit",
                    marker_color="#16A34A", opacity=0.8)
        fig.update_layout(barmode="group", height=340,
                           margin=dict(l=0, r=0, t=10, b=0),
                           plot_bgcolor="white", paper_bgcolor="white",
                           xaxis=dict(showgrid=False),
                           yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickprefix="$"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_mr, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Top Products ---
with tab2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top Products by Revenue</div>", unsafe_allow_html=True)

    limit = st.slider("Number of products", 5, 30, 10, key="top_prod_limit")
    st.code(f"""
SELECT p.product_name, p.category,
       SUM(o.revenue) AS total_revenue,
       SUM(o.quantity) AS units_sold,
       SUM(o.profit) AS total_profit
FROM orders o JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC LIMIT {limit};
    """, language="sql")

    df_tp = query_top_products(limit)
    if not df_tp.empty:
        fig2 = px.bar(
            df_tp.sort_values("total_revenue"),
            x="total_revenue", y="product_name", orientation="h",
            color="category", color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"total_revenue": "Revenue ($)", "product_name": "Product"},
        )
        fig2.update_layout(height=max(300, limit * 28),
                            margin=dict(l=0, r=0, t=10, b=0),
                            plot_bgcolor="white", paper_bgcolor="white",
                            showlegend=True,
                            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"))
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df_tp, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Region Sales ---
with tab3:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Region-wise Sales Analysis</div>", unsafe_allow_html=True)

    st.code("""
SELECT region,
       SUM(revenue)  AS total_revenue,
       SUM(profit)   AS total_profit,
       COUNT(*)      AS total_orders
FROM orders GROUP BY region ORDER BY total_revenue DESC;
    """, language="sql")

    df_rs = query_region_sales()
    if not df_rs.empty:
        col_left, col_right = st.columns(2)
        with col_left:
            fig3a = px.bar(
                df_rs, x="region", y="total_revenue",
                color="region", color_discrete_sequence=["#2563EB","#16A34A","#D97706","#7C3AED","#DB2777"],
                labels={"total_revenue":"Revenue ($)", "region":"Region"},
            )
            fig3a.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                                 plot_bgcolor="white", paper_bgcolor="white",
                                 showlegend=False)
            st.plotly_chart(fig3a, use_container_width=True)
        with col_right:
            fig3b = px.pie(df_rs, values="total_orders", names="region",
                           hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig3b.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                                 paper_bgcolor="white")
            st.plotly_chart(fig3b, use_container_width=True)
        st.dataframe(df_rs, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Categories ---
with tab4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Category & Sub-category Performance</div>", unsafe_allow_html=True)

    st.code("""
SELECT p.category, p.sub_category,
       SUM(o.revenue) AS total_revenue,
       SUM(o.profit)  AS total_profit,
       COUNT(*)       AS orders
FROM orders o JOIN products p ON o.product_id = p.product_id
GROUP BY p.category, p.sub_category ORDER BY total_revenue DESC;
    """, language="sql")

    df_cat = query_best_performing_category()
    if not df_cat.empty:
        fig4 = px.treemap(df_cat, path=["category","sub_category"],
                           values="total_revenue", color="total_profit",
                           color_continuous_scale="Blues",
                           labels={"total_revenue":"Revenue","total_profit":"Profit"})
        fig4.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(df_cat, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Customers ---
with tab5:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Customer Purchase Frequency (Top 50)</div>", unsafe_allow_html=True)

    st.code("""
SELECT c.customer_id, c.name, c.segment, c.region,
       COUNT(o.order_id) AS purchase_count,
       SUM(o.revenue)    AS total_spent,
       MAX(o.order_date) AS last_purchase_date
FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 50;
    """, language="sql")

    df_cust = query_customer_purchase_frequency()
    if not df_cust.empty:
        fig5 = px.scatter(df_cust, x="purchase_count", y="total_spent",
                           color="segment", size="total_spent",
                           hover_data=["name", "region"],
                           labels={"purchase_count":"Purchases","total_spent":"Total Spent ($)"},
                           color_discrete_sequence=px.colors.qualitative.Set2)
        fig5.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0),
                            plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig5, use_container_width=True)
        st.dataframe(df_cust, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Custom SQL ---
with tab6:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Custom SQL Query</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='bv-info-box'>
        Available tables: <b>orders</b>, <b>customers</b>, <b>products</b><br>
        Only SELECT queries are allowed. The results are read-only.
    </div>
    """, unsafe_allow_html=True)

    default_sql = """SELECT p.category,
       SUM(o.revenue) AS total_revenue,
       AVG(o.discount) AS avg_discount,
       COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;"""

    custom_sql = st.text_area("SQL Query", value=default_sql, height=180)

    if st.button("▶ Run Query", type="primary"):
        if custom_sql.strip().lower().startswith("select"):
            result = run_query(custom_sql)
            if "Error" in result.columns:
                st.error(f"Query error: {result['Error'].iloc[0]}")
            else:
                st.success(f"✅ Returned {len(result):,} rows · {len(result.columns)} columns")
                st.dataframe(result, use_container_width=True, hide_index=True)
                csv = result.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Results", data=csv,
                                   file_name="query_results.csv", mime="text/csv")
        else:
            st.warning("⚠️ Only SELECT queries are permitted for safety.")

    st.markdown("</div>", unsafe_allow_html=True)
