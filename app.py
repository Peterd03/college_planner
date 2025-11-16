import streamlit as st
import pandas as pd
from main import (
    build_pipeline,
    display_output,
    MSI_CATEGORIES,
    DEGREE_ORDER
)

# Page config
st.set_page_config(page_title="College Match Planner", layout="wide")

# CSS for styling
st.markdown("""
<style>
html, body, .block-container {
    background-color: white !important;
    font-family: "Inter", sans-serif;
}
h1, h2, h3 { color: #000000 !important; }
.card {
    background: #ffffff;
    padding: 24px 28px;
    border-radius: 16px;
    border: 1px solid #e0e0e0;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.04);
    margin-bottom: 26px;
}
.stButton>button {
    background-color: #4a6cf7 !important;
    color: white !important;
    padding: 0.7rem 1.4rem;
    border-radius: 12px;
    font-size: 1rem;
    border: none;
    transition: 0.2s ease;
}
.stButton>button:hover {
    background-color: #3c56d6 !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 🎓 College Match & Affordability Planner")
st.markdown("---")

# Tabs for components
tab_home, tab_survey, tab_results = st.tabs(["Home", "Take Survey", "Results"])

# --- HOME TAB ---
with tab_home:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## Welcome!\n\nClick the button below to start your college match survey.")
    if st.button("📝 Start Survey"):
        # Navigate to Survey tab
        st.experimental_set_query_params(page="survey")
    st.markdown("</div>", unsafe_allow_html=True)

# --- SURVEY TAB ---
with tab_survey:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 1. About You")
    state_pref = st.selectbox("Preferred State", ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])
    residency_pref = st.radio("Residency Status", {"In-State": "in_state", "Out-of-State": "oos"})
    family_earnings = st.slider("Family Annual Earnings", 0, 200000, 60000, step=5000)
    desired_degree = st.selectbox("Minimum Degree Level", list(DEGREE_ORDER.keys()))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 2. Your Preferences")
    sector = st.selectbox("School Sector", ["Public","Private","For-Profit"])
    locality = st.selectbox("Campus Setting", ["City","Suburb","Town","Rural"])
    preferred_msi = st.selectbox("MSI Preference", ["none"] + MSI_CATEGORIES)
    total_enrollment = st.slider("Enrollment Size Preference", 1000, 60000, 15000)
    admit_rate = st.slider("Target Admit Rate (%)", 1, 100, 50) / 100
    student_faculty_ratio = st.slider("Student–Faculty Ratio Preference", 5, 25, 12)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 3. Factor Importance")
    w_sector = st.slider("Sector Importance", 1, 5, 3)
    w_locality = st.slider("Campus Setting Importance", 1, 5, 3)
    w_msi = st.slider("MSI Importance", 1, 5, 2)
    w_enroll = st.slider("Enrollment Size Importance", 1, 5, 3)
    w_admit = st.slider("Admit Rate Importance", 1, 5, 3)
    w_sfr = st.slider("Student–Faculty Ratio Importance", 1, 5, 3)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("📊 See My Results"):
        # store responses in session state to use in results tab
        st.session_state["survey_complete"] = True
        st.session_state["state_pref"] = state_pref
        st.session_state["residency_pref"] = residency_pref
        st.session_state["family_earnings"] = family_earnings
        st.session_state["desired_degree"] = desired_degree
        st.session_state["user_prefs"] = {
            "sector": sector,
            "locality": locality,
            "preferred_msi": None if preferred_msi=="none" else preferred_msi,
            "total_enrollment": total_enrollment,
            "admit_rate": admit_rate,
            "student_faculty_ratio": student_faculty_ratio
        }
        st.session_state["user_weights"] = {
            "sector": w_sector,
            "locality": w_locality,
            "msi": w_msi,
            "total_enrollment": w_enroll,
            "admit_rate": w_admit,
            "student_faculty_ratio": w_sfr
        }
        st.experimental_set_query_params(page="results")

# --- RESULTS TAB ---
with tab_results:
    if st.session_state.get("survey_complete", False):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## 🎯 Your Top College Matches")
        try:
            results = build_pipeline(
                st.session_state["state_pref"],
                st.session_state["residency_pref"],
                st.session_state["family_earnings"],
                st.session_state["desired_degree"],
                st.session_state["user_prefs"],
                st.session_state["user_weights"]
            )
            output = display_output(results, st.slider("How many to display?", 5, 50, 20))
            st.dataframe(output, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating results: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## 🔍 No survey submitted yet")
        st.markdown("Please go to the ‘Take Survey’ tab and complete the questions to view your matches.")
        st.markdown("</div>", unsafe_allow_html=True)
