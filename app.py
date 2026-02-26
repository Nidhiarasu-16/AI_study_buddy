# app.py

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

# Input topic
topic = st.text_input("Enter a topic you want to study:")

if topic:
    st.subheader("Generating results...")
    
    with st.spinner("Processing your topic..."):
        try:
            # --- 1. Explain topic ---
            generator = pipeline("text-generation", model="distilgpt2")
            explanation_prompt = f"Explain the topic '{topic}' in simple terms for a student."
            explanation = generator(explanation_prompt, max_length=200, do_sample=True, temperature=0.7)[0]["generated_text"]
            
            # --- 2. Summarize notes ---
            summary_prompt = f"Summarize the following explanation into concise study notes:\n{explanation}"
            summary = generator(summary_prompt, max_length=150, do_sample=True, temperature=0.7)[0]["generated_text"]
            
            # --- 3. Generate quiz questions ---
            quiz_prompt = f"Create 5 multiple-choice quiz questions from the following study notes:\n{summary}"
            quiz = generator(quiz_prompt, max_length=250, do_sample=True, temperature=0.7)[0]["generated_text"]
            
        except Exception as e:
            st.error(f"Error generating content: {e}")
            st.stop()
    
    # Display results
    st.subheader("📘 Simple Explanation")
    st.write(explanation)
    
    st.subheader("📝 Study Notes")
    st.write(summary)
    
    st.subheader("❓ Quiz / Flashcards")
    st.write(quiz)
    
else:
    st.info("Please enter a topic to generate study content.")
