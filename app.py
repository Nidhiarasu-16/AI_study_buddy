import streamlit as st
from google import genai
from google.genai import types
from fpdf import FPDF
import io
from PIL import Image

# --- 1. Page Config ---
st.set_page_config(page_title="AI Study Buddy", page_icon="🧠")

# --- 2. API Setup ---
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not API_KEY:
    st.info("Please add your Google API Key in the sidebar or Secrets to continue.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- 3. Helper Functions ---
def generate_pdf(text, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Study Guide: {topic}", ln=True, align='C')
    pdf.ln(10)
    # Multi_cell handles word wrapping for long AI responses
    pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 4. UI Layout ---
st.title("AI-Powered Study Buddy 🤓")
topic = st.text_input("What do you want to learn?", placeholder="e.g. Quantum Entanglement")

# Use Session State to keep data across button clicks (like showing answers)
if "study_content" not in st.session_state:
    st.session_state.study_content = None
if "study_image" not in st.session_state:
    st.session_state.study_image = None

if st.button("Generate Lesson") and topic:
    with st.spinner(f"Brainstorming and illustrating {topic}..."):
        # A. Generate Text
        text_prompt = f"""
        Act as an expert teacher. Create a study guide for: {topic}.
        Include:
        1. A simple explanation with an analogy.
        2. 5 key study bullet points.
        3. 3 multiple-choice questions (DO NOT include the answers yet).
        4. At the very end, add a section starting with 'ANSWERS_START' followed by the keys.
        """
        
        try:
            # Text Generation
            text_res = client.models.generate_content(model="gemini-2.0-flash", contents=text_prompt)
            st.session_state.study_content = text_res.text
            
            # B. Image Generation (Nano Banana)
            img_prompt = f"A professional, educational diagram or artistic representation of {topic}, high resolution, white background."
            img_res = client.models.generate_image(
                model="imagen-3.0-generate-001", # Model ID for Nano Banana / Imagen 3
                prompt=img_prompt
            )
            st.session_state.study_image = img_res.generated_images[0].image
            
        except Exception as e:
            st.error(f"Error: {e}")

# --- 5. Display Content ---
if st.session_state.study_content:
    # Show Image
    if st.session_state.study_image:
        st.image(st.session_state.study_image, caption=f"Visualizing {topic}")

    # Split content to hide answers
    full_text = st.session_state.study_content
    if "ANSWERS_START" in full_text:
        lesson_part, answer_part = full_text.split("ANSWERS_START")
    else:
        lesson_part, answer_part = full_text, "Answers not found."

    st.markdown(lesson_part)

    # Quiz Mode: Show Answers Button
    with st.expander("📝 Quiz Mode: Show Answers"):
        st.write(answer_part.strip())

    st.markdown("---")

    # Save as PDF
    pdf_bytes = generate_pdf(full_text, topic)
    st.download_button(
        label="📥 Save as PDF",
        data=pdf_bytes,
        file_name=f"{topic}_study_guide.pdf",
        mime="application/pdf"
    )

else:
    st.info("Enter a topic and click 'Generate Lesson' to get started.")
