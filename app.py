# === FILE: app.py ===
import streamlit as st
import openai
import os
from xhtml2pdf import pisa
import smtplib
from email.message import EmailMessage

# Set page configuration
st.set_page_config(page_title="The Holland Bridge", layout="centered")

# Inject Suzy Welch website-inspired styles
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

# Add animated banner
display_gif = "assets/holland_bridge.gif"
if os.path.exists(display_gif):
    st.markdown("<h2 style='text-align: center;'>Welcome to The Holland Bridge</h2>", unsafe_allow_html=True)
    st.image(display_gif, use_container_width=True)

# Stepper state in session
if 'step' not in st.session_state:
    st.session_state.step = 1

# Safe initialization of required session keys
default_keys = {
    "holland": [],
    "values": [],
    "name_1": "", "admire_1": "", "reject_1": "",
    "name_2": "", "admire_2": "", "reject_2": "",
    "name_3": "", "admire_3": "", "reject_3": "",
    "name_4": "", "admire_4": "", "reject_4": "",
    "interpersonal": "", "timeframe": "", "workstyle": "",
    "inductive": "", "sequential": "", "spatial": "",
    "idea": "", "numeric": "",
    "industry_avoid": ""
}
for k, v in default_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Step navigation
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if st.button("⬅️ Back", disabled=st.session_state.step == 1):
        st.session_state.step -= 1
with col3:
    if st.button("Next ➡️", disabled=st.session_state.step == 6):
        st.session_state.step += 1

st.markdown("---")

# Step 1 – Holland Codes
if st.session_state.step == 1:
    st.header("Please select your results from the Holland Codes")
    st.multiselect(
        "Pick up to 3 codes",
        ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"],
        max_selections=3,
        key="holland"
    )

# Step 2 – Core Values (Values Bridge)
elif st.session_state.step == 2:
    st.header("Your Top 5 Core Values – The Values Bridge Results")
    values_options = [
        "Cosmos", "Scope", "Luminance", "Workcentrism", "Radius",
        "Non Sibi", "Agency", "Achievement", "Voice", "Beholderism",
        "Belonging", "Familycentrism", "Place", "Eudemonia", "Affluence"
    ]
    st.multiselect("Please enter your Top 5 Core Values from your results of the values bridge below:", values_options, max_selections=5, key="values")

# Step 3 – Admired Lives
elif st.session_state.step == 3:
    st.header("Whose Life Do You Want Anyway?")
    for i in range(1, 5):
        with st.expander(f"Person {i} - Name of the person"):
            st.text_input("Who is the person whose life you admire or desire?", key=f"name_{i}")
            st.text_area("Here are the main reasons I love, desire, or otherwise covet the life this person leads. What about this person’s life appeals to you? Consider their career, relationships, lifestyle, values, or achievements.", key=f"admire_{i}")
            st.text_area("Um, no thank you. What aspects of this person’s life do you not want for yourself?", key=f"reject_{i}")

# Step 4 – YouScience Traits
elif st.session_state.step == 4:
    st.header("YouScience Results")
    def radio_group(label, options, key):
        return st.radio(label, options, horizontal=True, key=key)

    radio_group("Interpersonal Style", ["Introvert", "Blended Energizer", "Extrovert"], "interpersonal")
    radio_group("Timeframe Orientation", ["Future Focuser", "Balanced Focuser", "Present Focuser"], "timeframe")
    radio_group("Work Approach", ["Generalist", "Liaison", "Specialist"], "workstyle")
    radio_group("Inductive Reasoning", ["Diagnostic Problem Solver", "Investigator", "Fact Checker"], "inductive")
    radio_group("Sequential Reasoning", ["Sequential Thinker", "Collaborative Planner", "Process Supporter"], "sequential")
    radio_group("Spatial Visualization", ["3D Visualizer", "Space Planner", "Abstract Thinker"], "spatial")
    radio_group("Idea Generation", ["Brainstormer", "Idea Contributor", "Concentrated Focuser"], "idea")
    radio_group("Numerical Reasoning", ["Numerical Detective", "Numerical Predictor", "Numerical Checker"], "numeric")

# Step 5 – Industry Avoidance
elif st.session_state.step == 5:
    st.header("What Industries Do You Want to Avoid?")
    st.text_area("Please mention industries or sectors you know you would not want to work in:", key="industry_avoid")

# Step 6 – Contact Info and Submit
elif st.session_state.step == 6:
    st.header("Contact Information")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")

    if st.button("📩 Submit"):
        admired_lives = [
            {"name": st.session_state.get(f"name_{i}", ""),
             "admire": st.session_state.get(f"admire_{i}", ""),
             "reject": st.session_state.get(f"reject_{i}", "")}
            for i in range(1, 5)
        ]

        base_prompt = f"""
### HOLLAND CODES:
{', '.join(st.session_state.get("holland", []))}
### CORE VALUES:
{', '.join(st.session_state.get("values", []))}
### ADMIRED LIVES:
{admired_lives}
### YOUSCIENCE TRAITS:
- Interpersonal Style: {st.session_state['interpersonal']}
- Time Orientation: {st.session_state['timeframe']}
- Work Approach: {st.session_state['workstyle']}
- Inductive Reasoning: {st.session_state['inductive']}
- Sequential Reasoning: {st.session_state['sequential']}
- Spatial Visualization: {st.session_state['spatial']}
- Idea Generation: {st.session_state['idea']}
- Numerical Reasoning: {st.session_state['numeric']}
### INDUSTRIES TO AVOID:
{st.session_state['industry_avoid']}
"""

        roles_prompt = f"""
You are a career strategist. Generate a PDF-style HTML content titled:
<h1>{first_name} {last_name} – The Holland Bridge – Aligned Roles</h1>
Include 6 aligned job roles. For each:
<b>[Role Name]</b>
<ul><li><strong>Why it fits:</strong> {{reason}}</li>
<li><strong>What success looks like:</strong> {{description}}</li>
<li><strong>Potential job titles:</strong> {{titles}}</li>
</ul>
{base_prompt}
"""

        industries_prompt = f"""
You are a career strategist. Generate a PDF-style HTML content titled:
<h1>{first_name} {last_name} – The Holland Bridge – Aligned Megatrends and Industries</h1>
Include 6 megatrends. For each:
<b>[Megatrend Name]</b>
<ul>
<li><strong>Why it fits:</strong> {{reason}}</li>
<li><strong>Examples of trends and industries:</strong> {{examples}}</li>
<li><strong>Industries:</strong> {{industries}}</li>
</ul>
{base_prompt}
"""

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or st.secrets["openai"]["api_key"])

        with st.spinner("Generating AI insights..."):
            roles_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": roles_prompt}],
                temperature=0.7
            )
            roles_html = roles_response.choices[0].message.content

            industries_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": industries_prompt}],
                temperature=0.7
            )
            industries_html = industries_response.choices[0].message.content

        def html_to_pdf(source_html, output_filename):
            with open(output_filename, "wb") as f:
                pisa.CreatePDF(source_html, dest=f)

        roles_pdf_name = f"{first_name} {last_name} - Holland Bridge - Aligned Roles.pdf"
        industries_pdf_name = f"{first_name} {last_name} - Holland Bridge - Aligned Industries and Megatrends.pdf"

        html_to_pdf(roles_html, roles_pdf_name)
        html_to_pdf(industries_html, industries_pdf_name)

        msg = EmailMessage()
        msg['Subject'] = "Your Holland Bridge Reports"
        msg['From'] = st.secrets["smtp"]["sender"]
        msg['To'] = email
        msg.set_content("Attached are your personalized Holland Bridge reports.")

        for fname in [roles_pdf_name, industries_pdf_name]:
            with open(fname, "rb") as f:
                msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=fname)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["smtp"]["sender"], st.secrets["smtp"]["password"])
            smtp.send_message(msg)

        st.success("Success! Your results have been emailed to you!")
