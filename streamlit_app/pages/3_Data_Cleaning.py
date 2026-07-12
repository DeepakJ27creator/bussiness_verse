"""
BusinessVerse - Page 3: Data Cleaning
Interactive data cleaning: null removal, fill, deduplication,
column type conversion, and feature selection.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Cleaning · BusinessVerse", page_icon="🧹", layout="wide")

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
        <h1>🧹 Data Cleaning</h1>
        <p>Clean and prepare your dataset for analysis</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data from session
# ---------------------------------------------------------------------------
if "uploaded_df" not in st.session_state:
    st.info("📂 Please upload a dataset on the **Data Upload** page first.")
    st.stop()

# Work on a copy stored in session
if "clean_df" not in st.session_state:
    st.session_state["clean_df"] = st.session_state["uploaded_df"].copy()

df_original = st.session_state["uploaded_df"]
df = st.session_state["clean_df"]

# ---------------------------------------------------------------------------
# Status bar
# ---------------------------------------------------------------------------
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.metric("Original Rows",    f"{len(df_original):,}")
with col_s2:
    st.metric("Current Rows",     f"{len(df):,}")
with col_s3:
    st.metric("Rows Removed",     f"{len(df_original) - len(df):,}")
with col_s4:
    st.metric("Missing Values",   f"{df.isnull().sum().sum():,}")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Cleaning Operations (sidebar panel)
# ---------------------------------------------------------------------------
st.markdown("### Cleaning Operations")

col_ops, col_preview = st.columns([1, 2.5])

with col_ops:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Available Operations</div>", unsafe_allow_html=True)

    # 1. Remove rows with any null
    if st.button("🗑️ Drop Rows with Nulls", use_container_width=True):
        before = len(df)
        df = df.dropna()
        st.session_state["clean_df"] = df
        st.success(f"Removed {before - len(df):,} rows with missing values.")
        st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # 2. Fill null with mean/median/mode
    st.markdown("**Fill Missing Values**")
    fill_col    = st.selectbox("Column", ["(all numeric)"] + list(df.columns), key="fill_col")
    fill_method = st.selectbox("Fill with", ["Mean", "Median", "Mode", "Zero", "Custom Value"], key="fill_method")
    fill_custom = ""
    if fill_method == "Custom Value":
        fill_custom = st.text_input("Custom value", key="fill_custom")

    if st.button("▶ Apply Fill", use_container_width=True):
        try:
            targets = [fill_col] if fill_col != "(all numeric)" else df.select_dtypes(include="number").columns.tolist()
            for col_name in targets:
                if fill_method == "Mean":
                    df[col_name].fillna(df[col_name].mean(), inplace=True)
                elif fill_method == "Median":
                    df[col_name].fillna(df[col_name].median(), inplace=True)
                elif fill_method == "Mode":
                    df[col_name].fillna(df[col_name].mode()[0], inplace=True)
                elif fill_method == "Zero":
                    df[col_name].fillna(0, inplace=True)
                elif fill_method == "Custom Value" and fill_custom:
                    df[col_name].fillna(fill_custom, inplace=True)
            st.session_state["clean_df"] = df
            st.success(f"Missing values filled using {fill_method}.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # 3. Remove duplicates
    if st.button("🔁 Remove Duplicates", use_container_width=True):
        before = len(df)
        df = df.drop_duplicates()
        st.session_state["clean_df"] = df
        st.success(f"Removed {before - len(df):,} duplicate rows.")
        st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # 4. Column type conversion
    st.markdown("**Convert Column Type**")
    conv_col  = st.selectbox("Column to convert", df.columns.tolist(), key="conv_col")
    conv_type = st.selectbox("Target type", ["int", "float", "str", "datetime"], key="conv_type")
    if st.button("⚙️ Convert Type", use_container_width=True):
        try:
            if conv_type == "datetime":
                df[conv_col] = pd.to_datetime(df[conv_col], errors="coerce")
            elif conv_type == "int":
                df[conv_col] = pd.to_numeric(df[conv_col], errors="coerce").astype("Int64")
            elif conv_type == "float":
                df[conv_col] = pd.to_numeric(df[conv_col], errors="coerce")
            else:
                df[conv_col] = df[conv_col].astype(str)
            st.session_state["clean_df"] = df
            st.success(f"Column '{conv_col}' converted to {conv_type}.")
            st.rerun()
        except Exception as e:
            st.error(f"Conversion failed: {e}")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # 5. Feature selection (drop columns)
    st.markdown("**Drop Columns**")
    cols_to_drop = st.multiselect("Select columns to remove", df.columns.tolist(), key="drop_cols")
    if st.button("❌ Drop Selected Columns", use_container_width=True):
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            st.session_state["clean_df"] = df
            st.success(f"Dropped {len(cols_to_drop)} column(s).")
            st.rerun()
        else:
            st.warning("No columns selected.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # 6. Reset
    if st.button("🔄 Reset to Original", use_container_width=True):
        st.session_state["clean_df"] = st.session_state["uploaded_df"].copy()
        st.success("Dataset reset to original.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Preview panel
# ---------------------------------------------------------------------------
with col_preview:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Current Dataset Preview</div>", unsafe_allow_html=True)

    tab_prev, tab_miss, tab_dtype = st.tabs(["Preview", "Missing Values", "Data Types"])

    with tab_prev:
        n = st.slider("Rows", 5, min(100, len(df)), 20, key="clean_slider")
        st.dataframe(df.head(n), use_container_width=True)

    with tab_miss:
        miss_df = df.isnull().sum().reset_index()
        miss_df.columns = ["Column", "Missing Count"]
        miss_df["Missing %"] = (miss_df["Missing Count"] / len(df) * 100).round(2)
        miss_df = miss_df[miss_df["Missing Count"] > 0]
        if miss_df.empty:
            st.success("✅ No missing values remain.")
        else:
            st.dataframe(miss_df, use_container_width=True, hide_index=True)

    with tab_dtype:
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Dtype":  df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Download cleaned data
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    csv_clean = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Cleaned Dataset",
        data=csv_clean,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        use_container_width=True,
    )
