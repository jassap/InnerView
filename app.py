import streamlit as st
import brain
import voice
import TrackerLogic
import os

# 1. Custom Page Layout
st.set_page_config(page_title="InnerView AI", layout="wide", page_icon="🧠")

# --- INITIALIZATION (Fixes the AttributeError) ---
# Ensure these variables exist the moment the app loads
if "app_state" not in st.session_state:
    st.session_state.app_state = "idle"

if "focus_score" not in st.session_state:
    st.session_state.focus_score = 0.0

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# 2. Sidebar with Reset Button
with st.sidebar:
    st.title("🛡️ Pulse-Check")
    role = st.selectbox("Interviewing for:", ["Data Scientist", "Software Engineer", "Computer Scientist"])
    
    st.divider()
    
    # Start Button
    if st.button("🚀 Start Mock Interview", use_container_width=True):
        st.session_state.app_state = "asking"
        st.rerun()

    # Reset Button
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.app_state = "idle"
        st.session_state.focus_score = 0.0
        st.session_state.current_question = ""
        # Clean up old files if they exist
        for f in ["interview_answer.wav", "original_answer.txt", "improved_answer.txt"]:
            if os.path.exists(f): os.remove(f)
        st.rerun()

# 3. Main Logic Flow
st.title("InnerView AI Interview Coach")

if st.session_state.app_state == "idle":
    st.info("Select your role in the sidebar and click Start to begin.")

elif st.session_state.app_state == "asking":
    with st.spinner("AI Coach is generating a custom question..."):
        question = brain.generate_interview_question(role)
        st.session_state.current_question = question
        st.subheader("Current Question:")
        st.info(question)
        voice.speak_from_file("current_question.txt")
        st.session_state.app_state = "recording"
        st.rerun()

if st.session_state.app_state == "recording":
    st.subheader("Current Question:")
    st.info(st.session_state.current_question)
    st.warning("Recording in progress... Maintain eye contact!")
    
    # Stop Button (Browser-based)
    if st.button("🛑 Stop & Analyze", type="primary", use_container_width=True):
        st.session_state.app_state = "analysis"
        st.rerun()

    # Video and Metric Placeholders
    video_placeholder = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        focus_metric = st.empty()
    with col2:
        progress_bar = st.empty()

    # Run the tracker session
    audio_file, focus_score = TrackerLogic.run_tracker_session(focus_metric, progress_bar, video_placeholder)
    st.session_state.focus_score = focus_score

if st.session_state.app_state == "analysis":
    # Safely retrieve score from state
    final_score = st.session_state.get("focus_score", 0.0)
    st.success(f"Session Finished!")
    import time
    time.sleep(1.5)
    audio_path = "interview_answer.wav"
    if os.path.exists(audio_path):
        with st.spinner("Analyzing your STAR response..."):
            # Gemini improves the answer from the saved audio
            improved_text = brain.get_improved_answer("interview_answer.wav")
        
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Your Transcript:")
                if os.path.exists("original_answer.txt"):
                    with open("original_answer.txt", "r") as f:
                        st.text_area("Original Response", f.read(), height=250)
            with col2:
                st.subheader("Coach's Improvement:")
                st.write(improved_text)
                voice.speak_from_file("improved_answer.txt")