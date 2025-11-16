
import duckdb
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px

res_path = "Datathon_Fa25/data/College_Results.csv"
aff_path = "Datathon_Fa25/data/Affordability_Gap.csv"

aff_tbl = [
    "Unit ID", "Student Family Earnings Ceiling", "State Abbreviation", "City", "Sector Name", "Degree of Localization Name",
    "Cost of Attendance: In State", "Cost of Attendance: Out of State", "Net Price",
    "Weekly Hours to Close Gap","Weekly Hours to Close Gap: Center-Based Care",
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
    "Student Family Earnings Ceiling": "family_earnings_ceiling",
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


INCOME_THRESHOLDS = {
    30000: (0, 30000),
    48000: (30000, 48000),
    75000: (48000, 75000),
    110000: (75000, 110000),
    150000: (110000, 150000)
}

LOCALITY_SIM_MATRIX = {
    "City": {"City":1,"Suburb":0.7,"Town":0.3,"Rural":0.1},
    "Suburb":{"City":0.7,"Suburb":1,"Town":0.5,"Rural":0.3},
    "Town":{"City":0.3,"Suburb":0.5,"Town":1,"Rural":0.6},
    "Rural":{"City":0.1,"Suburb":0.3,"Town":0.6,"Rural":1}
}

MSI_CATEGORIES = ["hbcu", "aanapii", "nanti", "hsi", "tribal", "pbi", "annhi"]

DEGREE_ORDER = {
    "non-degree":0,
    "associate":1,
    "bachelor":2,
    "master":3,
    "doctoral":4,
    "na":-1
}

LOCALITY_DEGREE_MAP = {1:"City",2:"Suburb",3:"Town",4:"Rural"}

def normalize_degree_string(s):
    if not isinstance(s,str):
        return "na"
    x = s.lower()
    if "associate" in x:
        return "associate"
    if "bachelor" in x:
        return "bachelor"
    if "master" in x:
        return "master"
    if "doctor" in x or "phd" in x:
        return "doctoral"
    if "non-degree" in x:
        return "non-degree"
    if "not available" in x:
        return "na"
    return "na"

def load_affordability_data(path):
    con = duckdb.connect()
    cols = ", ".join(f'"{c}"' for c in aff_tbl)
    df = con.execute(f"SELECT {cols} FROM read_csv_auto('{path}')").df()
    df = df.rename(columns=aff_map)

    df["localization_degree"] = pd.to_numeric(df["localization_degree"], errors="coerce")
    df["locality"] = df["localization_degree"].map(LOCALITY_DEGREE_MAP)

    df["family_earnings_ceiling"] = pd.to_numeric(df["family_earnings_ceiling"], errors="coerce")

    df["family_earn_low"] = np.nan
    df["family_earn_high"] = np.nan

    for raw_val, (low, high) in INCOME_THRESHOLDS.items():
        mask = df["family_earnings_ceiling"] == raw_val
        df.loc[mask, "family_earn_low"] = low
        df.loc[mask, "family_earn_high"] = high

    numeric_cols = ["coa_in_state","coa_out_state","net_price","weekly_hours_gap","weekly_hours_gap_center"]
    for col in numeric_cols:
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
    cols = ", ".join(f'"{c}"' for c in res_tbl)
    df = con.execute(f"SELECT {cols} FROM read_csv_auto('{path}')").df()
    df = df.rename(columns=res_map)
    numeric = ["total_enrollment","admit_rate","student_faculty_ratio","median_earnings_10yr","grad_rate_4yr","retention_rate"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def filter_schools(df, state_pref, residency_pref, family_earnings, desired_degree):
    out = df.copy()

    if residency_pref == "in_state":
        out = out[out["state"] == state_pref]
    elif residency_pref == "oos":
        out = out[out["state"] != state_pref]

    if family_earnings is not None:
    
        # Case 1: Income fits inside documented bin
        matches = out[
            (out["family_earn_low"].notna()) &
            (out["family_earn_low"] <= family_earnings) &
            (family_earnings <= out["family_earn_high"])
        ]
    
        # Case 2: Income exceeds documented bins → keep highest bin per school
        if matches.empty:
            highest_rows = (
                out[out["family_earn_low"].notna()]
                .sort_values(["unitid", "family_earn_low"], ascending=[True, False])
                .drop_duplicates("unitid")
            )
            out = highest_rows
        else:
            catch_all = out[out["family_earn_low"].isna() & out["family_earn_high"].isna()]
            out = pd.concat([matches, catch_all], ignore_index=True)

    if desired_degree is not None:
        lvl = DEGREE_ORDER.get(desired_degree, -1)
        out = out[out["degree_level"] >= lvl]

    out = out.drop_duplicates(subset="unitid", keep="first")
    return out

def numeric_distance(value, target, data_min, data_max):
    return abs(value-target)/(data_max-data_min+1e-9)

def categorical_similarity(value, target, sim_matrix):
    if pd.isna(value) or pd.isna(target):
        return 1
    return 1 - sim_matrix.get(target,{}).get(value,0)

def msi_distance(row, preferred_msi):
    school_msis = [c for c in MSI_CATEGORIES if row.get(c,0)==1]
    if preferred_msi is None or preferred_msi == "none":
        if len(school_msis) == 0:
            return 0
        else:
            return 1

    if preferred_msi not in MSI_CATEGORIES:
        return 0
    school_pref = row.get(preferred_msi,0)==1
    if school_pref:
        return 0
    elif len(school_msis) == 0:
        return 1
    else:
        return 2

def compute_school_score(df, user_prefs, user_weights):
    numeric_features = ["total_enrollment","admit_rate","student_faculty_ratio"]
    bounds = {c:(df[c].min(),df[c].max()) for c in numeric_features}
    
    scores = []
    for _,row in df.iterrows():
        tw=0
        sw=0
        sec = 0 if row["sector"]==user_prefs["sector"] else 1
        tw+=sec*user_weights["sector"]; sw+=user_weights["sector"]
        loc = categorical_similarity(row["locality"],user_prefs["locality"],LOCALITY_SIM_MATRIX)
        tw+=loc*user_weights["locality"]; sw+=user_weights["locality"]
        msi = msi_distance(row,user_prefs["preferred_msi"])
        tw+=msi*user_weights["msi"]; sw+=user_weights["msi"]
        
        for f in numeric_features:
            if pd.isna(row[f]) or pd.isna(user_prefs[f]):
                d=1
            else:
                mn,mx=bounds[f]
                d=numeric_distance(row[f],user_prefs[f],mn,mx)
            tw+=d*user_weights[f]; sw+=user_weights[f]
        
        scores.append(tw/sw if sw>0 else np.nan)

    out=df.copy()
    out["distance_score"] = scores
    k = 6   # curvature; 6–10 is good range
    m = out["distance_score"].median()  # center point
    out["similarity_score"] = 1 / (1 + np.exp(k * (out["distance_score"] - m)))
    out = out.drop(columns=["distance_score"])
    return out.sort_values("similarity_score", ascending=False).reset_index(drop=True)

def _normalize_rate(series):
    s = series.astype(float)
    mask = s > 1
    s[mask] = s[mask] / 100.0
    return s

def compute_roi(df, state_pref, residency_pref):
    d = df.copy()

    g = _normalize_rate(d["grad_rate_4yr"])
    r = _normalize_rate(d["retention_rate"])
    a = _normalize_rate(d["admit_rate"])

    annual_cost = pd.Series(np.nan, index=d.index)

    if residency_pref == "in_state":
        in_mask = d["state"] == state_pref
        annual_cost[in_mask] = d.loc[in_mask, "coa_in_state"]
        annual_cost[~in_mask] = d.loc[~in_mask, "coa_out_state"]
    elif residency_pref == "oos":
        annual_cost = d["coa_out_state"]
    else:
        annual_cost = d["net_price"]

    annual_cost = annual_cost.fillna(d["net_price"])

    g_eff = g.copy()
    g_eff = g_eff.clip(lower=0.5)
    years = 4.0 / g_eff
    years = years.clip(upper=8.0)

    expected_cost = annual_cost * years

    earnings = d["median_earnings_10yr"].astype(float)
    earnings_factor = earnings * g * r
    signal_boost = 1.0 - a
    expected_earnings = earnings_factor * (1.0 + 0.25 * signal_boost)

    work = d["weekly_hours_gap"].fillna(0.0).astype(float)
    work_penalty = (work / 40.0).clip(lower=0.0, upper=1.0)

    roi_raw = (expected_earnings - expected_cost) / expected_cost.replace(0, np.nan)
    roi = roi_raw * (1.0 - work_penalty)

    d["roi"] =( roi - np.mean(roi)) / np.std(roi)
    d["roi"] = d["roi"].fillna(-99.9)
    return d

def build_pca_plot(df, user_prefs):
    numeric_features = ["total_enrollment","admit_rate","student_faculty_ratio"]

    df_numeric = df[numeric_features].astype(float)
    valid_mask = df_numeric.notna().all(axis=1)

    if valid_mask.sum() < 3:
        fig = px.scatter(title="Not enough numeric data for PCA visualization.")
        return fig

    X = df_numeric[valid_mask]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    coords = pca.fit_transform(X_scaled)

    df_plot = df.copy()
    df_plot["PC1"] = np.nan
    df_plot["PC2"] = np.nan
    df_plot.loc[valid_mask, "PC1"] = coords[:,0]
    df_plot.loc[valid_mask, "PC2"] = coords[:,1]

    user_vec = pd.DataFrame([user_prefs])[numeric_features].astype(float)

    for col in numeric_features:
        if np.isnan(user_vec[col].values[0]):
            user_vec[col] = X[col].median()

    user_scaled = scaler.transform(user_vec)
    user_coord = pca.transform(user_scaled)[0]

    fig = px.scatter(
        df_plot,
        x="PC1",
        y="PC2",
        hover_name="institution_name",
        color="similarity_score",
        color_continuous_scale="Viridis",
        title="College Landscape (PCA Projection)"
    )

    fig.add_scatter(
        x=[user_coord[0]],
        y=[user_coord[1]],
        mode="markers+text",
        marker=dict(size=18, symbol="star", color="red"),
        text=["YOU"],
        textposition="top center",
        name="Your Preference"
    )

    return fig

def build_pipeline(state_pref, residency_pref, family_earnings, desired_degree, user_prefs, user_weights):
    aff = load_affordability_data(aff_path)
    res = load_results_data(res_path)
    filtered = filter_schools(aff, state_pref, residency_pref, family_earnings, desired_degree)
    merged = pd.merge(filtered, res, on="unitid", how="inner").drop_duplicates("unitid")
    ranked = compute_school_score(merged, user_prefs, user_weights)
    ranked = compute_roi(ranked, state_pref, residency_pref)
    return ranked


def display_output(df, n=20):
    df = df.copy()
    df["msi_type"] = df.apply(
        lambda row: next((cat.upper() for cat in MSI_CATEGORIES if row.get(cat, 0) == 1), "None"),
        axis=1
    )
    df = df.sort_values("similarity_score", ascending=False).reset_index(drop=True)
    df["similarity_score"] = (df["similarity_score"] * 100).round(1).astype(str) + "%"
    return df[["similarity_score","roi","institution_name","state","city","msi_type","coa_in_state","coa_out_state",
               "total_enrollment","admit_rate","admissions_url"]]

