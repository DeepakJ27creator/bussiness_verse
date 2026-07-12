"""
BusinessVerse - Page 6: Machine Learning
Sales Prediction (Linear Regression), Customer Churn (Random Forest),
Customer Segmentation (K-Means).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from streamlit_app.utils.db_manager import run_query, DB_PATH
from streamlit_app.utils.ml_utils import (
    train_sales_model, predict_sales,
    train_churn_model, predict_churn,
    train_segmentation_model, models_trained
)

st.set_page_config(page_title="Machine Learning · BusinessVerse", page_icon="🤖", layout="wide")

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
        <h1>🤖 Machine Learning</h1>
        <p>Train and run predictive models on your business data</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.error("⚠️ Database not found. Please run the data generator first.")
    st.stop()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_orders():
    return run_query("SELECT * FROM orders")

@st.cache_data(ttl=600)
def load_customers():
    return run_query("SELECT * FROM customers")

orders_df    = load_orders()
customers_df = load_customers()

# ---------------------------------------------------------------------------
# Model status
# ---------------------------------------------------------------------------
trained = models_trained()
col_s1, col_s2, col_s3 = st.columns(3)

for col, name, key in zip([col_s1, col_s2, col_s3],
                           ["Sales Model", "Churn Model", "Segmentation Model"],
                           ["sales", "churn", "segmentation"]):
    with col:
        status = "✅ Trained" if trained[key] else "⚪ Not Trained"
        color  = "#DCFCE7" if trained[key] else "#F1F5F9"
        st.markdown(f"""
        <div style='background:{color}; border:1px solid #E2E8F0;
             border-radius:10px; padding:0.9rem 1.2rem;'>
            <div style='font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase;'>{name}</div>
            <div style='font-size:1rem; font-weight:700; color:#0F172A; margin-top:0.25rem;'>{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Sales Prediction", "⚠️ Churn Prediction", "🎯 Customer Segmentation"
])

# ===========================================================================
# TAB 1: SALES PREDICTION
# ===========================================================================
with tab1:
    col_left, col_right = st.columns([1.2, 2])

    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Model Configuration</div>", unsafe_allow_html=True)
        st.markdown("**Algorithm:** Linear Regression")
        st.markdown("**Target:** Monthly Total Revenue")
        st.markdown("**Features:** Lag revenue, rolling mean, order volume, discount")

        if st.button("🚀 Train Sales Model", use_container_width=True, type="primary"):
            if orders_df.empty:
                st.error("No orders data found.")
            else:
                with st.spinner("Training model..."):
                    result = train_sales_model(orders_df)
                if "error" in result:
                    st.error(result["error"])
                else:
                    m = result["metrics"]
                    st.success("✅ Model trained and saved!")
                    st.metric("MAE",  f"${m['MAE']:,.2f}")
                    st.metric("RMSE", f"${m['RMSE']:,.2f}")
                    st.metric("R² Score", f"{m['R2']:.4f}")
                    st.rerun()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        months = st.slider("Months to predict", 1, 24, 6, key="sales_months")
        if st.button("🔮 Predict Future Revenue", use_container_width=True):
            preds = predict_sales(months)
            if preds.empty:
                st.warning("Please train the model first.")
            else:
                st.session_state["sales_preds"] = preds

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Revenue Prediction Chart</div>", unsafe_allow_html=True)

        if not orders_df.empty:
            # Historical data
            orders_df["order_date"] = pd.to_datetime(orders_df["order_date"])
            hist = orders_df.groupby(orders_df["order_date"].dt.to_period("M").astype(str))["revenue"].sum().reset_index()
            hist.columns = ["month","revenue"]

            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(
                x=hist["month"], y=hist["revenue"],
                name="Historical Revenue", mode="lines+markers",
                line=dict(color="#2563EB", width=2),
                marker=dict(size=4),
            ))

            if "sales_preds" in st.session_state:
                preds = st.session_state["sales_preds"]
                preds["month_str"] = preds["month"].dt.strftime("%Y-%m")
                fig_s.add_trace(go.Scatter(
                    x=preds["month_str"], y=preds["predicted_revenue"],
                    name="Predicted Revenue", mode="lines+markers",
                    line=dict(color="#D97706", width=2, dash="dash"),
                    marker=dict(size=6, symbol="diamond"),
                ))

            fig_s.update_layout(
                height=380, margin=dict(l=0,r=0,t=10,b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                legend=dict(orientation="h", y=1.05, x=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickprefix="$"),
            )
            st.plotly_chart(fig_s, use_container_width=True)

            if "sales_preds" in st.session_state:
                preds = st.session_state["sales_preds"]
                st.dataframe(
                    preds.assign(predicted_revenue=preds["predicted_revenue"].apply(lambda v: f"${v:,.2f}"))
                         .rename(columns={"month":"Month","predicted_revenue":"Predicted Revenue"}),
                    use_container_width=True, hide_index=True
                )

        st.markdown("</div>", unsafe_allow_html=True)

# ===========================================================================
# TAB 2: CHURN PREDICTION
# ===========================================================================
with tab2:
    col_l, col_r = st.columns([1.2, 2])

    with col_l:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Model Configuration</div>", unsafe_allow_html=True)
        st.markdown("**Algorithm:** Random Forest Classifier")
        st.markdown("**Target:** Customer Churn (Yes/No)")
        st.markdown("**Features:** Purchase history, recency, segment, region")

        if st.button("🚀 Train Churn Model", use_container_width=True, type="primary"):
            with st.spinner("Training model..."):
                result = train_churn_model(customers_df, orders_df)
            if "error" in result:
                st.error(result["error"])
            else:
                acc = result["metrics"]["Accuracy"]
                report = result["metrics"]["Report"]
                st.success(f"✅ Model trained! Accuracy: {acc*100:.1f}%")
                st.rerun()

        st.markdown("<hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("**Predict for a Customer**")

        c_purchases = st.number_input("Total Purchases", 0, 500, 12, key="churn_purchases")
        c_spent     = st.number_input("Total Spent ($)", 0.0, 100000.0, 2500.0, key="churn_spent")
        c_days      = st.number_input("Days as Customer", 0, 2000, 365, key="churn_days")
        c_recency   = st.number_input("Days Since Last Order", 0, 1000, 90, key="churn_recency")
        c_region    = st.selectbox("Region", ["North","South","East","West","Central"], key="churn_region")
        c_segment   = st.selectbox("Segment", ["Consumer","Corporate","Home Office"], key="churn_segment")

        region_map  = {"North":0,"South":1,"East":2,"West":3,"Central":4}
        segment_map = {"Consumer":0,"Corporate":1,"Home Office":2}

        if st.button("🔮 Predict Churn", use_container_width=True):
            pred, proba = predict_churn({
                "total_purchases":       c_purchases,
                "total_spent":           c_spent,
                "days_as_customer":      c_days,
                "days_since_last_order": c_recency,
                "region_enc":            region_map.get(c_region, 0),
                "segment_enc":           segment_map.get(c_segment, 0),
            })
            if pred is None:
                st.warning("Please train the model first.")
            else:
                st.session_state["churn_pred"]  = pred
                st.session_state["churn_proba"] = proba

        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Churn Prediction Result</div>", unsafe_allow_html=True)

        if "churn_pred" in st.session_state:
            pred  = st.session_state["churn_pred"]
            proba = st.session_state["churn_proba"]
            risk  = "High Risk" if proba > 0.65 else ("Medium Risk" if proba > 0.35 else "Low Risk")
            color = "#FEE2E2" if proba > 0.65 else ("#FEF3C7" if proba > 0.35 else "#DCFCE7")
            tcolor= "#B91C1C" if proba > 0.65 else ("#B45309" if proba > 0.35 else "#15803D")

            st.markdown(f"""
            <div style='background:{color}; border-radius:12px; padding:2rem; text-align:center; margin-bottom:1rem;'>
                <div style='font-size:0.85rem; color:{tcolor}; font-weight:600; text-transform:uppercase;'>Prediction Result</div>
                <div style='font-size:2.5rem; font-weight:800; color:{tcolor}; margin:0.5rem 0;'>
                    {"🚨 Will Churn" if pred == 1 else "✅ Will Retain"}
                </div>
                <div style='font-size:1.1rem; color:{tcolor};'>Churn Probability: <b>{proba*100:.1f}%</b></div>
                <div style='font-size:0.9rem; color:{tcolor}; margin-top:0.25rem;'>Risk Level: <b>{risk}</b></div>
            </div>
            """, unsafe_allow_html=True)

            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=proba * 100,
                title={"text": "Churn Probability (%)", "font": {"size": 14}},
                gauge={
                    "axis":   {"range": [0, 100]},
                    "bar":    {"color": tcolor},
                    "steps": [
                        {"range": [0, 35],  "color": "#DCFCE7"},
                        {"range": [35, 65], "color": "#FEF3C7"},
                        {"range": [65, 100],"color": "#FEE2E2"},
                    ],
                    "threshold": {"line": {"color": "red","width": 3},
                                   "thickness": 0.75, "value": proba * 100}
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=30,r=30,t=20,b=10),
                                     paper_bgcolor="white")
            st.plotly_chart(fig_gauge, use_container_width=True)

        else:
            st.markdown("""
            <div style='text-align:center; padding:3rem; color:#94A3B8;'>
                <div style='font-size:2rem; margin-bottom:1rem;'>⚠️</div>
                <div>Train the model and enter customer details to see a prediction.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Churn distribution
        if not customers_df.empty and "is_churned" in customers_df.columns:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Churn Distribution in Dataset</div>", unsafe_allow_html=True)
            churn_counts = customers_df["is_churned"].value_counts().reset_index()
            churn_counts.columns = ["Churned","Count"]
            churn_counts["Churned"] = churn_counts["Churned"].map({0:"Retained",1:"Churned"})
            fig_cd = px.pie(churn_counts, values="Count", names="Churned",
                             hole=0.55, color="Churned",
                             color_discrete_map={"Retained":"#16A34A","Churned":"#DC2626"})

            fig_cd.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="white")
            st.plotly_chart(fig_cd, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ===========================================================================
# TAB 3: CUSTOMER SEGMENTATION
# ===========================================================================
with tab3:
    col_l3, col_r3 = st.columns([1, 2.5])

    with col_l3:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Segmentation Config</div>", unsafe_allow_html=True)
        st.markdown("**Algorithm:** K-Means Clustering")
        st.markdown("**Features:** Purchases, spend, recency, tenure")

        n_clusters = st.slider("Number of Segments (K)", 2, 8, 4, key="kmeans_k")

        if st.button("🚀 Run Segmentation", use_container_width=True, type="primary"):
            with st.spinner("Clustering customers..."):
                result = train_segmentation_model(customers_df, orders_df, n_clusters)
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state["segment_result"] = result
                st.success(f"✅ {n_clusters} segments identified!")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_r3:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Customer Segments Visualization</div>", unsafe_allow_html=True)

        if "segment_result" in st.session_state:
            res     = st.session_state["segment_result"]
            seg_df  = res["labeled_df"]

            # Scatter: Total Spent vs Purchases
            fig_seg = px.scatter(
                seg_df, x="total_purchases", y="total_spent",
                color="segment_label", size="total_spent",
                hover_data=["customer_id","recency"],
                labels={"total_purchases":"Number of Purchases","total_spent":"Total Spent ($)",
                        "segment_label":"Segment"},
                color_discrete_sequence=["#2563EB","#16A34A","#D97706","#7C3AED","#DB2777","#0891B2","#DC2626","#059669"],
            )
            fig_seg.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0),
                                   plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_seg, use_container_width=True)

            # Segment summary table
            seg_summary = seg_df.groupby("segment_label").agg(
                customers=("customer_id","count"),
                avg_purchases=("total_purchases","mean"),
                avg_spent=("total_spent","mean"),
                avg_recency=("recency","mean"),
            ).reset_index().round(2)
            seg_summary.columns = ["Segment","Customers","Avg Purchases","Avg Spent ($)","Avg Recency (days)"]
            st.dataframe(seg_summary, use_container_width=True, hide_index=True)

            # Pie chart
            fig_pie = px.pie(seg_df, names="segment_label", hole=0.5,
                              color_discrete_sequence=["#2563EB","#16A34A","#D97706","#7C3AED"])
            fig_pie.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="white")
            st.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.markdown("""
            <div style='text-align:center; padding:3rem; color:#94A3B8;'>
                <div style='font-size:2rem; margin-bottom:1rem;'>🎯</div>
                <div>Configure and run segmentation to see customer clusters.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
