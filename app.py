import streamlit as st
import openai
import os

# Set page configuration
st.set_page_config(page_title="The Holland Bridge", layout="centered")

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
    "idea": "", "numeric": ""
}
for k, v in default_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Title
st.title("\U0001F4DA The Holland Bridge")
st.subheader("A self-discovery tool inspired by Suzy Welch's Becoming You methodology")

# Step navigation
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    if st.button("⬅️ Back", disabled=st.session_state.step == 1):
        st.session_state.step -= 1
with col3:
    if st.button("Next ➡️", disabled=st.session_state.step == 5):
        st.session_state.step += 1

st.markdown("---")

# Step 1 – Holland Codes
if st.session_state.step == 1:
    st.header("Step 1: Select Your Holland Codes")
    st.multiselect(
        "Pick up to 3 codes that best reflect you:",
        ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"],
        max_selections=3,
        key="holland"
    )

# Step 2 – Core Values (Values Bridge)
elif st.session_state.step == 2:
    st.header("Step 2: Choose Your Top 5 Values")
    st.markdown("Choose from the official Values Bridge options:")
    values_options = [
        "Cosmos", "Scope", "Luminance", "Workcentrism", "Radius",
        "Non Sibi", "Agency", "Achievement", "Voice", "Beholderism",
        "Belonging", "Familycentrism", "Place", "Eudemonia", "Affluence"
    ]
    st.multiselect(
        "Select up to 5 values:",
        values_options,
        max_selections=5,
        key="values"
    )

# Step 3 – Admired Lives
elif st.session_state.step == 3:
    st.header("Step 3: Admired Lives")
    st.markdown("Provide 4 people whose lives you admire and why:")
    for i in range(1, 5):
        with st.expander(f"Person {i}"):
            st.text_input(f"Name of Person {i}", key=f"name_{i}")
            st.text_area(f"What you admire about them", key=f"admire_{i}")
            st.text_area(f"What you *don’t* want from their life", key=f"reject_{i}")

# Step 4 – YouScience Traits
elif st.session_state.step == 4:
    st.header("Step 4: Select Your YouScience Results")
    def radio_group(label, options, key):
        return st.radio(label, options, horizontal=True, key=key)

    st.subheader("Interpersonal Style")
    radio_group("Select one:", ["Introvert", "Blended Energizer", "Extrovert"], "interpersonal")

    st.subheader("Time Frame Orientation")
    radio_group("Select one:", ["Future Focuser", "Balanced Focuser", "Present Focuser"], "timeframe")

    st.subheader("Work Approach")
    radio_group("Select one:", ["Generalist", "Liaison", "Specialist"], "workstyle")

    st.subheader("Inductive Reasoning")
    radio_group("Select one:", ["Diagnostic Problem Solver", "Investigator", "Fact Checker"], "inductive")

    st.subheader("Sequential Reasoning")
    radio_group("Select one:", ["Sequential Thinker", "Collaborative Planner", "Process Supporter"], "sequential")

    st.subheader("Spatial Visualization")
    radio_group("Select one:", ["3D Visualizer", "Space Planner", "Abstract Thinker"], "spatial")

    st.subheader("Idea Generation")
    radio_group("Select one:", ["Brainstormer", "Idea Contributor", "Concentrated Focuser"], "idea")

    st.subheader("Numerical Reasoning")
    radio_group("Select one:", ["Numerical Detective", "Numerical Predictor", "Numerical Checker"], "numeric")

# Step 5 – Contact Info and Submit
elif st.session_state.step == 5:
    st.header("Step 5: Contact Info & Submit")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    industry_avoid = st.text_area("Industries you want to avoid")

    if st.button("Submit Form ✅"):
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or st.secrets["openai"]["api_key"])

        admired_lives = [
            {
                "name": st.session_state.get(f"name_{i}", ""),
                "admire": st.session_state.get(f"admire_{i}", ""),
                "reject": st.session_state.get(f"reject_{i}", "")
            } for i in range(1, 5)
        ]

        prompt = f"""
You are an AI career strategist. Based on the following user data, generate an HTML output strictly in this format:

<h1> The Holland Bridge – Aligned Megatrends and Industries </h1>
<br> This is a beta version of the Holland Bridge, an instrument we are developing as part of the Becoming You Method. Its intention is to help individuals better identify roles aligned with their areas of interest. Your feedback is invaluable to us as we continue refining and improving this tool, thank you!

<h2>
1. First Name: {name}<br>
2. Email: {email}
</h2>

Then give at least six megatrends. Each should be formatted like this:

<b> [Megatrend Name] </b>
<ul>
<li><strong>Why it fits:</strong> {{description}}</li>
<li><strong>Examples:</strong> {{description of trends and industries}}</li>
<li><strong>Industries:</strong> {{list of industries}}</li>
</ul>

Only use this exact format in your response.

Use the following data to guide your response:

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
{industry_avoid}
"""

        with st.spinner("Generating AI insights..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            html_output = response.choices[0].message.content

        st.markdown("### ✨ Your Personalized Career Insights")
        st.components.v1.html(html_output, height=900, scrolling=True)

