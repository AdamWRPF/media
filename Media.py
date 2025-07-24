import streamlit as st
import pandas as pd
from datetime import datetime

EXCEL_FILE = "Media.xlsx"

# --- CONFIGURE PAGE ---
st.set_page_config(page_title="🎥 Media Team Dashboard", layout="wide")

# Dark theme enforcement and styling
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
            color: #fafafa;
        }
        [data-testid="stSidebar"] {
            background-color: #161b22;
        }
        .stButton>button {
            background-color: #238636;
            color: white;
        }
        .stTextInput>div>input, .stSelectbox>div>div {
            background-color: #21262d;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Media Team Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_FILE)
    df["Event Date"] = pd.to_datetime(df["Event Date"], dayfirst=True)
    return df

df = load_data()

# --- TEAM MEMBERS LIST ---
team_members = [
    "Alex Hulme",
    "Mike Melladay",
    "Labibur Rahman",
    "Sam Taylor",
    "Emma Wilding"
]

# --- SIDEBAR MENU ---
st.sidebar.markdown("## 🎛️ Dashboard Controls")
st.sidebar.markdown("Filter and search scheduled events.")

# Filter by team member
selected_member = st.sidebar.selectbox("👤 Select Team Member", ["All"] + team_members)

# Search bar
search_query = st.sidebar.text_input("🔍 Search (venue, postcode, type...)")

st.sidebar.markdown("---")
st.sidebar.markdown("## 🗓️ Upcoming Events")

# Calendar preview (next 5)
upcoming = df[df["Event Date"] >= pd.Timestamp.today()].sort_values("Event Date").head(5)
if upcoming.empty:
    st.sidebar.markdown("_No upcoming events._")
else:
    for _, row in upcoming.iterrows():
        st.sidebar.markdown(
            f"**{row['Event Date'].strftime('%d %b')}**  \n"
            f"📍 {row['Venue']}  \n"
            f"🎥 {row['Media Type']} – {row['Cover']}"
        )

# --- APPLY FILTERS ---
filtered_df = df.copy()

if selected_member != "All":
    filtered_df = filtered_df[filtered_df["Cover"] == selected_member]

if search_query:
    mask = filtered_df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)
    filtered_df = filtered_df[mask]

# --- PASSWORD FOR EDITING ---
with st.expander("🔒 Edit Mode (Password Required)", expanded=False):
    password = st.text_input("Enter password", type="password")
    edit_mode = password == st.secrets.get("media_dashboard_password", "")

# --- DISPLAY EVENTS TABLE ---
st.subheader("📋 Scheduled Events")

if edit_mode:
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )
else:
    st.dataframe(filtered_df, use_container_width=True)

# --- EXPORT CSV ---
st.download_button(
    label="⬇️ Download CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="media_schedule.csv",
    mime="text/csv"
)

# --- ADD NEW EVENT FORM ---
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
            st.success("✅ New event added. Please refresh to see it in the table.")

# --- SAVE CHANGES BUTTON ---
if edit_mode and st.button("💾 Save Changes to File"):
    if selected_member != "All":
        df.loc[df["Cover"] == selected_member] = edited_df
    else:
        df = edited_df

    df.to_excel(EXCEL_FILE, index=False)
    st.success("✅ Changes saved to file.")
