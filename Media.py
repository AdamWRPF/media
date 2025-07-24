import streamlit as st
import pandas as pd
from datetime import datetime

EXCEL_FILE = "Media.xlsx"

st.set_page_config(page_title="Media Team Dashboard", layout="wide")
st.title("🎥 Media Team Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_FILE)
    df["Event Date"] = pd.to_datetime(df["Event Date"], dayfirst=True).dt.strftime("%d/%m/%Y")
    return df

df = load_data()

# --- PASSWORD FOR EDITING ---
with st.expander("🔒 Edit Mode (Password Required)", expanded=False):
    password = st.text_input("Enter password", type="password")
    edit_mode = password == st.secrets.get("media_dashboard_password", "")

# --- COVER FILTER ---
team_members = df["Cover"].dropna().unique().tolist()
cover_filter = st.selectbox("🎯 Filter by Cover (Team Member)", ["All"] + sorted(team_members))

if cover_filter != "All":
    filtered_df = df[df["Cover"] == cover_filter]
else:
    filtered_df = df

# --- DISPLAY EVENTS ---
st.subheader("📋 Scheduled Events")

if edit_mode:
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )
else:
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

# --- ADD NEW ENTRY FORM ---
if edit_mode:
    st.subheader("➕ Add New Event")
    with st.form("add_event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Event Date", value=datetime.today())
            new_time = st.text_input("Start Time", value="10AM")
            new_venue = st.text_input("Venue")
            new_postcode = st.text_input("Post Code")
        with col2:
            new_cover = st.selectbox("Cover", [
                "Alex Hulme", "Mike Melladay", "Labibur Rahman", "Sam Taylor", "Emma Wilding"
            ])
            new_type = st.selectbox("Media Type", ["Photography", "Video", "Other"])
            new_link = st.text_input("Website", value="https://")

        submitted = st.form_submit_button("Add Event")

        if submitted:
            new_row = {
                "Event Date": new_date.strftime("%d/%m/%Y"),
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

# --- SAVE CHANGES ---
if edit_mode and st.button("💾 Save Changes to File"):
    if cover_filter != "All":
        df.loc[df["Cover"] == cover_filter] = edited_df
    else:
        df = edited_df

    df.to_excel(EXCEL_FILE, index=False)
    st.success("✅ Data saved successfully.")
