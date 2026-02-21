import cv2
import mediapipe as mp
import numpy as np
import time
import sounddevice as sd
from scipy.io.wavfile import write
import threading

# --- INITIALIZATION ---
mp_face_mesh = mp.solutions.face_mesh
# Legacy API: 478 points includes irises (indices 468-477)
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
cap = cv2.VideoCapture(0)

# --- AUDIO & SESSION SETTINGS ---
fs = 44100  
audio_data = []
session_active = False
recording_thread = None

# --- TRACKING VARIABLES ---
total_focus_time = 0
is_currently_focused = False
streak_start_time = None

# Iris & Eye Indices
LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133
LEFT_IRIS_CENTER = 468

def record_audio_loop():
    """Background thread function for recording audio."""
    global audio_data
    with sd.InputStream(samplerate=fs, channels=1) as stream:
        while session_active:
            data, _ = stream.read(1024)
            audio_data.append(data.copy())

print("--- CONTROLS ---")
print("S: Start Session | P: Pause & Save | R: Reset Timer | Q: Quit")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    key = cv2.waitKey(1) & 0xFF
    
    # 1. HANDLE SESSION STATE CHANGES
    if key == ord('s') and not session_active:
        session_active = True
        audio_data = [] 
        # Start the background audio thread
        recording_thread = threading.Thread(target=record_audio_loop)
        recording_thread.start()
        print(">>> Recording Started")

    elif key == ord('p') and session_active:
        session_active = False # Stops the audio thread
        if is_currently_focused:
            total_focus_time += (time.time() - streak_start_time)
            is_currently_focused = False
        
        # Save recording if data exists
        if audio_data:
            full_audio = np.concatenate(audio_data, axis=0)
            write("interview_answer.wav", fs, full_audio)
            print(">>> Saved to 'interview_answer.wav'")

    elif key == ord('r'):
        total_focus_time = 0
        print(">>> Timer Reset")

    elif key == ord('q'): break

    # 2. RENDER UI BASED ON STATE
    if session_active:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        display_text = "Looking for eyes..."
        color = (255, 255, 255)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                def get_px(idx):
                    lm = face_landmarks.landmark[idx]
                    return np.array([lm.x * w, lm.y * h])

                # Calculate Ratio
                l_outer = get_px(LEFT_EYE_OUTER)
                l_inner = get_px(LEFT_EYE_INNER)
                l_iris = get_px(LEFT_IRIS_CENTER)
                
                ratio = np.linalg.norm(l_iris - l_inner) / np.linalg.norm(l_outer - l_inner)

                if 0.42 < ratio < 0.58: # FOCUSING
                    if not is_currently_focused:
                        streak_start_time = time.time()
                        is_currently_focused = True
                    display_text = f"FOCUSING: {time.time() - streak_start_time:.1f}s"
                    color = (0, 255, 0)
                else: # DISTRACTED
                    if is_currently_focused:
                        total_focus_time += (time.time() - streak_start_time)
                        is_currently_focused = False
                    display_text = "LOOKING AWAY"
                    color = (0, 0, 255)
                
                # Draw visual iris tracker
                cv2.circle(frame, tuple(l_iris.astype(int)), 3, (255, 255, 255), -1)

        # Active Session UI
        cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1) # Red REC Dot
        cv2.putText(frame, display_text, (55, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Session Total: {total_focus_time:.1f}s", (30, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    else:
        # --- BLANK/STANDBY SCREEN ---
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 0), -1) 
        cv2.putText(frame, "SESSION PAUSED", (w//4, h//2 - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, "Press 'S' to Start Recording", (w//4, h//2 + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, f"Last Focus Score: {total_focus_time:.1f}s", (w//4, h//2 + 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('MediaPipe Interview Coach v1.1', frame)

cap.release()
cv2.destroyAllWindows()