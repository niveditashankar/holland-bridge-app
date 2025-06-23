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

# === Step State Tracking ===
if 'step' not in st.session_state:
    st.session_state.step = 1

# === Session Initialization ===
default_keys = {
    "holland1": "", "holland2": "", "holland3": "",
    "values_1": "", "values_2": "", "values_3": "", "values_4": "", "values_5": "",
    "name_1": "", "admire_1": "", "reject_1": "",
    "name_2": "", "admire_2": "", "reject_2": "",
    "name_3": "", "admire_3": "", "reject_3": "",
    "interpersonal": "", "timeframe": "", "workstyle": "", "vocab": "",
    "visual": "", "inductive": "", "sequential": "", "spatial": "",
    "idea": "", "numeric": "", "industry_avoid": "",
    "first_name": "", "last_name": "", "email": ""
}
for k, v in default_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === Navigation Buttons ===
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if st.button("⬅️ Back", disabled=st.session_state.step == 1):
        st.session_state.step -= 1
with col3:
    if st.button("Next ➡️", disabled=st.session_state.step == 6):
        st.session_state.step += 1

st.markdown("---")

# === Stepper UI ===
if st.session_state.step == 1:
    st.header("Please select your first interest from the Holland Codes")
    st.selectbox("Please select your first interest from the Holland Codes", ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"], key="holland1")
    st.selectbox("Please select your second interest from the Holland Codes", ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"], key="holland2")
    st.selectbox("Please select your third interest from the Holland Codes", ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"], key="holland3")

elif st.session_state.step == 2:
    st.header("Your Top 5 Core Values – The Values Bridge Results")
    for i in range(1, 6):
        st.text_input(f"Core Value #{i}", key=f"values_{i}")

elif st.session_state.step == 3:
    st.header("Whose Life Do You Want Anyway?")
    for i in range(1, 4):
        st.text_input(f"Person {i} - Name of the person", key=f"name_{i}")
        st.text_area(f"Person {i} - Here are the main reasons I love, desire, or otherwise covet the life this person leads. What about this person's life appeals to you? Consider their career, relationships, lifestyle, values, or achievements.", key=f"admire_{i}")
        st.text_area(f"Person {i} - Um, no thank you. What aspects of this person's life do you not want for yourself?", key=f"reject_{i}")

elif st.session_state.step == 4:
    st.header("You Science Results")
    def radio_group(label, options, key):
        return st.radio(label, options, horizontal=True, key=key)
    radio_group("Interpersonal Style", ["Introvert", "Blended Energizer", "Extrovert"], "interpersonal")
    radio_group("Timeframe Orientation", ["Future Focuser", "Balanced Focuser", "Present Focuser"], "timeframe")
    radio_group("Work Approach", ["Generalist", "Liaison", "Specialist"], "workstyle")
    radio_group("Vocabulary", ["Limited", "Competent", "Masterful"], "vocab")
    radio_group("Visual Comparison Speed", ["Single Checker", "Double Checker", "Triple Checker"], "visual")
    radio_group("Inductive Reasoning", ["Diagnostic Problem Solver", "Investigator", "Fact Checker"], "inductive")
    radio_group("Sequential Reasoning", ["Sequential Thinker", "Collaborative Planner", "Process Supporter"], "sequential")
    radio_group("Spatial Visualization", ["3D Visualizer", "Space Planner", "Abstract Thinker"], "spatial")
    radio_group("Idea Generation", ["Brainstormer", "Idea Contributor", "Concentrated Focuser"], "idea")
    radio_group("Numerical Reasoning", ["Numerical Detective", "Numerical Predictor", "Numerical Checker"], "numeric")

elif st.session_state.step == 5:
    st.header("Industries and Roles to Avoid: Defining Your No-Go Zones")
    st.text_area("Are there any industries and roles you are certain you do NOT want to work in?\nFor example: Healthcare, Mining and HR", key="industry_avoid")

elif st.session_state.step == 6:
    st.header("Contact Information")
    st.text_input("First Name", key="first_name")
    st.text_input("Last Name", key="last_name")
    st.text_input("Email", key="email")

    if st.button("📩 Submit"):
        full_name = f"{st.session_state.first_name} {st.session_state.last_name}"

        def create_pdf(content: str, filename: str) -> BytesIO:
            buffer = BytesIO()
            pisa.CreatePDF(content, dest=buffer)
            buffer.seek(0)
            return buffer

        def send_email(to_email: str, pdf_buffers: dict):
            msg = EmailMessage()
            msg["Subject"] = "Your Holland Bridge Results"
            msg["From"] = st.secrets["email"]
            msg["To"] = to_email
            msg.set_content("Please find attached your personalized Holland Bridge reports.")
            for fname, buf in pdf_buffers.items():
                msg.add_attachment(buf.read(), maintype='application', subtype='pdf', filename=fname)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(st.secrets["email"], st.secrets["password"])
                smtp.send_message(msg)

        template = Template("""
        <h2>{{ title }}</h2>
        <p><strong>Name:</strong> {{ name }}</p>
        <p><strong>Content:</strong></p>
        <ul>{% for item in content %}<li>{{ item }}</li>{% endfor %}</ul>
        """)

        roles_content = template.render(
            title="Aligned Roles",
            name=full_name,
            content=[f"Holland Codes: {st.session_state.holland1}, {st.session_state.holland2}, {st.session_state.holland3}",
                     f"Values: {', '.join([st.session_state[f'values_{i}'] for i in range(1,6)])}"])

        trends_content = template.render(
            title="Aligned Megatrends and Industries",
            name=full_name,
            content=[f"Avoided Industries: {st.session_state.industry_avoid}"])

        pdfs = {
            f"{full_name} – Holland Bridge – Aligned Roles.pdf": create_pdf(roles_content, "roles.pdf"),
            f"{full_name} – Holland Bridge – Megatrends.pdf": create_pdf(trends_content, "trends.pdf")
        }

        send_email(st.session_state.email, pdfs)
        st.success("Success! Your results have been emailed to you.")
