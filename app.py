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
st.set_page_config(page_title="College Planner", layout="wide")

# ---------------------------------------------------------
# CSS (LOVABLE-STYLE)
# ---------------------------------------------------------
st.markdown("""
<style>

html, body, .block-container {
    background-color: white !important;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, p, div, label {
    color: #111 !important;
}

/* Center Cards */
.centered {
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

/* Pretty Cards */
.card {
    background: #ffffff;
    padding: 32px;
    border-radius: 22px;
    box-shadow: 0 4px 25px rgba(0,0,0,0.07);
    border: 1px solid #eee;
    margin-top: 40px;
}

/* Beautiful Button */
.stButton > button {
    width: 100%;
    background-color: #3b82f6;
    color: white !important;
    padding: 14px 20px;
    font-size: 18px;
    border-radius: 12px;
    border: none;
    transition: 0.15s ease;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}

/* Hide default Streamlit tabs from rerendering */
.block-container {
    padding-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE ROUTER
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page_name):
    st.session_state.page = page_name


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if st.session_state.page == "home":
    st.markdown("<div class='centered'>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("# 🎓 College Match Planner")
    st.markdown("Welcome! This tool will help you find colleges that fit your academic, financial, and personal preferences.")

    if st.button("Start Survey →"):
        go("survey")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SURVEY PAGE
# ---------------------------------------------------------
elif st.session_state.page == "survey":

    st.markdown("<div class='centered'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown("## 🧑‍🎓 Tell Us About Yourself")

    # --- Section 1
    st.markdown("### Background")

    state_pref = st.selectbox("Preferred State", ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])
    residency_pref = st.radio("Residency Preference", {"In-State": "in_state", "Out-of-State": "oos"})
    family_earnings = st.slider("Family Annual Earnings", 0, 200000, 60000, step=5000)
    desired_degree = st.selectbox("Minimum Degree Level", list(DEGREE_ORDER.keys()))

    st.markdown("---")
    st.markdown("### School Preferences")

    sector = st.selectbox("School Sector", ["Public","Private","For-Profit"])
    locality = st.selectbox("Campus Setting", ["City","Suburb","Town","Rural"])
    preferred_msi = st.selectbox("MSI Preference", ["none"] + MSI_CATEGORIES)
    total_enrollment = st.slider("Preferred Enrollment Size", 1000, 60000, 15000)
    admit_rate = st.slider("Preferred Admit Rate (%)", 1, 100, 50) / 100
    sfr = st.slider("Preferred Student–Faculty Ratio", 5, 25, 12)

    st.markdown("---")
    st.markdown("### Importance Rating (1 = Low, 5 = High)")

    w_sector = st.slider("Sector Importance", 1, 5, 3)
    w_locality = st.slider("Campus Setting Importance", 1, 5, 3)
    w_msi = st.slider("MSI Importance", 1, 5, 2)
    w_enroll = st.slider("Enrollment Size Importance", 1, 5, 3)
    w_admit = st.slider("Admit Rate Importance", 1, 5, 3)
    w_sfr = st.slider("Student–Faculty Ratio Importance", 1, 5, 3)

    # ---- Submit Survey
    if st.button("See Results →"):
        st.session_state.survey = {
            "state_pref": state_pref,
            "residency_pref": residency_pref,
            "family_earnings": family_earnings,
            "desired_degree": desired_degree,
            "user_prefs": {
                "sector": sector,
                "locality": locality,
                "preferred_msi": None if preferred_msi=="none" else preferred_msi,
                "total_enrollment": total_enrollment,
                "admit_rate": admit_rate,
                "student_faculty_ratio": sfr
            },
            "user_weights": {
                "sector": w_sector,
                "locality": w_locality,
                "msi": w_msi,
                "total_enrollment": w_enroll,
                "admit_rate": w_admit,
                "student_faculty_ratio": w_sfr
            }
        }
        go("results")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# RESULTS PAGE
# ---------------------------------------------------------
elif st.session_state.page == "results":

    st.markdown("<div class='centered'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown("## 🎯 Your Matches")

    s = st.session_state.survey
    try:
        results = build_pipeline(
            s["state_pref"],
            s["residency_pref"],
            s["family_earnings"],
            s["desired_degree"],
            s["user_prefs"],
            s["user_weights"]
        )
        top_n = st.slider("How many colleges to display?", 5, 50, 20)
        output = display_output(results, top_n)
        st.dataframe(output, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("← Back to Home"):
        go("home")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

