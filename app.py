import streamlit as st
import pandas as pd
import numpy as np

from main import (
    build_pipeline,
    display_output,
    MSI_CATEGORIES,
    DEGREE_ORDER
)

# ============================================================
# PAGE CONFIG + WHITE THEME
# ============================================================
st.set_page_config(
    page_title="College Planner",
    layout="centered"
)

# Inject CSS for custom styling
st.markdown("""
<style>

body {
    background-color: white !important;
}

.block-container {
    padding-top: 2rem !important;
}

h1, h2, h3 {
    color: #1e3a8a !important;
    font-weight: 700 !important;
}

.section-card {
    padding: 1.3rem 1.5rem;
    border-radius: 12px;
    background: #fafafa;
    border: 1px solid #e5e7eb;
    margin-bottom: 1.3rem;
}

.button-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.4rem;
}

.button-row button {
    flex-grow: 1;
}

.logo {
    white-space: pre;
    font-family: monospace;
    font-size: 14px;
    color: #1e3a8a;
    line-height: 1.1;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# ASCII LOGO
# ============================================================
st.markdown("""
<div class="logo">
   ___      _ _       _                ____  _                              
  / __| ___| | | __ _| |_ ___ _ _     |  _ \\| | __ _ _ __   __ _  ___ _ __  
  \\__ \\/ -_) | |/ _` |  _/ -_) '_|____| |_) | |/ _` | '_ \\ / _` |/ _ \\ '_ \\ 
  |___/\\___|_|_|\\__,_|\\__\\___|_|_____|  __/|_|\\__,_| | | | (_| |  __/ | | |
                                      |_|             |_| |_|\\__,_|\\___|_| |_|
                                      
                 COLLEGE MATCH & AFFORDABILITY PLANNER
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# Helper function for 1–5 button selector
def weight_selector(label, key):
    st.write(f"**{label}**")
    cols = st.columns(5)
    selected = st.session_state.get(key, 3)

    for i, col in enumerate(cols, start=1):
        if col.button(str(i), key=f"{key}_{i}"):
            st.session_state[key] = i
            selected = i

    return selected


# ============================================================
# SECTION 1 — YOUR BACKGROUND
# ============================================================
st.markdown("## 🧑‍🎓 1. About You")
with st.container():
    st.write('<div class="section-card">', unsafe_allow_html=True)

    state_pref = st.selectbox(
        "🌎 Which state do you want to study in?",
        ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"],
        index=0
    )

    residency_pref = st.radio(
        "🏠 Will you apply as:",
        {
            "In-State Student": "in_state",
            "Out-of-State Student": "oos"
        }
    )

    family_earnings = st.slider(
        "💵 Estimated Family Annual Earnings",
        0, 200000, 60000, step=5000
    )

    desired_degree = st.selectbox(
        "🎓 Minimum Degree Level",
        list(DEGREE_ORDER.keys()),
        index=2
    )

    st.write('</div>', unsafe_allow_html=True)


# ============================================================
# SECTION 2 — PREFERENCES
# ============================================================
st.markdown("## ⭐ 2. Your Preferences")
with st.container():
    st.write('<div class="section-card">', unsafe_allow_html=True)

    sector = st.selectbox("🏛️ Preferred School Sector:", ["Public","Private","For-Profit"])

    locality = st.selectbox("📍 Preferred Campus Setting:", ["City","Suburb","Town","Rural"])

    preferred_msi = st.selectbox(
        "🏫 MSI Preference:",
        ["none"] + MSI_CATEGORIES
    )

    total_enrollment = st.slider("👥 Total Enrollment Preference", 1000, 60000, 15000)

    admit_rate = st.slider("📊 Preferred Admit Rate (%)", 1, 100, 50) / 100

    student_faculty_ratio = st.slider("🧑‍🏫 Student–Faculty Ratio", 5, 25, 12)

    user_prefs = {
        "sector": sector,
        "locality": locality,
        "preferred_msi": preferred_msi if preferred_msi != "none" else None,
        "total_enrollment": total_enrollment,
        "admit_rate": admit_rate,
        "student_faculty_ratio": student_faculty_ratio
    }

    st.write('</div>', unsafe_allow_html=True)



# ============================================================
# SECTION 3 — WEIGHTS (BUTTONS 1–5)
# ============================================================
st.markdown("## ⚖️ 3. How Important Are These Factors?")
with st.container():
    st.write('<div class="section-card">', unsafe_allow_html=True)

    user_weights = {
        "sector": weight_selector("Sector (Public vs Private)", "w_sector"),
        "locality": weight_selector("Campus Setting (City/Suburb/Town/Rural)", "w_locality"),
        "msi": weight_selector("Minority Serving Institution Match", "w_msi"),
        "total_enrollment": weight_selector("Enrollment Size", "w_enroll"),
        "admit_rate": weight_selector("Admit Rate", "w_admit"),
        "student_faculty_ratio": weight_selector("Student–Faculty Ratio", "w_sfr")
    }

    st.write('</div>', unsafe_allow_html=True)


# ============================================================
# SECTION 4 — RESULTS SETTINGS
# ============================================================
st.markdown("## 🔍 4. Result Settings")
top_n = st.slider("Number of Colleges to Show:", 5, 50, 20)


# ============================================================
# SECTION 5 — RUN THE MODEL
# ============================================================
st.markdown("---")

if st.button("🔎 Find My Best College Matches"):
    st.write("### 🎉 Your Top Matches")

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
