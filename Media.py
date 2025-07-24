import streamlit as st
import pandas as pd
from datetime import datetime

EXCEL_FILE = "Media.xlsx"

# --- PASSWORD PROTECTION ---
st.set_page_config(page_title="Media Team Dashboard", layout="wide")
st.title("🎥 Media Team Dashboard")

password = st.text_input("Enter password", type="password")
if password != st.secrets.get("media_dashboard_password", ""):
    st.warning("Incorrect password.")
    st.stop()

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE)

df = load_data()

# --- TEAM FILTER ---
team_members = [
    "Alex Hulme",
    "Mike Melladay",
    "Labibur Rahman",
    "Sam Taylor",
    "Emma Wilding"
]

st.sidebar.header("📌 Filters")
selected_member = st.sidebar.selectbox("Filter by Team Member", ["All"] + team_members)

if selected_member != "All":
    filtered_df = df[df["Cover"] == selected_member]
else:
    filtered_df = df

# --- DISPLAY TABLE ---
st.subheader("📋 Scheduled Events")
edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)

# --- ADD NEW ENTRY ---
st.subheader("➕ Add New Event")
with st.form("add_event_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_date = st.date_input("Event Date", value=datetime.today())
        new_time = st.text_input("Start Time", value="10AM")
        new_venue = st.text_input("Venue")
        new_postcode = st.text_input("Post Code")
    with col2:
        new_cover = st.selectbox("Cover", team_members)
        new_type = st.selectbox("Media Type", ["Photography", "Video", "Other"])
        new_link = st.text_input("Website", value="https://")

    submitted = st.form_submit_button("Add Event")

    if submitted:
        new_row = {
            "Event Date": new_date,
            "Start Time": new_time,
            "Venue": new_venue,
            "Post code": new_postcode,
            "Cover": new_cover,
            "Media Type": new_type,
            "Website": new_link
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        st.success("✅ New event added. Please refresh to view in the main table.")

# --- SAVE EDITED DATA ---
if st.button("💾 Save Changes to File"):
    # Update original DataFrame only if filtered
    if selected_member != "All":
        df.loc[df["Cover"] == selected_member] = edited_df
    else:
        df = edited_df

    df.to_excel(EXCEL_FILE, index=False)
    st.success("✅ Data saved successfully.")
