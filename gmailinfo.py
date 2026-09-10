import streamlit as st
import pandas as pd

# Initialize user profile if it doesn't exist yet
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "diabetes_type": "Type 1",
        "treatment_type": "Insulin + Tablets",
        "icr": 10.0,
        "isf": 40.0,
        "target_glucose": 100.0,
        "basal_meds": "Lantus",
        "bolus_meds": "Humalog",
        "oral_meds": "Metformin"
    }

# Safe lookup for profile ratios
profile = st.session_state.user_profile
icr = float(profile.get("icr", 10.0))
isf = float(profile.get("isf", 40.0))
target = float(profile.get("target_glucose", 100.0))
st.header("Bolus & Correction Dose Calculator")

# Fetch baseline ratios from user_profile
icr = float(st.session_state.user_profile.get("icr", 10.0))
isf = float(st.session_state.user_profile.get("isf", 40.0))
target = float(st.session_state.user_profile.get("target_glucose", 100.0))

with st.form("dose_calc_form"):
    col1, col2 = st.columns(2)
    with col1:
        current_glucose = st.number_input("Current Blood Glucose (mg/dL)", value=150.0, min_value=20.0, max_value=500.0)
    with col2:
        carbs = st.number_input("Carbohydrates to Eat (g)", value=40.0, min_value=0.0, max_value=300.0)
    
    calc_button = st.form_submit_button("Calculate Insulin Dose")
    
    if calc_button:
        # Calculate dosage components
        carb_dose = carbs / icr if icr > 0 else 0.0
        
        glucose_diff = current_glucose - target
        correction_dose = (glucose_diff / isf) if (glucose_diff > 0 and isf > 0) else 0.0
        
        total_dose = round(carb_dose + correction_dose, 1)
        
        # Display results
        st.success(f"### Total Recommended Dose: **{total_dose} Units**")
        st.write(f"* **Carb Coverage:** {round(carb_dose, 1)} Units")
        st.write(f"* **Correction Coverage:** {round(correction_dose, 1)} Units")