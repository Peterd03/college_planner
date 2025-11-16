import streamlit as st
import pandas as pd
import numpy as np

# Import your backend logic from main.py
from main import (
	build_pipeline,
	display_output,
	MSI_CATEGORIES,
	DEGREE_ORDER,
)

# ------------------------------------------------------------
#       PAGE CONFIG + CUSTOM WHITE THEME
# ------------------------------------------------------------
st.set_page_config(
	page_title="College Planner",
	layout="centered"
)

# Inject CSS for cleaner white UI + stylized headers
st.markdown("""
	<style>
		body {
			background-color: white !important;
		}
		.block-container {
			padding-top: 2rem;
			padding-bottom: 5rem;
		}
		h1, h2, h3 {
			color: #1e3d7b !important;
			font-weight: 700 !important;
		}
		.logo {
			font-family: monospace;
			font-size: 14px;
			white-space: pre;
			line-height: 1.1;
			color: #1e3d7b;
		}
		.section-box {
			padding: 1.2rem;
			border-radius: 10px;
			border: 1px solid #e6e6e6;
			background-color: #fafafa;
			margin-bottom: 1.5rem;
		}
		</style>
""", unsafe_allow_html=True)



# ------------------------------------------------------------
#                  LOGO  (ASCII BANNER)
# ------------------------------------------------------------
st.markdown(
	"""
	<div class="logo">
   ___      _ _       _                ____  _                              
  / __| ___| | | __ _| |_ ___ _ _     |  _ \\| | __ _ _ __   __ _  ___ _ __  
  \\__ \\/ -_) | |/ _` |  _/ -_) '_|____| |_) | |/ _` | '_ \\ / _` |/ _ \\ '_ \\ 
  |___/\\___|_|_|\\__,_|\\__\\___|_|_____|  __/|_|\\__,_| | | | (_| |  __/ | | |
                                      |_|             |_| |_|\\__,_|\\___|_| |_|
                                      
                      COLLEGE MATCH & AFFORDABILITY PLANNER
	</div>
	""",
	unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SECTION 1: USER BACKGROUND
# ============================================================
st.markdown("## 🧑‍🎓 1. About You")

with st.container():
	st.markdown('<div class="section-box">', unsafe_allow_html=True)

	state_pref = st.selectbox(
		"🌎 Which state do you want to study in?",
		["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"]
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
		["bachelor","associate","master","doctoral","non-degree"]
	)

	st.markdown('</div>', unsafe_allow_html=True)



# ============================================================
# SECTION 2: USER PREFERENCES
# ============================================================
st.markdown("## ⭐ 2. Your Preferences")

with st.container():
	st.markdown('<div class="section-box">', unsafe_allow_html=True)

	sector = st.selectbox("🏛️ Preferred School Sector", ["Public","Private","For-Profit"])

	locality = st.selectbox("📍 Preferred Campus Setting", ["City","Suburb","Town","Rural"])

	preferred_msi = st.selectbox(
		"🏫 Do you prefer an MSI (Minority Serving Institution)?",
		["none"] + MSI_CATEGORIES
	)

	total_enrollment = st.slider("👥 Ideal Total Enrollment Size", 1000, 60000, 15000)

	admit_rate = st.slider("📊 Preferred Admit Rate (%)", 1, 100, 50) / 100

	student_faculty_ratio = st.slider("🧑‍🏫 Student-to-Faculty Ratio", 5, 25, 12)

	user_prefs = {
		"sector": sector,
		"locality": locality,
		"preferred_msi": preferred_msi if preferred_msi != "none" else None,
		"total_enrollment": total_enrollment,
		"admit_rate": admit_rate,
		"student_faculty_ratio": student_faculty_ratio
	}

	st.markdown('</div>', unsafe_allow_html=True)



# ============================================================
# SECTION 3: WEIGHTS
# ============================================================
st.markdown("## ⚖️ 3. Factor Importance")

with st.container():
	st.markdown('<div class="section-box">', unsafe_allow_html=True)

	user_weights = {
		"sector": st.slider("Sector Importance", 1, 5, 3),
		"locality": st.slider("Campus Setting Importance", 1, 5, 3),
		"msi": st.slider("MSI Importance", 1, 5, 2),
		"total_enrollment": st.slider("Enrollment Size Importance", 1, 5, 3),
		"admit_rate": st.slider("Admit Rate Importance", 1, 5, 3),
		"student_faculty_ratio": st.slider("Student-Faculty Ratio Importance", 1, 5, 3)
	}

	st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SECTION 4: RESULTS SETTINGS
# ============================================================
st.markdown("## 🔍 4. Results Settings")

top_n = st.slider("Number of Colleges to Display", 5, 50, 20)


# ============================================================
# SECTION 5: RUN PIPELINE
# ============================================================
st.markdown("---")
if st.button("🔎 Find My Best Colleges"):
	st.write("### 🎉 Your Personalized College Matches")

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
		st.error(f"❌ Error: {e}")


