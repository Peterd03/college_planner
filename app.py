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
st.set_page_config(page_title="College Match Planner", layout="wide")

# ---------------------------------------------------------
# GLOBAL CSS — BEAUTIFUL LOVABLE-STYLE UI (WITH DROPDOWN FIX)
# ---------------------------------------------------------
st.markdown("""
<style>

html, body, .block-container {
    background-color: #ffffff !important;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4, label, p, div, span {
    color: #000000 !important;
}

/* Centered Content */
.center {
    max-width: 780px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 20px;
}

/* Nice Card */
.card {
    background: #ffffff;
    padding: 32px;
    border-radius: 22px;
    border: 1px solid #e5e5e5;
    margin-top: 35px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.06);
}

/* Buttons */
.stButton > button {
    width: 100%;
    background-color: #2563eb !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    font-size: 18px !important;
    border: none !important;
    transition: 0.2s ease-in-out;
}
.stButton > button:hover {
    background-color: #1d4ed8 !important;
}

/* ------------------------------------------------- */
/*           DROPDOWN / SELECTBOX FIXES              */
/* ------------------------------------------------- */

/* Main closed selectbox */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 10px !important;
    border: 1px solid #cccccc !important;
}

/* Dropdown menu container */
.stSelectbox div[data-baseweb="popover"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
    color: #000000 !important;
    border: 1px solid #cccccc !important;
}

/* Dropdown items */
.stSelectbox ul > li {
    background-color: #ffffff !important;
    color: #000000 !important;
    padding: 8px 14px !important;
    border-radius: 6px !important;
}

/* Hovered option */
.stSelectbox ul > li:hover {
    background-color: #eff6ff !important;
    color: #000000 !important;
}

/* Selected option inside dropdown */
.stSelectbox ul > li[data-selected="true"] {
    background-color: #dbeafe !important;
    color: #000000 !important;
}

/* Radio buttons text */
.stRadio div[role="radiogroup"] label {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE ROUTER (INSTANT)
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def goto(page):
    st.session_state.page = page


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if st.session_state.page == "home":

    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown("<h1>🎓 College Match Planner</h1>")
    st.markdown(
        "Find your perfect college match based on affordability, academics, and personal preferences."
    )

    if st.button("Start Survey →"):
        goto("survey")

    st.markdown("</div></div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SURVEY PAGE
# ---------------------------------------------------------
elif st.session_state.page == "survey":

    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # --------- Background Info ---------
    st.markdown("## 🧑‍🎓 Background Information")

    state_pref = st.selectbox("Preferred State", [
        "CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"
    ])

    residency_pref = st.radio(
        "Residency Preference",
        {"In-State":"in_state", "Out-of-State":"oos"}
    )

    family_earnings = st.slider(
        "Family Annual Earnings", 0, 200000, 60000, step=5000
    )

    desired_degree = st.selectbox(
        "Minimum Degree Level",
        list(DEGREE_ORDER.keys())
    )

    st.markdown("---")

    # --------- Preferences ---------
    st.markdown("## 🏫 School Preferences")

    sector = st.selectbox("School Sector", ["Public","Private","For-Profit"])
    locality = st.selectbox("Campus Setting", ["City","Suburb","Town","Rural"])
    preferred_msi = st.selectbox("MSI Preference", ["none"] + MSI_CATEGORIES)

    total_enrollment = st.slider("Enrollment Size Preference", 1000, 60000, 15000)
    admit_rate = st.slider("Target Admit Rate (%)", 1, 100, 50) / 100
    sfr = st.slider("Preferred Student–Faculty Ratio", 5, 25, 12)

    st.markdown("---")

    # --------- Weights ---------
    st.markdown("## ⚖️ Importance Ratings (1 = Low, 5 = High)")

    w_sector = st.slider("Sector Importance", 1, 5, 3)
    w_locality = st.slider("Campus Setting Importance", 1, 5, 3)
    w_msi = st.slider("MSI Importance", 1, 5, 2)
    w_enroll = st.slider("Enrollment Size Importance", 1, 5, 3)
    w_admit = st.slider("Admit Rate Importance", 1, 5, 3)
    w_sfr = st.slider("Student–Faculty Ratio Importance", 1, 5, 3)

    # --------- Submit Survey ---------
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
        goto("results")

    st.markdown("</div></div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# RESULTS PAGE
# ---------------------------------------------------------
elif st.session_state.page == "results":

    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown("## 🎯 Your College Matches")

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

        how_many = st.slider("How many colleges to show?", 5, 50, 20)
        out = display_output(results, how_many)

        st.dataframe(out, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating results: {e}")

    if st.button("← Back to Home"):
        goto("home")

    st.markdown("</div></div>", unsafe_allow_html=True)


