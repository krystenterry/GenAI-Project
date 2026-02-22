import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to create PDF
def create_pdf(text, topic):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    
    title = Paragraph(f"<b>AI Study Guide: {topic}</b>", styles["Title"])
    body = Paragraph(text.replace("\n", "<br/>"), styles["BodyText"])

    content.append(title)
    content.append(body)
    doc.build(content)

    buffer.seek(0)
    return buffer

# Page config
st.set_page_config(page_title="AI Certification Study Buddy", page_icon="🎯")

# UI
st.title("🎯 AI Certification Study Buddy")
st.subheader("Generate Complete Exam Concepts for Open-Book Certifications")

# Inputs
topic = st.text_input(
    "Enter Certification or Topic (Example: Scrum Master, AWS Cloud Practitioner, PMP):"
)

exam_type = st.text_input(
    "Optional: Specific Exam Name (Example: PSM I, CSM, AWS CCP):"
)

mode = st.radio(
    "Select Study Mode:",
    ["Exam Prep (All Concepts)", "Learn Mode (Simple Explanation)"]
)

# Store result in session state
if "study_guide" not in st.session_state:
    st.session_state.study_guide = None

if st.button("Generate Study Guide"):
    if topic:
        with st.spinner("Generating your comprehensive study guide..."):

            if mode == "Exam Prep (All Concepts)":
                prompt = f"""
                You are an expert certification exam coach.

                Create a comprehensive open-book exam study guide for:
                Topic: {topic}
                Exam: {exam_type if exam_type else "General Certification"}

                Your response MUST include ALL major exam concepts and domains.

                Structure the output with clear sections:

                1. Core Exam Domains (with explanations)
                2. ALL Key Concepts Likely Covered on the Exam
                3. Important Definitions to Know
                4. High-Yield Topics (most frequently tested)
                5. Common Exam Scenarios & Situational Questions
                6. Common Tricky Areas Students Get Wrong
                7. 5 Certification-Style Practice Questions

                Be detailed, structured, and educational.
                Do NOT provide real exam answers or leaked content.
                """

            else:
                prompt = f"""
                Explain the topic '{topic}' in a simple and structured way for studying.

                Include:
                - Simple explanation
                - Real-world analogy
                - Key concepts
                - Summary
                """

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a professional certification study coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )

            result = response.choices[0].message.content
            st.session_state.study_guide = result

    else:
        st.warning("Please enter a certification topic first.")

# Display Study Guide
if st.session_state.study_guide:
    st.markdown("## 📚 Your AI-Generated Study Guide")
    st.write(st.session_state.study_guide)

    # Create PDF
    pdf_file = create_pdf(st.session_state.study_guide, topic)

    # Download button
    st.download_button(
        label="📥 Download as PDF Study Guide",
        data=pdf_file,
        file_name=f"{topic.replace(' ', '_')}_study_guide.pdf",
        mime="application/pdf"
    )