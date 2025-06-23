# === FILE: app.py ===
import streamlit as st
import os
from openai import OpenAI
from xhtml2pdf import pisa
import smtplib
from email.message import EmailMessage
from io import BytesIO
from jinja2 import Template

# === Streamlit Configuration ===
st.set_page_config(page_title="The Holland Bridge", layout="centered")

# === Custom CSS Styling ===
st.markdown("""
<style>
    .main {
        background-color: #F7EDE8;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #4B2E2B;
        font-family: Georgia, serif;
    }
    .stButton > button {
        background-color: #7B3F30;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 16px;
    }
    .stSelectbox, .stMultiselect, .stTextInput, .stTextArea, .stRadio > div {
        background-color: #FBEDE6 !important;
        border: 1px solid #7B3F30 !important;
        border-radius: 6px !important;
        color: #4B2E2B !important;
    }
    .stMarkdown, .stRadio label, .stTextInput label, .stTextArea label {
        font-family: Georgia, serif;
        color: #4B2E2B;
    }
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #7B3F30 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# === Display GIF Banner ===
display_gif = "assets/holland_bridge.gif"
if os.path.exists(display_gif):
    st.markdown("<h2 style='text-align: center;'>Welcome to The Holland Bridge</h2>", unsafe_allow_html=True)
    st.image(display_gif, use_container_width=True)

# === Core Values (Exact 15 from Suzy Welch) ===
core_values_options = [
    "Scope", "Radius", "Familycentrism", "Non Sibi", "Luminance",
    "Agency", "Workcentrism", "Eudemonia", "Achievement", "Affluence",
    "Voice", "Beholderism", "Belonging", "Place", "Cosmos"
]

# === Step Initialization ===
if "step" not in st.session_state:
    st.session_state.step = 1

# === Navigation Buttons ===
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if st.button("⬅️ Back", disabled=st.session_state.step == 1):
        st.session_state.step -= 1
with col3:
    if st.button("Next ➡️", disabled=st.session_state.step == 6):
        st.session_state.step += 1

st.markdown("---")

# === Step 1: Holland Codes ===
if st.session_state.step == 1:
    st.header("Which Holland Codes reflect you best?")
    st.multiselect("Select up to 3 Holland Codes:",
                  ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"],
                  max_selections=3, key="holland")

# === Step 2: Core Values ===
elif st.session_state.step == 2:
    st.header("What are your top 5 core values?")
    st.multiselect("Choose exactly 5 core values:",
                  core_values_options,
                  max_selections=5, key="values")

# === Step 3: Admired Lives ===
elif st.session_state.step == 3:
    st.header("Whose life do you admire or desire?")
    for i in range(1, 5):
        with st.expander(f"Person {i} - Tell us about them"):
            st.text_input("Name:", key=f"name_{i}")
            st.text_area("What about their life do you admire?", key=f"admire_{i}")
            st.text_area("What aspects do you *not* want from their life?", key=f"reject_{i}")

# === Step 4: YouScience ===
elif st.session_state.step == 4:
    def radio_group(label, options, key):
        return st.radio(label, options, horizontal=True, key=key)

    st.header("Select your YouScience Profile Results")
    radio_group("Interpersonal Style", ["Introvert", "Blended Energizer", "Extrovert"], "interpersonal")
    radio_group("Timeframe Orientation", ["Future Focuser", "Balanced Focuser", "Present Focuser"], "timeframe")
    radio_group("Work Approach", ["Generalist", "Liaison", "Specialist"], "workstyle")
    radio_group("Inductive Reasoning", ["Diagnostic Problem Solver", "Investigator", "Fact Checker"], "inductive")
    radio_group("Sequential Reasoning", ["Sequential Thinker", "Collaborative Planner", "Process Supporter"], "sequential")
    radio_group("Spatial Visualization", ["3D Visualizer", "Space Planner", "Abstract Thinker"], "spatial")
    radio_group("Idea Generation", ["Brainstormer", "Idea Contributor", "Concentrated Focuser"], "idea")
    radio_group("Numerical Reasoning", ["Numerical Detective", "Numerical Predictor", "Numerical Checker"], "numeric")

# === Step 5: Avoided Industries ===
elif st.session_state.step == 5:
    st.header("What industries do you want to avoid?")
    st.text_area("Enter industries you prefer to avoid:", key="industry_avoid")

# === Step 6: Contact Info and Submit ===
elif st.session_state.step == 6:
    st.header("Where can we send your personalized report?")
    st.text_input("First Name", key="first_name")
    st.text_input("Last Name", key="last_name")
    st.text_input("Email", key="email")

    if st.button("📩 Submit"):
        user_name = f"{st.session_state.first_name} {st.session_state.last_name}"
        user_data = dict(st.session_state)
        roles_pdf = render_pdf({"section": "Roles", **user_data})
        industries_pdf = render_pdf({"section": "Industries", **user_data})
        send_email(user_name, st.session_state.email, {
            "Holland Bridge - Aligned Roles": roles_pdf,
            "Holland Bridge - Aligned Industries and Megatrends": industries_pdf
        })
        st.success("✅ Your personalized reports have been sent to your email!")

# === PDF Render and Email Helpers ===
def render_pdf(user_data):
    template = Template(open("assets/report_template.html").read())
    html_content = template.render(user_data=user_data)
    pdf_buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode("utf-8")), dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def send_email(name, recipient, pdfs):
    msg = EmailMessage()
    msg["Subject"] = f"Your Holland Bridge Reports"
    msg["From"] = st.secrets["smtp"]["sender"]
    msg["To"] = recipient
    msg.set_content("Find attached your personalized Holland Bridge reports.")
    for title, pdf_bytes in pdfs.items():
        msg.add_attachment(pdf_bytes.read(), maintype="application", subtype="pdf", filename=f"{name} - {title}.pdf")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(st.secrets["smtp"]["sender"], st.secrets["smtp"]["password"])
    server.send_message(msg)
    server.quit()
