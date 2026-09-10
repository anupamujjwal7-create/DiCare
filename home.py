import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from streamlit_oauth import OAuth2Component

# -----------------------------
# 1. PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="DiaCare — Diabetes Management Platform",
    page_icon="🩸",
    layout="wide"
)

# -----------------------------
# 2. GOOGLE OAUTH SETUP
# -----------------------------
with open("client_secret.json", "r") as f:
    config = json.load(f)["web"]

CLIENT_ID = config["client_id"]
CLIENT_SECRET = config["client_secret"]
AUTHORIZE_URL = config["auth_uri"]
TOKEN_URL = config["token_uri"]
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"
REDIRECT_URI = "http://localhost:8502/"

oauth2 = OAuth2Component(
    CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REVOKE_TOKEN_URL, REDIRECT_URI
)

# Authentication check
if "token" not in st.session_state:
    st.title("DiaCare - Diabetes Management")
    st.subheader("Please sign in to access your dashboard")
    
    result = oauth2.authorize_button(
        name="Sign in with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google_auth",
    )
    
    if result and "token" in result:
        st.session_state["token"] = result["token"]
        st.rerun()
    st.stop()

# Logout button in sidebar
if st.sidebar.button("Logout"):
    del st.session_state["token"]
    st.rerun()

# -----------------------------
# 3. INITIALIZE SESSION STATE
# -----------------------------
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "diabetes_type": "Type 1",
        "treatment_type": "Insulin + Tablets",
        "icr": 10.0,
        "isf": 40.0,
        "target_glucose": 100.0,
        "basal_meds": "Lantus",
        "bolus_meds": "Humalog",
        "oral_meds": "Metformin",
    }

if "glucose_logs" not in st.session_state:
    st.session_state.glucose_logs = pd.DataFrame(columns=["Timestamp", "Glucose_mgdL", "Context", "Symptoms"])

# -----------------------------
# 4. SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("Navigation")
navigation_page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Main Dashboard",
        "🩺 Health History & Insights"
    ]
)

# -----------------------------
# 5. PAGE: MAIN DASHBOARD
# -----------------------------
if navigation_page == "🏠 Main Dashboard":

    st.title("🩸 DiaCare Platform")
    st.caption("Self-Management Support & Clinical Intelligence Portal")

    st.warning(
        "⚠️ **Medical Disclaimer:** This application is for logging and self-management educational support only. "
        "It does not replace professional medical judgment. Always verify dosing with your clinical care team."
    )

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Welcome Back")
        st.write(f"**Current Profile:** {st.session_state.user_profile['diabetes_type']} | "
                 f"**Treatment:** {st.session_state.user_profile['treatment_type']}")

    with col_right:
        st.subheader("Quick Metrics")
        logs = st.session_state.glucose_logs
        if not logs.empty:
            latest = logs.iloc[-1]
            st.metric("Latest Glucose", f"{latest['Glucose_mgdL']} mg/dL", delta=f"{latest['Context']}")
            avg_g = logs["Glucose_mgdL"].mean()
            st.metric("Avg Glucose Estimate", f"{avg_g:.1f} mg/dL")
        else:
            st.info("No glucose records logged yet.")

    st.divider()

    # USER PROFILE & EDITING
    st.header("👤 User Profile")

    with st.expander("⚙️ Edit Personal Details & Ratios"):
        with st.form("profile_edit_form"):
            curr = st.session_state.user_profile

            col_a, col_b = st.columns(2)
            with col_a:
                d_type = st.selectbox(
                    "Diabetes Type", 
                    ["Type 1", "Type 2", "Gestational", "Pre-diabetes"], 
                    index=["Type 1", "Type 2", "Gestational", "Pre-diabetes"].index(curr.get("diabetes_type", "Type 1"))
                )
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

    st.divider()

    # GLUCOSE LOGGING
    st.header("🩸 Glucose Logs")

    with st.form("add_glucose_form"):
        st.subheader("Add New Reading")
        glucose = st.number_input("Glucose Level (mg/dL)", min_value=20, max_value=500, value=100)
        context = st.selectbox("Context", ["Fasting", "Before Meal", "After Meal", "Bedtime"])
        symptoms = st.text_input("Symptoms", value="None")
        
        submit_button = st.form_submit_button("Add Reading")
        
        if submit_button:
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Glucose_mgdL": glucose,
                "Context": context,
                "Symptoms": symptoms
            }])
            st.session_state.glucose_logs = pd.concat([st.session_state.glucose_logs, new_data], ignore_index=True)
            st.success("Reading logged!")
            st.rerun()

    st.dataframe(st.session_state.glucose_logs, use_container_width=True)

    st.divider()

    # DOSE CALCULATOR
    st.header("💉 Bolus & Correction Dose Calculator")

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
            carb_dose = carbs / icr if icr > 0 else 0.0
            glucose_diff = current_glucose - target
            correction_dose = (glucose_diff / isf) if (glucose_diff > 0 and isf > 0) else 0.0
            total_dose = round(carb_dose + correction_dose, 1)
            
            st.success(f"### Total Recommended Dose: **{total_dose} Units**")
            st.write(f"* **Carb Coverage:** {round(carb_dose, 1)} Units")
            st.write(f"* **Correction Coverage:** {round(correction_dose, 1)} Units")

# -----------------------------
# 6. PAGE: HEALTH HISTORY & INSIGHTS
# -----------------------------
elif navigation_page == "🩺 Health History & Insights":

    st.title("🩺 Health History & Insights")
    st.write("Track your health information and see how different factors relate to glucose levels.")

    tracker_tab = st.radio(
        "Select Tracker Section:",
        ["📊 Dashboard Overview", "🧪 Lab Results", "⚖️ Weight & BP", "🧪 Ketone Log", "🏃 Activity Log"],
        horizontal=True
    )

    if tracker_tab == "📊 Dashboard Overview":
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Latest HbA1c", "6.8%")
        col2.metric("Weight", "68 kg")
        col3.metric("Blood Pressure", "120/80")
        col4.metric("Activity", "35 min")

        st.divider()
        st.subheader("📈 Glucose & Activity Trends")
        glucose_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Average Glucose": [125, 132, 118, 145, 128, 120, 135],
            "Exercise (min)": [20, 30, 45, 15, 40, 50, 25]
        })
        st.line_chart(glucose_data.set_index("Day")[["Average Glucose", "Exercise (min)"]])

    elif tracker_tab == "🧪 Lab Results":
        st.header("🧪 Lab Result History")
        with st.form("lab_form"):
            test_date = st.date_input("Test Date", date.today())
            test_type = st.selectbox("Test", ["HbA1c", "Fasting Blood Glucose", "Cholesterol", "Triglycerides", "Other"])
            value = st.number_input("Result", min_value=0.0, step=0.1)
            unit = st.text_input("Unit", placeholder="Example: % or mg/dL")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add Result"):
                st.success("Lab result added successfully!")

    elif tracker_tab == "⚖️ Weight & BP":
        st.header("⚖️ Weight & Blood Pressure")
        t1, t2 = st.tabs(["Weight", "Blood Pressure"])
        with t1:
            st.subheader("Add Weight")
            with st.form("w_form"):
                st.date_input("Date", date.today())
                st.number_input("Weight (kg)", min_value=0.0, step=0.1)
                if st.form_submit_button("Save Weight"):
                    st.success("Weight recorded!")
        with t2:
            st.subheader("Add Blood Pressure")
            with st.form("bp_form"):
                st.date_input("Date", date.today(), key="bp_date")
                st.number_input("Systolic", min_value=0)
                st.number_input("Diastolic", min_value=0)
                if st.form_submit_button("Save Blood Pressure"):
                    st.success("Blood pressure recorded!")

    elif tracker_tab == "🧪 Ketone Log":
        st.header("🧪 Ketone Log")
        with st.form("k_form"):
            st.date_input("Date", date.today())
            st.time_input("Time")
            st.number_input("Ketone Reading", min_value=0.0, step=0.1)
            st.selectbox("Testing Method", ["Blood", "Urine"])
            if st.form_submit_button("Save Reading"):
                st.success("Ketone reading recorded!")

    elif tracker_tab == "🏃 Activity Log":
        st.header("🏃 Exercise & Activity")
        with st.form("act_form"):
            st.date_input("Date", date.today())
            st.selectbox("Activity", ["Walking", "Running", "Cycling", "Swimming", "Gym", "Sports", "Other"])
            st.number_input("Duration (minutes)", min_value=0, step=5)
            if st.form_submit_button("Save Activity"):
                st.success("Activity recorded!")