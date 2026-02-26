import streamlit as st
from google import genai
from fpdf import FPDF

# --- 1. Page Config ---
st.set_page_config(page_title="AI Study Buddy", page_icon="🧠", layout="centered")

# --- 2. CSS Hacks ---
st.markdown(
    """
    <style>
    /* Hide 'Press enter to apply' instructions */
    [data-testid="InputInstructions"] {
        display: none;
    }
    
    /* Optional: Style the buttons to look more modern */
    .stButton>button {
        border-radius: 20px;
        width: 100%;
        border: 1px solid #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. Sidebar & API Setup ---
with st.sidebar:
    st.title("Settings ⚙️")
    st.info("Your AI Study Buddy uses the latest Gemini 2.5 Flash model.")
    
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        API_KEY = st.text_input("Enter Gemini API Key:", type="password")

if not API_KEY:
    st.warning("Please provide an API Key in the sidebar to begin.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- 4. PDF Helper ---
def generate_pdf(text, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Study Guide: {topic}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # Clean text for PDF (fpdf doesn't like some special characters)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. Main UI ---
st.title("AI-Powered Study Buddy 🤓")
topic = st.text_input("What are we learning today?", placeholder="e.g. Black Holes")

if "study_content" not in st.session_state:
    st.session_state.study_content = None

if st.button("Generate Lesson") and topic:
    with st.spinner(f"Creating a custom guide for {topic}..."):
        prompt = f"""
        Act as an expert teacher. Create a comprehensive study guide for: {topic}.
        1. Start with a clear explanation and a creative analogy.
        2. Provide 5 essential key points.
        3. Create 3 multiple-choice questions.
        4. End the response with the marker '---ANSWERS---' and then list the correct answers.
        """
        try:
            # Model updated to gemini-2.5-flash for 2026 stability
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            st.session_state.study_content = response.text
        except Exception as e:
            st.error(f"Error: {e}")

# --- 6. Displaying the Result with Tabs ---
if st.session_state.study_content:
    full_text = st.session_state.study_content
    
    # Split content for Quiz Mode
    if "---ANSWERS---" in full_text:
        lesson_part, answer_part = full_text.split("---ANSWERS---")
    else:
        lesson_part, answer_part = full_text, "Answers not found."

    # Use Tabs for a professional look
    tab1, tab2, tab3 = st.tabs(["📖 Lesson", "📝 Practice Quiz", "📥 Download"])

    with tab1:
        st.markdown(lesson_part)

    with tab2:
        # We only show the MCQs part here (often at the bottom of the lesson_part)
        st.info("Test your knowledge below!")
        st.markdown(lesson_part.split("3.")[-1] if "3." in lesson_part else "Check the lesson tab for questions.")
        with st.expander("Click to Reveal Answers"):
            st.success(answer_part.strip())

    with tab3:
        st.write("Take your study guide to go!")
        pdf_bytes = generate_pdf(full_text, topic)
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"{topic}_Guide.pdf",
            mime="application/pdf"
        )
else:
    st.write("No lesson generated yet. Enter a topic above to start!")
