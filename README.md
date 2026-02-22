# InnerView AI: Pulse-Check Interview Coach

InnerView AI is an intelligent mock interview platform designed to help candidates master the **STAR method** (Situation, Task, Action, Result) while improving their non-verbal communication. Built for the HackHERS 2026 hackathon, the application uses real-time computer vision to track eye contact and Generative AI to provide personalized behavioral feedback.

## 🚀 Features

* **Real-Time Eye Tracking**: Uses OpenCV Haar Cascades to monitor eye contact during your response, providing a "Focus Score" and live visual feedback directly in the browser.
* **AI Interview Coach**: Generates role-specific behavioral questions (e.g., Data Scientist, Software Engineer) using the Gemini 2.5 Flash model.
* **Voice Integration**: The AI coach "speaks" questions and feedback using ElevenLabs' high-fidelity text-to-speech technology.
* **STAR Method Analysis**: Automatically transcribes your spoken answer and provides a refined version following the STAR method for maximum impact.
* **Live Dashboard**: A Streamlit-based web interface featuring a live camera feed, focus metrics, and a STAR-formatted improvement transcript.

## 🛠️ Technology Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **AI/LLM**: Google Gemini 2.5 Flash
* **Computer Vision**: OpenCV (Haar Cascade Classifiers)
* **Voice**: ElevenLabs API
* **Audio**: Sounddevice & SciPy

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

* Python 3.12+
* A webcam and microphone

## ⚙️ Installation & Setup

1. **Clone the Repository**:
```bash
git clone https://github.com/jassap/InnerView.git
cd InnerView

```


2. **Set Up a Virtual Environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate

```


3. **Install Dependencies**:
```bash
pip install streamlit google-genai elevenlabs opencv-contrib-python sounddevice scipy python-dotenv

```


4. **Environment Variables**:
Create a `.env` file in the root directory and add your API keys:
```text
GEMINI_API_KEY=your_google_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key

```



## 🖥️ Usage

1. **Run the Application**:
```bash
python3 -m streamlit run app.py

```


2. **Conduct an Interview**:
* Select your target **Job Role** in the sidebar.
* Click **🚀 Start Mock Interview** to hear the AI generate a question.
* Maintain eye contact with the camera while speaking. Use the **Live Focus Streak** and **Progress Bar** to monitor your performance.
* Click **🛑 Stop & Analyze** to end the session.
* Review your **Original Response** and the **Coach's Improvement** based on the STAR method.



## 📁 Project Structure

* `app.py`: The main Streamlit web application and UI logic.
* `TrackerLogic.py`: The computer vision engine for eye tracking and audio recording.
* `brain.py`: Integration with Google Gemini for question generation and answer refinement.
* `voice.py`: ElevenLabs integration for text-to-speech functionality.

---

*Created for HackHERS 2026 by Jashmitha, Snehal, and Shrimayi.*
