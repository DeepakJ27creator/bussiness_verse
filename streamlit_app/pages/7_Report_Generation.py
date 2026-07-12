"""
BusinessVerse - Page 7: Report Generation
Download cleaned data, analytics reports, and export summaries.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import io
from datetime import datetime

from streamlit_app.utils.db_manager import (
    query_monthly_revenue, query_top_products, query_region_sales,
    query_category_performance, query_customer_purchase_frequency,
    get_kpis, DB_PATH
)

st.set_page_config(page_title="Reports · BusinessVerse", page_icon="📄", layout="wide")

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
        <h1>📄 Report Generation</h1>
        <p>Export analytics reports, cleaned data, and business summaries</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Report 1: Cleaned Dataset
# ---------------------------------------------------------------------------
st.markdown("### 📁 Dataset Export")
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Download Cleaned / Uploaded Dataset</div>", unsafe_allow_html=True)

if "clean_df" in st.session_state:
    df_clean = st.session_state["clean_df"]
    st.success(f"✅ Cleaned dataset available: **{len(df_clean):,} rows × {len(df_clean.columns)} columns**")
    col_a, col_b = st.columns(2)
    with col_a:
        csv_data = df_clean.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Cleaned Data (CSV)",
            data=csv_data,
            file_name=f"businessverse_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_b:
        # Excel export
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_clean.to_excel(writer, sheet_name="Cleaned Data", index=False)
        buf.seek(0)
        st.download_button(
            "⬇️ Download Cleaned Data (Excel)",
            data=buf.getvalue(),
            file_name=f"businessverse_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("ℹ️ No cleaned dataset available. Upload data on the **Data Upload** page first.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Report 2: Analytics Summary
# ---------------------------------------------------------------------------
if DB_PATH.exists():
    st.markdown("### 📊 Analytics Reports")

    col_left, col_right = st.columns(2)

    def df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    report_sections = [
        ("Monthly Revenue Report",          query_monthly_revenue,              "monthly_revenue"),
        ("Top Products Report",             lambda: query_top_products(20),     "top_products"),
        ("Region Sales Report",             query_region_sales,                 "region_sales"),
        ("Category Performance Report",     query_category_performance,         "category_performance"),
        ("Customer Purchase Frequency",     query_customer_purchase_frequency,  "customer_frequency"),
    ]

    for i, (title, fn, fname) in enumerate(report_sections):
        container = col_left if i % 2 == 0 else col_right
        with container:
            st.markdown(f"<div class='section-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
            df_rep = fn()
            if not df_rep.empty:
                st.dataframe(df_rep.head(10), use_container_width=True, hide_index=True)
                st.download_button(
                    f"⬇️ Download {title}",
                    data=df_to_csv(df_rep),
                    file_name=f"{fname}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"dl_{fname}"
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # Report 3: Full Business Summary Excel
    # ---------------------------------------------------------------------------
    st.markdown("### 📑 Full Business Summary Export")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Download Complete Analytics Bundle (Excel)</div>", unsafe_allow_html=True)
    st.markdown(
        "This bundle includes all analytics reports in a single Excel workbook with multiple sheets."
    )

    if st.button("📦 Generate Full Report Bundle", use_container_width=False, type="primary"):
        with st.spinner("Building report bundle..."):
            buf = io.BytesIO()
            kpis = get_kpis()
            kpi_df = pd.DataFrame([kpis])

            try:
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    kpi_df.to_excel(writer,                      sheet_name="KPI Summary",         index=False)
                    query_monthly_revenue().to_excel(writer,     sheet_name="Monthly Revenue",      index=False)
                    query_top_products(30).to_excel(writer,      sheet_name="Top Products",         index=False)
                    query_region_sales().to_excel(writer,        sheet_name="Region Sales",         index=False)
                    query_category_performance().to_excel(writer, sheet_name="Category Performance", index=False)
                    query_customer_purchase_frequency().to_excel(writer, sheet_name="Customer Frequency", index=False)

                buf.seek(0)
                st.download_button(
                    "⬇️ Download Full Business Report",
                    data=buf.getvalue(),
                    file_name=f"businessverse_full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("✅ Report bundle ready for download!")
            except Exception as e:
                st.error(f"Error generating report: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("ℹ️ No database found. Run the data generator to enable analytics reports.")

# ---------------------------------------------------------------------------
# Report 4: ML Model Info
# ---------------------------------------------------------------------------
from streamlit_app.utils.ml_utils import models_trained, MODELS_DIR

st.markdown("### 🤖 ML Model Files")
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Trained Model Status</div>", unsafe_allow_html=True)

trained = models_trained()
model_info = [
    ("Sales Prediction Model",      "sales_model.pkl",     trained["sales"]),
    ("Churn Prediction Model",      "churn_model.pkl",     trained["churn"]),
    ("Segmentation Model",          "segment_model.pkl",   trained["segmentation"]),
]

for label, fname, is_trained in model_info:
    col_i, col_j = st.columns([3, 1])
    with col_i:
        status_html = (
            f"<span class='badge badge-green'>✅ Trained</span>"
            if is_trained else
            f"<span class='badge badge-amber'>⚪ Not Trained</span>"
        )
        st.markdown(
            f"<div style='padding:0.5rem 0; border-bottom:1px solid #F1F5F9;'>"
            f"<b>{label}</b> <code style='color:#64748B; font-size:0.8rem;'>{fname}</code> "
            f"{status_html}</div>",
            unsafe_allow_html=True
        )
    with col_j:
        if is_trained:
            model_path = MODELS_DIR / fname
            if model_path.exists():
                with open(model_path, "rb") as f:
                    st.download_button(
                        "⬇️",
                        data=f.read(),
                        file_name=fname,
                        mime="application/octet-stream",
                        key=f"dl_model_{fname}",
                    )

st.markdown("</div>", unsafe_allow_html=True)
