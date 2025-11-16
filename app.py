import streamlit as st
import pandas as pd
from main import (
    build_pipeline,
    display_output,
    MSI_CATEGORIES,
    build_pca_plot
)

st.set_page_config(page_title="College Match & ROI Tool", layout="wide")

# ---------------- MAPPINGS ---------------- #

STATE_LIST = sorted([
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS",
    "KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY",
    "NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV",
    "WI","WY"
])

RES_MAPPING = {
    "In-State Tuition Only": "in_state",
    "Out-of-State Tuition Only": "oos",
    "No Preference": "any"
}

MSI_LABELS = {
    "None": None,
    "Historically Black College/University (HBCU)": "hbcu",
    "Asian American & Native American Pacific Islander Serving Institution (AANAPISI)": "aanapii",
    "Native American Non-Tribal Institution (NANTI)": "nanti",
    "Hispanic Serving Institution (HSI)": "hsi",
    "Tribal College/University": "tribal",
    "Predominantly Black Institution (PBI)": "pbi",
    "Alaska Native / Native Hawaiian Serving Institution (ANNHI)": "annhi"
}

# ---------------- UI ---------------- #

st.title("College Match & ROI Explorer")

st.write(
    "Answer the questions below to generate a customized list of colleges ranked by similarity to your preferences."
)

with st.form("user_inputs"):

    st.subheader("Basic Filters")

    state_pref = st.selectbox(
        "Select your home state",
        options=STATE_LIST,
        index=STATE_LIST.index("CA")
    )

    residency_display = st.selectbox(
        "Residency preference:",
        list(RES_MAPPING.keys())
    )
    residency_pref = RES_MAPPING[residency_display]

    family_earnings = st.number_input(
        "Estimated Family Income",
        min_value=0,
        max_value=500000,
        step=1000,
        value=60000
    )

    desired_degree = st.selectbox(
        "Minimum degree you want:",
        ["non-degree", "associate", "bachelor", "master", "doctoral"]
    )

    st.subheader("Soft Preferences (Similarity Matching)")

    sector = st.selectbox("Preference:", ["Public", "Private"])

    locality = st.selectbox("Preferred campus setting:", ["City", "Suburb", "Town", "Rural"])

    msi_display = st.selectbox(
        "Do you prefer a federally designated minority-serving institution?",
        list(MSI_LABELS.keys())
    )
    preferred_msi = MSI_LABELS[msi_display]

    st.markdown("#### Numeric Preferences (You choose the target value)")

    colA, colB, colC = st.columns(3)

    with colA:
        target_enrollment = st.slider(
            "Ideal enrollment size",
            min_value=500,
            max_value=100000,
            value=30000,
            step=500
        )

    with colB:
        target_acceptance = st.slider(
            "Ideal acceptance rate (%)",
            min_value=1,
            max_value=100,
            value=20,
            step=1
        ) / 100

    with colC:
        target_ratio = st.slider(
            "Ideal student–faculty ratio",
            min_value=3,
            max_value=60,
            value=8,
            step=1
        )

    st.write("---")

    st.markdown("#### Weight How Much These Preferences Matter (1–5)")

    colW1, colW2, colW3 = st.columns(3)
    with colW1:
        w_sector = st.slider("Institution Type Weight", 1, 5, 3)
        w_locality = st.slider("Campus Setting Weight", 1, 5, 4)
        w_msi = st.slider("Minority Serving Institution Weight", 1, 5, 3)

    with colW2:
        w_enrollment = st.slider("Enrollment Weight", 1, 5, 4)
        w_acceptance = st.slider("Acceptance Rate Weight", 1, 5, 4)
        w_ratio = st.slider("Student–Faculty Ratio Weight", 1, 5, 3)

    submitted = st.form_submit_button("Find My Colleges")

if submitted:

    with st.spinner("Generating personalized match list..."):
        user_prefs = {
            "sector": sector,
            "locality": locality,
            "preferred_msi": preferred_msi if preferred_msi != "none" else None,
            "total_enrollment": target_enrollment,
            "admit_rate": target_acceptance,
            "student_faculty_ratio": target_ratio
        }

        user_weights = {
            "sector": w_sector,
            "locality": w_locality,
            "msi": w_msi,
            "total_enrollment": w_enrollment,
            "admit_rate": w_acceptance,
            "student_faculty_ratio": w_ratio
        }

        ranked_df = build_pipeline(
            state_pref,
            residency_pref,
            family_earnings,
            desired_degree,
            user_prefs,
            user_weights
        )

        results = display_output(ranked_df)

    st.success("Done! Your personalized college match results are below.")

    st.subheader("Recommended Colleges")
    st.data_editor(
        results,
        use_container_width=True,
        hide_index=True,
        disabled=True
    )
    csv_data = results.to_csv(index=False)
    st.download_button(
        label="📁 Download Full Results (CSV)",
        data=csv_data,
        file_name="college_matches.csv",
        mime="text/csv"
    )

    st.subheader("Visualizing Your Fit Among Colleges")

    try:
        pca_fig = build_pca_plot(ranked_df, user_prefs)
        st.plotly_chart(pca_fig, use_container_width=True)
    except Exception:
        st.warning("Not enough data to generate PCA visualization for this result set.")


