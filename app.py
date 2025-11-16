import streamlit as st
import pandas as pd
import numpy as np

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
# GOOGLE-FORMS STYLE CSS
# ---------------------------------------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    background: white !important;
    font-family: "Inter", sans-serif;
}

/* Main heading */
h1 {
    text-align: center;
    color: #1a237e;
    font-weight: 800;
    margin-bottom: 0px;
}
h3, h2 {
    color: #1a237e;
    font-weight: 700;
}

/* Section Card */
.section-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid #e0e0e0;
    margin-bottom: 26px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

/* Clean Form Labels */
label {
    font-size: 1rem !important;
    color: #1a237e !important;
}

/* GOOGLE FORMS BUTTONS */
.choice-btn {
    padding: 10px 18px;
    border-radius: 20px;
    border: 1.5px solid #cccccc;
    background: #f5f5f5;
    cursor: pointer;
    font-size: 15px;
    text-align: center;
    transition: all 0.15s ease;
    user-select: none;
}

.choice-btn:hover {
    background: #e8e8e8;
}

.choice-btn.selected {
    background: #3f51b5 !important;
    color: white !important;
    border-color: #303f9f !important;
}

/* Make Streamlit buttons look clean */
.stButton>button {
    background: #3f51b5;
    color: white;
    padding: 0.7rem 1.4rem;
    font-size: 1.1rem;
    border-radius: 10px;
    border: none;
}
.stButton>button:hover {
    background: #303f9f;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# UI TITLE
# ---------------------------------------------------------
st.markdown("# 🎓 College Match & Affordability Planner")
st.markdown("### Answer a few questions — get your best-fit colleges instantly.")
st.markdown("---")

# ---------------------------------------------------------
# GOOGLE-FORMS STYLE BUTTON FUNCTION
# ---------------------------------------------------------
def google_choice(label, key, options):
    st.write(f"**{label}**")
    if key not in st.session_state:
        st.session_state[key] = options[0]

    cols = st.columns(len(options))

    for i, opt in enumerate(options):
        with cols[i]:
            selected = st.session_state[key] == opt

            # Selected or unselected style
            style_class = "choice-btn selected" if selected else "choice-btn"
            st.markdown(f"""
                <div class="{style_class}">{opt}</div>
            """, unsafe_allow_html=True)

            # Hidden click handler
            if st.button(" ", key=f"{key}_{i}"):
                st.session_state[key] = opt

    return st.session_state[key]

# ---------------------------------------------------------
# SECTION 1 — BACKGROUND
# ---------------------------------------------------------
st.markdown("## 🧑‍🎓 1. About You")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    state_pref = st.selectbox("🌎 Preferred State", ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])

    residency_pref = st.radio("🏠 Residency",
                              {"In-State": "in_state", "Out-of-State": "oos"})

    family_earnings = st.slider("💵 Family Annual Earnings", 0, 200000, 60000, step=5000)

    desired_degree = st.selectbox("🎓 Minimum Degree Level", list(DEGREE_ORDER.keys()))

    st.write("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 2 — PREFERENCES
# ---------------------------------------------------------
st.markdown("## ⭐ 2. Your Preferences")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    sector = st.selectbox("🏛️ Preferred School Sector", ["Public","Private","For-Profit"])
    locality = st.selectbox("📍 Campus Setting", ["City","Suburb","Town","Rural"])
    preferred_msi = st.selectbox("🏫 MSI Preference", ["none"] + MSI_CATEGORIES)

    total_enrollment = st.slider("👥 Enrollment Size Preference", 1000, 60000, 15000)
    admit_rate = st.slider("📊 Target Admit Rate (%)", 1, 100, 50) / 100
    student_faculty_ratio = st.slider("🧑‍🏫 Student-Faculty Ratio Preference", 5, 25, 12)

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
# SECTION 3 — GOOGLE-FORMS STYLE WEIGHTS
# ---------------------------------------------------------
st.markdown("## ⚖️ 3. Factor Importance (Click One)")
with st.container():
    st.write("<div class='section-card'>", unsafe_allow_html=True)

    user_weights = {
        "sector": google_choice("Sector Importance", "w_sector", ["1","2","3","4","5"]),
        "locality": google_choice("Campus Setting Importance", "w_locality", ["1","2","3","4","5"]),
        "msi": google_choice("MSI Importance", "w_msi", ["1","2","3","4","5"]),
        "total_enrollment": google_choice("Enrollment Size Importance", "w_enroll", ["1","2","3","4","5"]),
        "admit_rate": google_choice("Admit Rate Importance", "w_admit", ["1","2","3","4","5"]),
        "student_faculty_ratio": google_choice("Student–Faculty Ratio Importance", "w_sfr", ["1","2","3","4","5"])
    }

    st.write("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------
st.markdown("## 🔍 4. Show My College Matches")
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
            {k: int(v) for k, v in user_weights.items()}
        )
        out = display_output(results, top_n)
        st.dataframe(out, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")


