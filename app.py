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
# PAGE CONFIG + FULL WHITE THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="College Planner",
    layout="wide"
)

# Inject custom CSS for white background + modern style
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: white !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    background-color: white !important;
}

h1 {
    text-align: center;
    font-weight: 800;
    color: #1e3a8a;
    letter-spacing: -0.5px;
}

.section-card {
    padding: 20px 24px;
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 26px;
}

/* WEIGHT BUTTONS */
.weight-container {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
}

.weight-btn {
    flex: 1;
    padding: 10px 0;
    margin-right: 8px;
    border-radius: 10px;
    border: 1px solid #cbd5e1;
    background: #f1f5f9;
    text-align: center;
    cursor: pointer;
    font-size: 16px;
    transition: 0.15s;
    font-weight: 600;
}

.weight-btn:hover {
    background: #dbeafe;
}

.weight-btn.selected {
    background: #2563eb !important;
    color: white !important;
    border-color: #1d4ed8 !important;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 17px;
    border: none;
    font-weight: 600;
    transition: 0.2s;
}

.stButton>button:hover {
    background-color: #1d4ed8;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CLEAN MODERN HEADER (NO ASCII)
# ---------------------------------------------------------
st.markdown("""
# 🎓 College Match & Affordability Planner
### Find the colleges that match your goals, preferences, and financial situation.
""")

st.markdown("---")


# ---------------------------------------------------------
# Weight Button Component
# ---------------------------------------------------------
def weight_buttons(label, key):
    st.write(f"**{label}**")

    if key not in st.session_state:
        st.session_state[key] = 3  # default importance

    cols = st.columns(5)

    # Render visual buttons and clickable overlays
    for i, col in enumerate(cols, start=1):

        # SELECTED BUTTON STYLE
        if st.session_state[key] == i:
            col.markdown(
                f"<div class='weight-btn selected'>{i}</div>", unsafe_allow_html=True
            )
        else:
            col.markdown(
                f"<div class='weight-btn'>{i}</div>", unsafe_allow_html=True
            )

        # INVISIBLE BUTTON HANDLE
        if col.button(" ", key=f"{key}_{i}"):
            st.session_state[key] = i

    return st.session_state[key]


# ---------------------------------------------------------
# SECTION 1 — STUDENT BACKGROUND
# ---------------------------------------------------------
st.markdown("## 🧑‍🎓 1. Your Background")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    state_pref = st.selectbox("🌎 Preferred Study State", 
                              ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])

    residency_pref = st.radio("🏠 Residency Status",
                              {"In-State": "in_state", "Out-of-State": "oos"})

    family_earnings = st.slider("💵 Annual Family Earnings", 0, 200000, 60000, step=5000)

    desired_degree = st.selectbox("🎓 Minimum Degree Level", list(DEGREE_ORDER.keys()))

    st.write("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 2 — PREFERENCES
# ---------------------------------------------------------
st.markdown("## ⭐ 2. Your Preferences")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    sector = st.selectbox("🏛️ School Sector Preference", ["Public", "Private", "For-Profit"])
    locality = st.selectbox("📍 Campus Setting", ["City", "Suburb", "Town", "Rural"])
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
# SECTION 3 — WEIGHT SLIDERS AS BUTTONS
# ---------------------------------------------------------
st.markdown("## ⚖️ 3. Importance Levels")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    user_weights = {
        "sector": weight_buttons("Sector Importance", "w_sector"),
        "locality": weight_buttons("Campus Setting Importance", "w_locality"),
        "msi": weight_buttons("MSI Importance", "w_msi"),
        "total_enrollment": weight_buttons("Enrollment Size Importance", "w_enroll"),
        "admit_rate": weight_buttons("Admit Rate Importance", "w_admit"),
        "student_faculty_ratio": weight_buttons("Student–Faculty Ratio Importance", "w_sfr")
    }

    st.write("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 4 — RUN TOOL
# ---------------------------------------------------------
st.markdown("## 🔍 4. View Your Top College Matches")

top_n = st.slider("Number of Colleges to Display", 5, 50, 20)

if st.button("🔎 Find My Colleges"):
    st.markdown("### 🎉 Your Best Matches")

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
        st.error(f"Error loading results: {e}")

