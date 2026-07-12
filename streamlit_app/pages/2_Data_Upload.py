"""
BusinessVerse - Page 2: Data Upload
Upload CSV files, preview data, view statistics, and detect missing values.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Upload · BusinessVerse", page_icon="📁", layout="wide")

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
        <h1>📁 Data Upload</h1>
        <p>Upload your CSV datasets for analysis</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# File uploader
# ---------------------------------------------------------------------------
st.markdown("### Upload Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV file", type=["csv"],
    help="Upload any CSV file. The system will auto-detect column types and statistics.",
    label_visibility="collapsed"
)

# Also allow loading built-in sample data
col_hint1, col_hint2 = st.columns([3, 1])
with col_hint1:
    st.markdown(
        "<div class='bv-info-box'>You can upload your own CSV file, or load the built-in sample dataset below.</div>",
        unsafe_allow_html=True
    )
with col_hint2:
    load_sample = st.button("📂 Load Sample Data", use_container_width=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = None

if load_sample:
    sample_path = Path(__file__).resolve().parent.parent.parent / "data" / "orders.csv"
    if sample_path.exists():
        df = pd.read_csv(sample_path)
        st.success(f"✅ Sample orders dataset loaded: **{len(df):,} rows × {len(df.columns)} columns**")
    else:
        st.error("Sample data not found. Please run `python streamlit_app/utils/data_generator.py` first.")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded successfully: **{uploaded_file.name}** · {len(df):,} rows × {len(df.columns)} columns")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Store in session for use in cleaning page
if df is not None:
    st.session_state["uploaded_df"] = df

# ---------------------------------------------------------------------------
# Display dataset info
# ---------------------------------------------------------------------------
if df is not None:
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Quick stats
    cols_stat = st.columns(5)
    stats = [
        ("Rows",          f"{len(df):,}"),
        ("Columns",       f"{len(df.columns)}"),
        ("Numeric Cols",  f"{df.select_dtypes(include='number').shape[1]}"),
        ("Missing Values",f"{df.isnull().sum().sum():,}"),
        ("Duplicates",    f"{df.duplicated().sum():,}"),
    ]
    colors = ["blue","green","amber","purple","blue"]
    for col_el, (label, value), color in zip(cols_stat, stats, colors):
        with col_el:
            st.markdown(f"""
            <div class='kpi-card {color}'>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value' style='font-size:1.4rem'>{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Preview", "📊 Statistics", "❓ Missing Values", "🔍 Column Info"])

    with tab1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Dataset Preview</div>", unsafe_allow_html=True)
        n_rows = st.slider("Rows to display", 5, min(100, len(df)), 20, key="preview_slider")
        st.dataframe(df.head(n_rows), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Descriptive Statistics (Numeric Columns)</div>", unsafe_allow_html=True)
        desc = df.describe().T.reset_index()
        desc.columns = ["Column"] + list(desc.columns[1:])
        st.dataframe(desc.style.format(precision=2), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Descriptive Statistics (Categorical Columns)</div>", unsafe_allow_html=True)
        cat_desc = df.describe(include="object").T.reset_index()
        if not cat_desc.empty:
            cat_desc.columns = ["Column"] + list(cat_desc.columns[1:])
            st.dataframe(cat_desc, use_container_width=True)
        else:
            st.info("No categorical columns found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Missing Value Analysis</div>", unsafe_allow_html=True)
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Column", "Missing Count"]
        missing["Missing %"] = (missing["Missing Count"] / len(df) * 100).round(2)
        missing["Status"] = missing["Missing Count"].apply(
            lambda x: "✅ Complete" if x == 0 else ("⚠️ Minor" if x < len(df)*0.05 else "❌ High")
        )
        missing = missing.sort_values("Missing Count", ascending=False)
        st.dataframe(missing, use_container_width=True, hide_index=True)
        total_missing = missing["Missing Count"].sum()
        if total_missing == 0:
            st.success("✅ No missing values found in this dataset.")
        else:
            st.warning(f"⚠️ Found {total_missing:,} missing values across {(missing['Missing Count'] > 0).sum()} columns.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Column Information</div>", unsafe_allow_html=True)
        col_info = pd.DataFrame({
            "Column":   df.columns,
            "Dtype":    df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null":     df.isnull().sum().values,
            "Unique":   df.nunique().values,
            "Sample":   [str(df[c].dropna().iloc[0]) if df[c].notnull().any() else "N/A" for c in df.columns],
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Placeholder state
    st.markdown("""
    <div class='section-card' style='text-align:center; padding:4rem 2rem;'>
        <div style='font-size:3rem; margin-bottom:1rem;'>📂</div>
        <div style='font-size:1.1rem; font-weight:600; color:#374151; margin-bottom:0.5rem;'>
            No Data Uploaded Yet
        </div>
        <div style='font-size:0.9rem; color:#64748B;'>
            Upload a CSV file above or load the built-in sample dataset to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)
