"""
BusinessVerse - Main Application Entry Point
Handles authentication and multi-page navigation using st.navigation().

Run with:  streamlit run streamlit_app/app.py
"""

import sys
import os
from pathlib import Path

# Ensure project root is in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="BusinessVerse Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load custom CSS
# ---------------------------------------------------------------------------
def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------------------------------------------------------------------
# Demo credentials
# ---------------------------------------------------------------------------
USERS = {
    "admin":   "admin123",
    "analyst": "analyst123",
    "demo":    "demo",
}

# ---------------------------------------------------------------------------
# Login Page
# ---------------------------------------------------------------------------
def show_login():
    col_l, col_mid, col_r = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("""
        <div style='text-align:center; margin-bottom:2rem;'>
            <div style='font-size:2.5rem; font-weight:800; color:#2563EB; letter-spacing:-0.03em;'>
                📊 BusinessVerse
            </div>
            <div style='font-size:0.95rem; color:#64748B; margin-top:0.25rem;'>
                Business Analytics Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### Sign in to your account")

            username = st.text_input("Username", placeholder="Enter username", key="login_user")
            password = st.text_input("Password", placeholder="Enter password",
                                      type="password", key="login_pass")

            col1, col2 = st.columns([1, 1])
            with col1:
                login_btn = st.button("Sign In", use_container_width=True, type="primary")
            with col2:
                st.markdown(
                    "<p style='font-size:0.8rem; color:#64748B; padding-top:0.6rem;'>"
                    "Try: <b>demo / demo</b></p>",
                    unsafe_allow_html=True
                )

            if login_btn:
                if username in USERS and USERS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username.capitalize()}! Loading dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown(
            "<div style='text-align:center; margin-top:1.5rem; font-size:0.75rem; color:#94A3B8;'>"
            "BusinessVerse v1.0 · Professional Analytics Platform</div>",
            unsafe_allow_html=True
        )


# ---------------------------------------------------------------------------
# Sidebar (shown when authenticated)
# ---------------------------------------------------------------------------
def build_sidebar():
    with st.sidebar:
        st.markdown(
            "<div style='font-size:1.25rem; font-weight:800; color:#2563EB; "
            "letter-spacing:-0.02em; padding:0.25rem 0 0.75rem 0;'>📊 BusinessVerse</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='font-size:0.8rem; color:#475569; margin-bottom:1rem;'>"
            f"<span style='display:inline-block; width:8px; height:8px; border-radius:50%; "
            f"background:#16A34A; margin-right:6px;'></span>"
            f"Signed in as <b>{st.session_state.username}</b></div>",
            unsafe_allow_html=True
        )
        st.markdown("<hr style='border-color:#E2E8F0; margin:0 0 0.75rem 0;'>", unsafe_allow_html=True)

        # Sign out button
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

        st.markdown(
            "<div style='font-size:0.7rem; color:#CBD5E1; margin-top:2rem; padding-top:1rem; "
            "border-top:1px solid #F1F5F9;'>BusinessVerse v1.0<br>© 2024 Analytics Platform</div>",
            unsafe_allow_html=True
        )


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------
if not st.session_state.authenticated:
    # Show only login page — no sidebar navigation
    show_login()
else:
    # Build the sidebar sign-out control
    build_sidebar()

    # Multi-page navigation using st.navigation (Streamlit >= 1.28)
    pages = [
        st.Page("pages/1_Dashboard.py",          title="Dashboard",           icon="🏠"),
        st.Page("pages/2_Data_Upload.py",         title="Data Upload",         icon="📁"),
        st.Page("pages/3_Data_Cleaning.py",       title="Data Cleaning",       icon="🧹"),
        st.Page("pages/4_SQL_Analytics.py",       title="SQL Analytics",       icon="🗄️"),
        st.Page("pages/5_Business_Analytics.py",  title="Business Analytics",  icon="📈"),
        st.Page("pages/6_Machine_Learning.py",    title="Machine Learning",    icon="🤖"),
        st.Page("pages/7_Report_Generation.py",   title="Reports",             icon="📄"),
    ]

    nav = st.navigation(pages)
    nav.run()
