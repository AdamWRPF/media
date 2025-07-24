import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

EXCEL_FILE = "Media.xlsx"
LOGO_FILE = "wrpf_logo.png"  # Make sure this file exists in the same directory

# --- PAGE CONFIG ---
st.set_page_config(page_title="WRPF Media Dashboard", layout="wide")
st.title("📸 WRPF UK Media Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_FILE)
    df["Event Date"] = pd.to_datetime(df["Event Date"], dayfirst=True)
    return df

df = load_data()

# --- TEAM MEMBERS ---
team_members = [
    "Alex Hulme",
    "Mike Melladay",
    "Labibur Rahman",
    "Sam Taylor",
    "Emma Wilding"
]

# --- SIDEBAR ---
st.sidebar.markdown("## 🎛️ Filters & Search")

selected_member = st.sidebar.selectbox("👤 Select Team Member", ["All"] + team_members)
search_query = st.sidebar.text_input("🔍 Search (venue, postcode, media type)")

st.sidebar.markdown("---")
st.sidebar.markdown("## 🗓️ Upcoming Events")

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

# --- FILTER DATA ---
filtered_df = df.copy()
if selected_member != "All":
    filtered_df = filtered_df[filtered_df["Cover"] == selected_member]

if search_query:
    mask = filtered_df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)
    filtered_df = filtered_df[mask]

# --- PASSWORD PROTECTION ---
with st.expander("🔒 Edit Mode (Password Required)", expanded=False):
    password = st.text_input("Enter password", type="password")
    edit_mode = password == st.secrets.get("media_dashboard_password", "")

# --- DISPLAY TABLE ---
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

# --- GENERATE PDF FUNCTION ---
def generate_pdf(dataframe):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)

    elements = []
    styles = getSampleStyleSheet()

    # Add WRPF logo
    try:
        logo = Image(LOGO_FILE, width=120, height=35)
        elements.append(logo)
        elements.append(Spacer(1, 12))
    except Exception:
        st.warning("⚠️ WRPF logo not found or failed to load.")

    # Title
    title = Paragraph("WRPF UK Media Event Schedule", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Format DataFrame
    display_df = dataframe.copy()
    display_df["Event Date"] = display_df["Event Date"].dt.strftime("%d/%m/%Y")
    table_data = [list(display_df.columns)] + display_df.astype(str).values.tolist()

    # Table Style
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D62828')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- EXPORT TO PDF ---
st.download_button(
    label="⬇️ Export to PDF",
    data=generate_pdf(filtered_df),
    file_name="WRPF_Media_Schedule.pdf",
    mime="application/pdf"
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

# --- SAVE CHANGES TO EXCEL ---
if edit_mode and st.button("💾 Save Changes to File"):
    if selected_member != "All":
        df.loc[df["Cover"] == selected_member] = edited_df
    else:
        df = edited_df

    df.to_excel(EXCEL_FILE, index=False)
    st.success("✅ Changes saved to file.")
