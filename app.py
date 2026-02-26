import streamlit as st
from google import genai
from fpdf import FPDF

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

# Initialize the client (Pick up API key from variable)
client = genai.Client(api_key=API_KEY)

# --- 3. Helper Functions ---
def generate_pdf(text, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Study Guide: {topic}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    # PDF libraries often fail on emojis or complex unicode
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. UI Layout ---
st.title("AI-Powered Study Buddy 🤓")
topic = st.text_input("What do you want to learn?", placeholder="e.g. Plate Tectonics")

# Use Session State so the lesson stays visible when you click PDF/Quiz buttons
if "study_content" not in st.session_state:
    st.session_state.study_content = None

if st.button("Generate Lesson") and topic:
    with st.spinner(f"Consulting the 2026 knowledge base for {topic}..."):
        prompt = f"""
        Act as an expert teacher. Create a study guide for: {topic}.
        Include:
        1. A simple explanation with an analogy.
        2. 5 key study bullet points.
        3. 3 multiple-choice questions.
        
        Important: End the response with 'ANSWERS_SECTION' then the keys.
        """
        
        try:
            # UPDATED: Using the 2026 standard model gemini-2.5-flash
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            st.session_state.study_content = response.text
            
        except Exception as e:
            st.error(f"Error: {e}")
            if "404" in str(e):
                st.warning("Tip: Use 'gemini-2.5-flash' or 'gemini-3-flash-preview'.")

# --- 5. Display Content ---
if st.session_state.study_content:
    full_text = st.session_state.study_content
    
    if "ANSWERS_SECTION" in full_text:
        lesson, answers = full_text.split("ANSWERS_SECTION")
    else:
        lesson, answers = full_text, "Answers unavailable."

    st.markdown("---")
    st.markdown(lesson)

    # Feature 1: Quiz Mode
    with st.expander("📝 Quiz Mode: Show Answers"):
        st.write(answers.strip())

    st.markdown("---")

    # Feature 2: Save as PDF
    pdf_bytes = generate_pdf(full_text, topic)
    st.download_button(
        label="📥 Save Study Guide as PDF",
        data=pdf_bytes,
        file_name=f"{topic}_StudyGuide.pdf",
        mime="application/pdf"
    )
