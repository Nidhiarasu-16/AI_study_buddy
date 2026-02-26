import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="AI-Powered Study Buddy", page_icon="🧠")
st.title("AI-Powered Study Buddy 🤓")
st.write("""
Enter any topic, and get:
- Simple explanation  
- Summarized study notes  
- Quiz questions / flashcards
""")

# --- Input topic ---
topic = st.text_input("Enter a topic you want to study:")

if topic:
    st.subheader("Generating results...")
    
    # Spinner to show processing
    with st.spinner("Processing your topic..."):
        try:
            # --- 1. Explain in simple terms ---
            explainer = pipeline("text2text-generation", model="google/flan-t5-small")
            explanation = explainer(f"Explain {topic} in simple terms for a student.", max_length=200)[0]["generated_text"]
            
            # --- 2. Summarize notes ---
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            summary = summarizer(explanation, max_length=100, min_length=40, do_sample=False)[0]["summary_text"]
            
            # --- 3. Generate quiz questions ---
            quiz_generator = pipeline("text-generation", model="distilgpt2")
            quiz_prompt = f"Generate 5 multiple-choice questions from this content:\n{summary}"
            quiz = quiz_generator(quiz_prompt, max_length=250, do_sample=True, temperature=0.7)[0]["generated_text"]
            
        except Exception as e:
            st.error(f"Error generating content: {e}")
            st.stop()
    
    # --- Display results ---
    st.subheader("📘 Simple Explanation")
    st.write(explanation)
    
    st.subheader("📝 Summarized Notes")
    st.write(summary)
    
    st.subheader("❓ Quiz / Flashcards")
    st.write(quiz)
    
else:
    st.info("Please enter a topic to generate study content.")
