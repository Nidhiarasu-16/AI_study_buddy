import streamlit as st
from google import genai

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

# Initialize the new GenAI Client
client = genai.Client(api_key=API_KEY)

# --- 3. UI Layout ---
st.title("AI-Powered Study Buddy 🤓")
topic = st.text_input("What do you want to learn?", placeholder="e.g. Quantum Entanglement")

if topic:
    with st.spinner(f"Preparing your lesson on {topic}..."):
        prompt = f"""
        Act as an expert teacher. Create a study guide for: {topic}.
        Include:
        1. A simple explanation with an analogy.
        2. 5 key study bullet points.
        3. 3 multiple-choice questions (include answers at the bottom).
        """
        
        try:
            # We use gemini-2.5-flash, the 2026 workhorse model
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.write("Tip: If you see a 404, try changing the model name to 'gemini-2.0-flash'.")
else:
    st.info("Enter a topic to get started.")
