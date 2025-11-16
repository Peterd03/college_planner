import streamlit as st
import numpy as np
import pandas as pd

from main import (
    build_pipeline,
    display_output,
    MSI_CATEGORIES,
    DEGREE_ORDER
)

# ---------------------------------------------------------
# PAGE CONFIG (white background)
# ---------------------------------------------------------
st.set_page_config(page_title="College Planner", layout="wide")

st.markdown("""
<style>
html, body, .block-container {
    background-color: white !important;
    font-family: "Inter", sans-serif;
}

/* Section cards */
.section-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid #e0e0e0;
    margin-bottom: 26px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.04);
}

h1 {
    text-align: center;
    color: #1a237e;
    font-weight: 800;
    margin-bottom: -10px;
}

h2, h3 {
    color: #1a237e;
    font-weight: 700;
}

/* Streamlit button cleanup */
.stButton>button {
    background-color: #3949ab;
    color: white;
    padding: 0.7rem 1.4rem;
    font-size: 1rem;
    border-radius: 12px;
    border: none;
}
.stButton>button:hover {
    background-color: #283593;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("# 🎓 College Match & Affordability Planner")
st.markdown("### Answer a few questions — get your best-fit colleges instantly.")
st.markdown("---")


# ---------------------------------------------------------
# SECTION 1 — BACKGROUND
# ---------------------------------------------------------
st.markdown("## 🧑‍🎓 1. Your Background")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    state_pref = st.selectbox("🌎 Preferred State", 
                              ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])

    residency_pref = st.radio("🏠 Residency",
                              {"In-State": "in_state", "Out-of-State": "oos"})

    family_earnings = st.slider("💵 Family Annual Earnings", 
                                0, 200000, 60000, step=5000)

    desired_degree = st.selectbox("🎓 Minimum Degree Level", list(DEGREE_ORDER.keys()))

    st.write("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 2 — PREFERENCES
# ---------------------------------------------------------
st.markdown("## ⭐ 2. Your Preferences")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    sector = st.selectbox("🏛️ School Sector", ["Public","Private","For-Profit"])
    locality = st.selectbox("📍 Campus Setting", ["City","Suburb","Town","Rural"])
    preferred_msi = st.selectbox("🏫 MSI Preference", ["none"] + MSI_CATEGORIES)

    total_enrollment = st.slider("👥 Enrollment Size Preference", 1000, 60000, 15000)
    admit_rate = st.slider("📊 Target Admit Rate (%)", 1, 100, 50) / 100
    student_faculty_ratio = st.slider("🧑‍🏫 Student–Faculty Ratio Preference", 5, 25, 12)

    user_prefs = {
        "sector": sector,
        "locality": locality,
        "preferred_msi": None if preferred_msi == "none" else preferred_msi,
        "total_enrollment": total_enrollment,
        "admit_rate": admit_rate,
        "student_faculty_ratio": student_faculty_ratio
    }

    st.write("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 3 — IMPORTANCE WEIGHTS (SLIDERS)
# ---------------------------------------------------------
st.markdown("## ⚖️ 3. Factor Importance")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    user_weights = {
        "sector": st.slider("Sector Importance", 1, 5, 3),
        "locality": st.slider("Campus Setting Importance", 1, 5, 3),
        "msi": st.slider("MSI Importance", 1, 5, 2),
        "total_enrollment": st.slider("Enrollment Size Importance", 1, 5, 3),
        "admit_rate": st.slider("Admit Rate Importance", 1, 5, 3),
        "student_faculty_ratio": st.slider("Student–Faculty Ratio Importance", 1, 5, 3)
    }

    st.write("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 4 — RESULTS
# ---------------------------------------------------------
st.markdown("## 🔍 4. Show My Matches")

top_n = st.slider("Number of Colleges to Display", 5, 50, 20)

if st.button("🔎 Find My Colleges"):
    st.markdown("### 🎉 Your Best College Matches")

    try:
        results = build_pipeline(
            state_pref,
            residency_pref,
            family_earnings,
            desired_degree,
            user_prefs,
            user_weights
        )
        out = display_output(results, top_n)
        st.dataframe(out, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")



