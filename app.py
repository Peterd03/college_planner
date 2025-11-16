import streamlit as st
import pandas as pd
import numpy as np
from main import build_pipeline, MSI_CATEGORIES, DEGREE_ORDER


st.title("College Match Recommendation Tool 🎓")
st.write("Answer the questions below to generate your personalized college match score.")


# -----------------------------------------------------------
#   SECTION 1: BASIC USER CONTEXT (STATE, RESIDENCY, DEGREE)
# -----------------------------------------------------------

st.header("1. Basic Information")

state_pref = st.selectbox(
	"Which state do you prefer to study in?",
	["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"]
)

residency_pref = st.radio(
	"Will you be applying as an in-state or out-of-state student?",
	{
		"In-State": "in_state",
		"Out-of-State": "oos"
	}
)

desired_degree = st.selectbox(
	"What is the minimum degree level you want the college to offer?",
	["bachelor","associate","master","doctoral","non-degree"]
)



# -----------------------------------------------------------
#   SECTION 2: USER PREFERENCES (THE VALUES)
# -----------------------------------------------------------

st.header("2. Your Preferences")

sector = st.selectbox(
	"Preferred school sector:",
	["Public","Private","For-Profit"]
)

locality = st.selectbox(
	"What type of campus setting do you prefer?",
	["City","Suburb","Town","Rural"]
)

preferred_msi = st.selectbox(
	"Would you prefer a Minority Serving Institution (MSI)?",
	["none"] + MSI_CATEGORIES
)


# ---- numeric preferences ----
total_enrollment = st.slider(
	"Preferred total undergraduate enrollment:",
	500, 70000, 15000
)

admit_rate = st.slider(
	"Preferred admit rate (%):",
	1, 100, 50
) / 100  # convert to decimal for model

student_faculty_ratio = st.slider(
	"Preferred student-to-faculty ratio:",
	5, 30, 12
)


# Bundle prefs exactly the way your backend expects
user_prefs = {
	"sector": sector,
	"locality": locality,
	"preferred_msi": preferred_msi if preferred_msi != "none" else "",
	"total_enrollment": total_enrollment,
	"admit_rate": admit_rate,
	"student_faculty_ratio": student_faculty_ratio
}



# -----------------------------------------------------------
#   SECTION 3: IMPORTANCE WEIGHTS (THE WEIGHTS)
# -----------------------------------------------------------

st.header("3. How important are these factors to you?")
st.write("Rate each factor from 1 (low importance) to 5 (very high importance).")

user_weights = {
	"sector": st.slider("Importance of school sector", 1, 5, 3),
	"locality": st.slider("Importance of campus setting", 1, 5, 3),
	"msi": st.slider("Importance of MSI designation", 1, 5, 2),
	"total_enrollment": st.slider("Importance of enrollment size", 1, 5, 3),
	"admit_rate": st.slider("Importance of admit rate", 1, 5, 3),
	"student_faculty_ratio": st.slider("Importance of student-faculty ratio", 1, 5, 3)
}



# -----------------------------------------------------------
#   SECTION 4: OUTPUT SETTINGS
# -----------------------------------------------------------

top_n = st.slider("How many colleges would you like to see?", 5, 50, 10)



# -----------------------------------------------------------
#   RUN PIPELINE
# -----------------------------------------------------------

if st.button("Find My Best Colleges"):
	st.write("### Your Top Matching Colleges")

	results = build_pipeline(
		state_pref,
		residency_pref,
		desired_degree,
		user_prefs,
		user_weights,
		top_n
	)

	if results is None or len(results) == 0:
		st.warning("No colleges matched your filters.")
	else:
		st.dataframe(results[["institution_name", "match_score"]], use_container_width=True)

