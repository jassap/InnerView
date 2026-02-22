import brain
import voice
import os
import time

def run_interview_session():
    # STEP 1: Gemini creates the question
    print("\n--- Phase 1: AI Coach is asking a question ---")
    question = brain.generate_interview_question("Data Scientist")
    print(f"Gemini Generated: {question}")
    
    # STEP 2: ElevenLabs speaks the question from the file Gemini just made
    # (brain.py saves this as 'current_question.txt')
    voice.speak_from_file("current_question.txt")

    # STEP 3: Pause for you to record (Integration point for eyecontactcheck.py)
    print("\n[Action Required] Record your answer to 'test_audio.wav' now...")
    input("Press Enter once 'test_audio.wav' is ready for analysis...")

    # STEP 4: Gemini improves the answer from the audio file
    if os.path.exists("interview_answer.wav"):
        print("\n--- Phase 2: Gemini is refining your answer ---")
        improved_text = brain.get_improved_answer("interview_answer.wav")
        print(f"Improved STAR Version: {improved_text}")
        
        # STEP 5: ElevenLabs speaks the improved version
        # (brain.py saves this as 'improved_answer.txt')
        voice.speak_from_file("improved_answer.txt")
    else:
        print("Error: 'test_audio.wav' not found. Cannot improve answer.")

if __name__ == "__main__":
    run_interview_session()
