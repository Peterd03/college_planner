import streamlit as st
import duckdb
import pandas as pd
import numpy as np


# -----------------------------------------------------
#   ORIGINAL BACKEND LOGIC (UNMODIFIED)
# -----------------------------------------------------

aff_tbl = [
	"Unit ID", "State Abbreviation", "City", "Sector Name", "Degree of Localization Name",
	"Cost of Attendance: In State", "Cost of Attendance: Out of State", "Net Price",
	"Weekly Hours to Close Gap", "Weekly Hours to Close Gap: Center-Based Care",
	"Admissions Website", "HBCU", "PBI", "ANNHI", "TRIBAL", "AANAPII", "HSI", "NANTI",
	"Highest Degree Offered Name"
]

res_tbl = [
	"UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION", "Institution Name", "Total Enrollment",
	"Total Percent of Applicants Admitted", "Student-to-Faculty Ratio",
	"Median Earnings of Students Working and Not Enrolled 10 Years After Entry",
	"Bachelor's Degree Graduation Rate Within 4 Years - Total", "First-Time, Full-Time Retention Rate"
]

aff_map = {
	"Unit ID": "unitid",
	"State Abbreviation": "state",
	"City": "city",
	"Sector Name": "sector",
	"Degree of Localization Name": "localization_degree",
	"Cost of Attendance: In State": "coa_in_state",
	"Cost of Attendance: Out of State": "coa_out_state",
	"Net Price": "net_price",
	"Weekly Hours to Close Gap": "weekly_hours_gap",
	"Weekly Hours to Close Gap: Center-Based Care": "weekly_hours_gap_center",
	"Admissions Website": "admissions_url",
	"HBCU": "hbcu",
	"PBI": "pbi",
	"ANNHI": "annhi",
	"TRIBAL": "tribal",
	"AANAPII": "aanapii",
	"HSI": "hsi",
	"NANTI": "nanti",
	"Highest Degree Offered Name": "highest_deg"
}

res_map = {
	"UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION": "unitid",
	"Institution Name": "institution_name",
	"Total Enrollment": "total_enrollment",
	"Total Percent of Applicants Admitted": "admit_rate",
	"Student-to-Faculty Ratio": "student_faculty_ratio",
	"Median Earnings of Students Working and Not Enrolled 10 Years After Entry": "median_earnings_10yr",
	"Bachelor's Degree Graduation Rate Within 4 Years - Total": "grad_rate_4yr",
	"First-Time, Full-Time Retention Rate": "retention_rate"
}

res_path = "data/College_Results.csv"
aff_path = "data/Affordability_Gap.csv"

LOCALITY_SIM_MATRIX = {
	"City": {"City": 1, "Suburb": 0.7, "Town": 0.3, "Rural": 0.1},
	"Suburb": {"City": 0.7, "Suburb": 1, "Town": 0.5, "Rural": 0.3},
	"Town": {"City": 0.3, "Suburb": 0.5, "Town": 1, "Rural": 0.6},
	"Rural": {"City": 0.1, "Suburb": 0.3, "Town": 0.6, "Rural": 1}
}

MSI_CATEGORIES = ["hbcu", "aanapii", "nanti", "hsi", "tribal", "pbi", "annhi"]

DEGREE_ORDER = {
	"non-degree": 0,
	"associate": 1,
	"bachelor": 2,
	"master": 3,
	"doctoral": 4,
	"na": -1
}

LOCALITY_DEGREE_MAP = {1: "City", 2: "Suburb", 3: "Town", 4: "Rural"}


def normalize_degree_string(s):
	if not isinstance(s, str):
		return "na"
	x = s.lower()
	if "associate" in x: return "associate"
	if "bachelor" in x: return "bachelor"
	if "master" in x: return "master"
	if "doctor" in x or "phd" in x: return "doctoral"
	if "non-degree" in x: return "non-degree"
	if "not available" in x: return "na"
	return "na"


def load_affordability_data(path):
	con = duckdb.connect()
	cols = ", ".join([f'"{c}"' for c in aff_tbl])
	df = con.execute(f"SELECT {cols} FROM read_csv_auto('{path}')").df()
	df = df.rename(columns=aff_map)

	df["localization_degree"] = pd.to_numeric(df["localization_degree"], errors="coerce")
	df["locality"] = df["localization_degree"].map(LOCALITY_DEGREE_MAP)
	df["family_earnings_ceiling"] = np.nan

	for col in ["coa_in_state","coa_out_state","net_price","weekly_hours_gap","weekly_hours_gap_center"]:
		df[col] = pd.to_numeric(df[col], errors="coerce")

	df["highest_deg_norm"] = df["highest_deg"].apply(normalize_degree_string)
	df["degree_level"] = df["highest_deg_norm"].map(DEGREE_ORDER).fillna(-1).astype(int)

	for col in MSI_CATEGORIES:
		if col not in df.columns:
			df[col] = 0
		df[col] = df[col].fillna(0).astype(int)

	return df


def load_results_data(path):
	con = duckdb.connect()
	cols = ", ".join([f'"{c}"' for c in res_tbl])
	df = con.execute(f"SELECT {cols} FROM read_csv_auto('{path}')").df()
	df = df.rename(columns=res_map)

	for col in ["total_enrollment","admit_rate","student_faculty_ratio","median_earnings_10yr","grad_rate_4yr","retention_rate"]:
		df[col] = pd.to_numeric(df[col], errors="coerce")

	return df


def filter_schools(df, state_pref, residency_pref, desired_degree):
	out = df.copy()
	if residency_pref == "in_state": out = out[out["state"] == state_pref]
	elif residency_pref == "oos": out = out[out["state"] != state_pref]

	if desired_degree is not None:
		out = out[out["degree_level"] >= DEGREE_ORDER.get(desired_degree, -1)]
	return out


def numeric_distance(value, target, mn, mx):
	return abs(value - target) / (mx - mn + 1e-9)


def categorical_similarity(value, target, sim_matrix):
	if pd.isna(value) or pd.isna(target): return 1
	return 1 - sim_matrix.get(target, {}).get(value, 0)


def msi_distance(row, preferred_msi):
	if preferred_msi not in MSI_CATEGORIES: return 0
	if row.get(preferred_msi, 0) == 1: return 0
	if sum([row.get(c, 0) for c in MSI_CATEGORIES]) == 0: return 1
	return 2


def compute_school_score(df, user_prefs, user_weights):
	numeric_features = ["total_enrollment","admit_rate","student_faculty_ratio"]
	bounds = {c: (df[c].min(), df[c].max()) for c in numeric_features}

	scores = []
	for _, row in df.iterrows():
		tw = s = 0
		
		sec = 0 if row["sector"] == user_prefs["sector"] else 1
		tw += sec * user_weights["sector"]; s += user_weights["sector"]

		loc = categorical_similarity(row["locality"], user_prefs["locality"], LOCALITY_SIM_MATRIX)
		tw += loc * user_weights["locality"]; s += user_weights["locality"]

		msi = msi_distance(row, user_prefs["preferred_msi"])
		tw += msi * user_weights["msi"]; s += user_weights["msi"]

		for f in numeric_features:
			if pd.isna(row[f]) or pd.isna(user_prefs[f]): d = 1
			else: d = numeric_distance(row[f], user_prefs[f], *bounds[f])
			tw += d * user_weights[f]; s += user_weights[f]

		scores.append(tw / s if s > 0 else np.nan)

	df = df.copy()
	df["match_score"] = scores
	return df.sort_values("match_score").reset_index(drop=True)


def build_pipeline(state_pref, residency_pref, desired_degree, user_prefs, user_weights, top_n=10):
	aff = load_affordability_data(aff_path)
	res = load_results_data(res_path)
	filtered = filter_schools(aff, state_pref, residency_pref, desired_degree)
	merged = pd.merge(filtered, res, on="unitid", how="inner")
	return compute_school_score(merged, user_prefs, user_weights).head(top_n)


# -----------------------------------------------------
#         STREAMLIT UI
# -----------------------------------------------------

st.title("College Match Finder 🎓")
st.write("Answer the questions below to find your best-fit colleges.")

# ---- Survey Questions ----

state_pref = st.selectbox("Preferred Study State:", ["CA","NY","TX","FL","WA","MA","IL","GA","NC","VA","Other"])
residency_pref = st.radio("Residency Status:", {"In-State": "in_state", "Out-of-State": "oos"})
desired_degree = st.selectbox("Minimum Degree Level:", ["bachelor","associate","master","doctoral","non-degree"])

sector = st.selectbox("Preferred School Sector:", ["Public","Private","For-Profit"])
locality = st.selectbox("Preferred Campus Setting:", ["City","Suburb","Town","Rural"])
preferred_msi = st.selectbox("Preferred MSI Category:", ["none"] + MSI_CATEGORIES)

enrollment = st.slider("Preferred Total Enrollment Size", 500, 70000, 15000)
admit_rate = st.slider("Preferred Admit Rate (%)", 1, 100, 50) / 100
ratio = st.slider("Student-Faculty Ratio Preference", 5, 30, 12)

user_prefs = {
	"sector": sector,
	"locality": locality,
	"preferred_msi": preferred_msi if preferred_msi != "none" else "",
	"total_enrollment": enrollment,
	"admit_rate": admit_rate,
	"student_faculty_ratio": ratio
}

st.header("Importance Weights (1 = low, 5 = high)")

user_weights = {
	"sector": st.slider("Sector Importance", 1, 5, 3),
	"locality": st.slider("Locality Importance", 1, 5, 3),
	"msi": st.slider("MSI Importance", 1, 5, 2),
	"total_enrollment": st.slider("Enrollment Importance", 1, 5, 3),
	"admit_rate": st.slider("Admit Rate Importance", 1, 5, 3),
	"student_faculty_ratio": st.slider("Student-Faculty Ratio Importance", 1, 5, 3)
}

top_n = st.slider("Number of Colleges to Return:", 5, 50, 10)

# ---- Run Pipeline ----
if st.button("Find My Colleges"):
	results = build_pipeline(state_pref, residency_pref, desired_degree, user_prefs, user_weights, top_n)
	st.write("### Best Matches")
	st.dataframe(results[["institution_name", "match_score"]], use_container_width=True)
