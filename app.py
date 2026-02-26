import streamlit as st
import google.generativeai as genai
import os

# --- Configuration ---
# Get your API key from https://aistudio.google.com/
# For security, it's best to use st.secrets or an environment variable
API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Study Buddy", page_icon="🧠", layout="wide")

st.title("AI-Powered Study Buddy 🤓")
st.markdown("---")

# Input section
topic = st.text_input("What do you want to learn today?", placeholder="e.g., Photosynthesis, Quantum Physics, The French Revolution")

if topic:
    with st.spinner(f"Mastering {topic}... hang tight!"):
        try:
            # We use a single prompt to get structured data back. 
            # This is faster and more cohesive than 3 separate calls.
            prompt = f"""
            Act as an expert tutor. Provide the following for the topic: {topic}
            
            1. SIMPLE EXPLANATION: Explain it like I'm 15.
            2. STUDY NOTES: 5-7 bullet points of the most important facts.
            3. QUIZ: 3 multiple-choice questions with answers hidden at the bottom.
            
            Format everything clearly using Markdown.
            """
            
            response = model.generate_content(prompt)
            full_text = response.text

            # Displaying the results in organized tabs
            tab1, tab2, tab3 = st.tabs(["📘 Explanation", "📝 Study Notes", "❓ Quiz"])

            # Logic to split the response if needed, or just show the whole thing
            # For simplicity, we'll display the AI's formatted markdown
            with tab1:
                st.markdown(full_text.split("2. STUDY NOTES")[0])
            with tab2:
                # Extracting the notes section
                notes_part = full_text.split("2. STUDY NOTES")[1].split("3. QUIZ")[0]
                st.markdown(notes_part)
            with tab3:
                quiz_part = full_text.split("3. QUIZ")[1]
                st.markdown(quiz_part)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.info("Enter a topic above to begin your study session.")
