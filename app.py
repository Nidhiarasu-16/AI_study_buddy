import streamlit as st
import google.generativeai as genai

# --- 1. Page Config ---
st.set_page_config(page_title="AI Study Buddy", page_icon="🧠", layout="centered")

# --- 2. API Setup ---
# Access your key from Streamlit Secrets (for Cloud) or st.sidebar (for testing)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    st.info("Please add your Google API Key to continue.")
    st.stop()

genai.configure(api_key=api_key)

# --- 3. Model Initialization (with Error Handling) ---
try:
    # 'gemini-1.5-flash' is the most reliable for study tools
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Model Error: {e}")
    st.stop()

# --- 4. UI Layout ---
st.title("AI-Powered Study Buddy 🤓")
st.markdown("Transform any topic into a structured lesson plan instantly.")

topic = st.text_input("What do you want to learn?", placeholder="e.g. Black Holes, Photosynthesis, Roman Empire")

if topic:
    with st.spinner(f"Analyzing '{topic}'..."):
        # The "Super Prompt" - Instructions for formatting and tone
        prompt = f"""
        Act as a world-class educational tutor. Create a study guide for the topic: {topic}.
        Please structure your response exactly as follows:
        
        # 📘 Simple Explanation
        Explain this like I'm a high school student. Use an analogy.
        
        # 📝 Key Study Notes
        - Provide 5 bullet points of the most critical facts.
        - Bold the key terms.
        
        # ❓ Quick Quiz
        - Provide 3 multiple-choice questions.
        - Provide the answers at the very end inside a 'collapsible' format.
        """

        try:
            response = model.generate_content(prompt)
            content = response.text
            
            # Displaying the content
            st.markdown("---")
            st.markdown(content)
            
            st.success("Study guide generated!")
            
            # Bonus: Download Button
            st.download_button(
                label="Download Notes as Text",
                data=content,
                file_name=f"{topic.replace(' ', '_')}_notes.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Generation failed: {e}")

else:
    st.info("Enter a topic above to generate your study materials.")
