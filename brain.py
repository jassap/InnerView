import os
from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def save_to_file(filename, text):
    """Helper function to save text to a specific file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved content to {filename}")

def generate_interview_question(job_role="Computer Scientist"):
    try:
        prompt = f"Generate one behavioral interview question for a {job_role} position. Output ONLY the question.Make it sound like a professional human interviewer. Make the questions shorter."
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        
        # Save question to text file
        save_to_file("current_question.txt", response.text)
        return response.text
    except errors.ClientError as e:
        return f"API Error: {e}"

def get_improved_answer(audio_path):
    try:
        if not os.path.exists(audio_path):
            return f"Error: File {audio_path} not found."

        uploaded_audio = client.files.upload(file=audio_path)
        prompt1="Transcribe this audio"
        response1=client.models.generate_content(model="gemini-2.5-flash", contents=[prompt1, uploaded_audio])

        prompt = "Transcribe this audio of my response to the question you generated " \
        "and give feedback on what I can do better using the STAR method. Make this feedback concise and make sure it's mostly constructive criticism, with some encouragement." \
        "Output ONLY the feedback.Do not say the step names like action or result. Simply give the answer."
        response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, uploaded_audio])
        
        # Save improved answer to text file
        save_to_file("original_answer.txt",response1.text)
        save_to_file("improved_answer.txt", response.text)
        
        
        client.files.delete(name=uploaded_audio.name)
        return response.text
    except errors.ClientError as e:
        return f"API Error: {e}"
    
    # ... (Keep your existing functions above) ...


if __name__ == "__main__":
    print("--- Starting InnerView Brain Test ---")
    
    # 1. This triggers the question generation AND saves 'current_question.txt'
    role = "Data Scientist"
    print(f"Generating question for {role}...")
    question = generate_interview_question(role)
    print(f"Result: {question}")
    
    # 2. This triggers the improvement AND saves 'improved_answer.txt'
    # Make sure 'test_audio.wav' is in your /Users/snehal/InnerView/ folder!
    target_audio = "interview_answer.wav"
    
    if os.path.exists(target_audio):
        print(f"\nImproving answer from {target_audio}...")
        improved = get_improved_answer(target_audio)
        print(f"Result: {improved}")
    else:
        print(f"\n Skip improvement test: '{target_audio}' not found.")