import streamlit as st
from google import genai
from fpdf import FPDF

# --- 1. Page Config ---
st.set_page_config(page_title="AI Study Buddy", page_icon="🧠")

# --- 2. CSS FIX: Remove "Press enter to apply" ---
st.markdown(
    """
    <style>
    [data-testid="InputInstructions"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. API Setup ---
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not API_KEY:
    st.info("Please add your Google API Key in the sidebar or Secrets to continue.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- 4. Helper Functions ---
def generate_pdf(text, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Study Guide: {topic}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI Layout ---
st.title("AI-Powered Study Buddy 🤓")
topic = st.text_input("What do you want to learn?", placeholder="e.g. Photosynthesis")

if "study_content" not in st.session_state:
    st.session_state.study_content = None

if st.button("Generate Lesson") and topic:
    with st.spinner(f"Creating your guide for {topic}..."):
        # UPDATED PROMPT: Explicitly asking for line-by-line MCQ alignment
        prompt = f"""
        Act as an expert teacher. Create a study guide for: {topic}.
        Include:
        1. A simple explanation with an analogy.
        2. 5 key study bullet points.
        3. 3 multiple-choice questions. 
        
        CRITICAL FORMATTING FOR MCQs: 
        Ensure each MCQ option (A, B, C, D) is on its own NEW LINE. 
        Example:
        A) Option one
        B) Option two
        C) Option three
        D) Option four
        
        At the very end of your response, write exactly 'ANSWERS_BELOW' and then provide the correct answers.
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            st.session_state.study_content = response.text
            
        except Exception as e:
            st.error(f"API Error: {e}")

# --- 6. Display Content ---
if st.session_state.study_content:
    full_text = st.session_state.study_content
    
    if "ANSWERS_BELOW" in full_text:
        lesson_material, answer_key = full_text.split("ANSWERS_BELOW")
    else:
        lesson_material, answer_key = full_text, "Answers not found in response."

    st.markdown("---")
    # Streamlit renders markdown, so the newlines from the prompt will show up correctly
    st.markdown(lesson_material)

    with st.expander("📝 Check Your Answers"):
        st.write(answer_key.strip())

    st.markdown("---")

    pdf_data = generate_pdf(full_text, topic)
    st.download_button(
        label="📥 Download Study Guide (PDF)",
        data=pdf_data,
        file_name=f"{topic}_Study_Guide.pdf",
        mime="application/pdf"
    )
else:
    st.info("Enter a topic above to begin!")
