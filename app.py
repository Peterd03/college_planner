import streamlit as st
import pandas as pd
from main import (
    build_pipeline,
    display_output,
    MSI_CATEGORIES,
    DEGREE_ORDER
)

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="College Match Planner",
    layout="wide"
)

# ---------------------------------------------------------
# GLOBAL CSS — BEAUTIFUL LOVABLE-STYLE UI
# ---------------------------------------------------------
st.markdown("""
<style>

html, body, .block-container {
    background-color: #ffffff !important;
    font-family: "Inter", sans-serif;
}

/* Headings + Text — BLACK */
h1, h2, h3, h4, label, p, div, span {
    color: #000000 !important;
}

/* Section Cards */
.card {
    background: #ffffff;
    padding: 28px 32px;
    border-radius: 18px;
    border: 1px solid #e5e5e5;
    box-shadow: 0px 6px 14px rgba(0,0,0,0.05);
    margin-bottom: 30px;
}

/* Sliders */
.stSlider > div > div > div {
    color: #000;
}

/* Buttons */
.stButton>button {
    background-color: #4a6cf7 !important;
    color: #ffffff !important;
    padding: 0.7rem 1.4rem;
    border-radius: 12px;
    font-size: 1rem;
    border: none;
    transition: 0.2s ease;
}
.stButton>button:hover {
    background-color: #3c56d6 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-size: 1.05rem;
    color: #000 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #4a6cf7 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h1>🎓 College Match & Affordability Planner</h1>", unsafe_allow_html=True)
st.markdown("A clean, modern, Lovable-style interface to find your perfect school.")

st.markdown("---")

# ---------------------------------------------------------
# TABS (Multi-Component UI)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Background",
    "2. Preferences",
    "3. Importance",
    "4. Results"
])

# ---------------------------------------------------------
# TAB 1 — BACKGROUND INFO
# ---------------------------------------------------------
with tab1:
    st.markdown("## 🧑‍🎓 Background Information")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        state_pref = st.selectbox("🌎 Preferred State", 
            ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])

        residency_pref = st.radio("🏠 Residency Type", 
            {"In-State": "in_state", "Out-of-State": "oos"})

    with col2:
        family_earnings = st.slider("💵 Family Annual Earnings", 
                                    0, 200000, 60000, step=5000)

        desired_degree = st.selectbox("🎓 Minimum Degree Level", list(DEGREE_ORDER.keys()))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2 — USER PREFERENCES
# ---------------------------------------------------------
with tab2:
    st.markdown("## ⭐ School Preferences")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        sector = st.selectbox("🏛️ School Sector", ["Public", "Private", "For-Profit"])
        locality = st.selectbox("📍 Campus Setting", ["City","Suburb","Town","Rural"])
        preferred_msi = st.selectbox("🏫 MSI Preference (optional)", ["none"] + MSI_CATEGORIES)

    with col2:
        total_enrollment = st.slider("👥 Enrollment Size Preference", 1000, 60000, 15000)
        admit_rate = st.slider("📊 Target Admit Rate (%)", 1, 100, 50) / 100
        student_faculty_ratio = st.slider("🧑‍🏫 Preferred Student–Faculty Ratio", 5, 25, 12)

    user_prefs = {
        "sector": sector,
        "locality": locality,
        "preferred_msi": None if preferred_msi == "none" else preferred_msi,
        "total_enrollment": total_enrollment,
        "admit_rate": admit_rate,
        "student_faculty_ratio": student_faculty_ratio
    }

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3 — IMPORTANCE WEIGHTS
# ---------------------------------------------------------
with tab3:
    st.markdown("## ⚖️ Factor Importance")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    user_weights = {
        "sector": st.slider("Sector Importance", 1, 5, 3),
        "locality": st.slider("Campus Setting Importance", 1, 5, 3),
        "msi": st.slider("MSI Preference Importance", 1, 5, 2),
        "total_enrollment": st.slider("Enrollment Size Importance", 1, 5, 3),
        "admit_rate": st.slider("Admit Rate Importance", 1, 5, 3),
        "student_faculty_ratio": st.slider("Faculty Ratio Importance", 1, 5, 3)
    }

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4 — RESULTS
# ---------------------------------------------------------
with tab4:
    st.markdown("## 🔍 Your Best College Matches")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    top_n = st.slider("How many colleges to show?", 5, 50, 20)

    if st.button("🔎 Generate Matches"):
        try:
            results = build_pipeline(
                state_pref,
                residency_pref,
                family_earnings,
                desired_degree,
                user_prefs,
                user_weights
            )
            output = display_output(results, top_n)
            st.dataframe(output, use_container_width=True)

        except Exception as e:
            st.error(f"Error generating matches: {e}")

    st.markdown("</div>", unsafe_allow_html=True)




