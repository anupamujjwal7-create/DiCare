import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- INITIALIZE GOOGLE AUTH ---
if "authenticator" not in st.session_state:
    st.session_state.authenticator = Authenticate(
        secret_credentials_path='client_secret.json',
        cookie_name='diacare_auth_cookie',
        cookie_key='random_secret_key_123',
        redirect_uri='http://localhost:8502/'
    )

authenticator = st.session_state.authenticator

# Process URL auth token with error handling
try:
    authenticator.check_authentification()
except Exception:
    # Clear bad/expired URL tokens and reset query params
    st.query_params.clear()

# Block app until user logs in
if not st.session_state.get('connected', False):
    st.title("DiaCare - Diabetes Management")
    st.subheader("Please sign in to access your dashboard")
    authenticator.login()
    st.stop()

# --- LOGGED IN SIDEBAR HEADER ---
user_name = st.session_state.get('user_info', {}).get('name', 'User')
st.sidebar.write(f"Logged in as: **{user_name}**")

if st.sidebar.button("Logout"):
    authenticator.logout()

# --- LOGGED IN SIDEBAR HEADER ---
user_name = st.session_state.get('user_info', {}).get('name', 'User')
st.sidebar.write(f"Logged in as: **{user_name}**")

if st.sidebar.button("Logout"):
    authenticator.logout()

# --- YOUR MAIN APP CONTINUES BELOW ---

# --- YOUR MAIN APP CONTINUES BELOW ---
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DiaCare — Diabetes Management Platform", page_icon="🩸", layout="wide")

# Persistent Session State Initialization
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "diabetes_type": "Type 1",
        "treatment_type": "Insulin + Tablets",
        "icr": 10.0,  # 1 unit covers 10g carbs
        "isf": 40.0,  # 1 unit drops 40 mg/dL
        "target_glucose": 100.0,
        "basal_meds": "Lantus",
        "bolus_meds": "Humalog",
        "oral_meds": "Metformin",
    }

if "glucose_logs" not in st.session_state:
    import pandas as pd
    st.session_state.glucose_logs = pd.DataFrame(columns=["Timestamp", "Glucose_mgdL", "Context", "Symptoms"])

if "dose_logs" not in st.session_state:
    import pandas as pd
    st.session_state.dose_logs = pd.DataFrame(columns=["Timestamp", "Medication", "Dose_Units", "Site"])

if "meal_logs" not in st.session_state:
    import pandas as pd
    st.session_state.meal_logs = pd.DataFrame(columns=["Timestamp", "Meal_Name", "Carbs_g", "High_Fat"])

# App Banner
st.title("🩸 DiaCare Platform")
st.caption("Self-Management Support & Clinical Intelligence Portal")

# Mandatory Medical Safety Disclaimer
st.warning(
    "⚠️ **Medical Disclaimer:** This application is for logging and self-management educational support only. "
    "It does not replace professional medical judgment. Dose calculations are estimates based on your "
    "physician-provided parameters. Always verify dosing with your clinical care team."
)

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Welcome Back")
    st.write(f"**Current Profile:** {st.session_state.user_profile['diabetes_type']} | "
             f"**Treatment:** {st.session_state.user_profile['treatment_type']}")
    
    st.markdown("""
    Use the navigation sidebar on the left to access all modules:
    - **Profile & Onboarding:** Configure clinical baselines (ICR, ISF, medication types).
    - **Glucose Logging:** Record blood glucose with context tags and symptoms.
    - **Medication Logging:** Track insulin and oral therapy administration.
    - **Meal Logging:** Log carbohydrates and view high-fat split-bolus clinical guidance.
    - **Analytics:** View time-in-range, eA1c estimates, and downloadable reports.
    - **Dose Calculator:** Execute bolus and correction math using physician-provided ratios.
    """)

with col_right:
    st.subheader("Quick Metrics")
    logs = st.session_state.glucose_logs
    if not logs.empty:
        latest = logs.iloc[-1]
        st.metric("Latest Glucose", f"{latest['Glucose_mgdL']} mg/dL", delta=f"{latest['Context']}")
        avg_g = logs["Glucose_mgdL"].mean()
        st.metric("30-Day Avg Estimate", f"{avg_g:.1f} mg/dL")
    else:
        st.info("No glucose records logged yet. Go to 'Log Glucose' to begin.")
        st.title("DiaCare - Diabetes Management")

st.header("User Profile")

# Collapsible section to edit settings
with st.expander("⚙️ Edit Profile Settings"):
    with st.form("profile_edit_form"):
        curr = st.session_state.user_profile

        col_a, col_b = st.columns(2)
        with col_a:
            d_type = st.selectbox("Diabetes Type", ["Type 1", "Type 2", "Gestational", "Pre-diabetes"])
            t_type = st.text_input("Treatment Type", value=str(curr.get("treatment_type", "")))
            icr = st.number_input("ICR (1 unit covers Xg carbs)", value=float(curr.get("icr", 10.0)))
            isf = st.number_input("ISF (1 unit drops X mg/dL)", value=float(curr.get("isf", 40.0)))

        with col_b:
            target = st.number_input("Target Glucose (mg/dL)", value=float(curr.get("target_glucose", 100.0)))
            basal = st.text_input("Basal Meds", value=str(curr.get("basal_meds", "")))
            bolus = st.text_input("Bolus Meds", value=str(curr.get("bolus_meds", "")))
            oral = st.text_input("Oral Meds", value=str(curr.get("oral_meds", "")))

        save_button = st.form_submit_button("Save Profile")

        if save_button:
            st.session_state.user_profile = {
                "diabetes_type": d_type,
                "treatment_type": t_type,
                "icr": icr,
                "isf": isf,
                "target_glucose": target,
                "basal_meds": basal,
                "bolus_meds": bolus,
                "oral_meds": oral
            }
            st.success("Profile updated successfully!")
            st.rerun()

# Display current profile values
profile = st.session_state.user_profile
col1, col2 = st.columns(2)

with col1:
    st.write(f"**Diabetes Type:** {profile['diabetes_type']}")
    st.write(f"**Treatment Type:** {profile['treatment_type']}")
    st.write(f"**ICR:** {profile['icr']}")
    st.write(f"**ISF:** {profile['isf']}")

with col2:
    st.write(f"**Target Glucose:** {profile['target_glucose']} mg/dL")
    st.write(f"**Basal Meds:** {profile['basal_meds']}")
    st.write(f"**Bolus Meds:** {profile['bolus_meds']}")
    st.write(f"**Oral Meds:** {profile['oral_meds']}")
profile = st.session_state.user_profile
col1, col2 = st.columns(2)

with col1:
    st.write(f"**Diabetes Type:** {profile['diabetes_type']}")
    st.write(f"**Treatment Type:** {profile['treatment_type']}")
    st.write(f"**ICR:** {profile['icr']}")
    st.write(f"**ISF:** {profile['isf']}")

with col2:
    st.write(f"**Target Glucose:** {profile['target_glucose']} mg/dL")
    st.write(f"**Basal Meds:** {profile['basal_meds']}")
    st.write(f"**Bolus Meds:** {profile['bolus_meds']}")
    st.write(f"**Oral Meds:** {profile['oral_meds']}")

st.header("Glucose Logs")
from datetime import datetime

st.subheader("Add New Reading")

# Create input form
with st.form("add_glucose_form"):
    glucose = st.number_input("Glucose Level (mg/dL)", min_value=20, max_value=500, value=100)
    context = st.selectbox("Context", ["Fasting", "Before Meal", "After Meal", "Bedtime"])
    symptoms = st.text_input("Symptoms", value="None")
    
    submit_button = st.form_submit_button("Add Reading")
    
    if submit_button:
        # Create a new entry row
        new_data = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Glucose_mgdL": glucose,
            "Context": context,
            "Symptoms": symptoms
        }])
        
        # Append new entry to the existing table
        st.session_state.glucose_logs = pd.concat([st.session_state.glucose_logs, new_data], ignore_index=True)
        st.success("Reading logged!")
        st.rerun()
st.dataframe(st.session_state.glucose_logs)
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