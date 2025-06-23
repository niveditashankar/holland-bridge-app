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

# === Form Submission Logic ===
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

# === Handle Submit Action ===
if st.session_state.get("step") == 6 and st.button("📩 Submit"):
    user_name = f"{st.session_state.first_name} {st.session_state.last_name}"
    user_data = dict(st.session_state)
    roles_pdf = render_pdf({"section": "Roles", **user_data})
    industries_pdf = render_pdf({"section": "Industries", **user_data})
    send_email(user_name, st.session_state.email, {
        "Holland Bridge - Aligned Roles": roles_pdf,
        "Holland Bridge - Aligned Industries and Megatrends": industries_pdf
    })
    st.success("✅ Your personalized reports have been sent to your email!")
