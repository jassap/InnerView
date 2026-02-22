import cv2
import numpy as np
import time
import threading
import sounddevice as sd
from scipy.io.wavfile import write
from collections import deque
import streamlit as st

def run_tracker_session(st_metric=None, st_progress=None, st_video=None):
    # --- 1. CONFIGURATION ---
    # Load the original Haar Cascades for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    BUFFER_SIZE = 15 
    detection_history = deque(maxlen=BUFFER_SIZE)
    FS, audio_data = 44100, []
    
    state = {
        "active": True, 
        "is_focused": False, 
        "total_focus": 0, 
        "streak_start": 0
    }

    # --- 2. AUDIO RECORDING WORKER ---
    def record_audio_loop():
        nonlocal audio_data
        with sd.InputStream(samplerate=FS, channels=1) as stream:
            while state["active"]:
                data, _ = stream.read(1024)
                audio_data.append(data.copy())

    cap = cv2.VideoCapture(0)
    threading.Thread(target=record_audio_loop, daemon=True).start()
    
    # --- 3. MAIN LOOP WITH SAFETY ---
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            display_frame = frame.copy() 
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Vision Logic (OG Haar)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            eyes_this_frame = 0

            for (x, y, fw, fh) in faces:
                cv2.rectangle(display_frame, (x, y), (x+fw, y+fh), (255, 0, 0), 2)
                roi_gray = gray[y:y+fh, x:x+fw]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                
                if len(eyes) >= 1:
                    ex, ey, ew, eh = eyes[0]
                    eye_roi = roi_gray[ey:ey+eh, ex:ex+ew]
                    _, thresh = cv2.threshold(eye_roi, 60, 255, cv2.THRESH_BINARY_INV)
                    moments = cv2.moments(thresh)
                    
                    if moments['m00'] > 0:
                        cx, cy = int(moments['m10'] / moments['m00']), int(moments['m01'] / moments['m00'])
                        if (0.3 * ew < cx < 0.7 * ew) and (0.3 * eh < cy < 0.7 * eh):
                            eyes_this_frame = 1
                            cv2.circle(display_frame[y:y+fh, x:x+fw], (ex+cx, ey+cy), 3, (0, 255, 255), -1)

            detection_history.append(eyes_this_frame)
            confidence = sum(detection_history) / len(detection_history) if len(detection_history) > 0 else 0

            # --- LIVE WEB UPDATES ---
            # Send frames and metrics to Streamlit placeholders
            if st_video:
                st_video.image(display_frame, channels="BGR", use_container_width=True)

            if confidence > 0.5:
                if not state["is_focused"]:
                    state["streak_start"] = time.time()
                    state["is_focused"] = True
                curr_streak = time.time() - state["streak_start"]
                if st_metric:
                    st_metric.metric("Live Focus Streak", f"{curr_streak:.1f}s", delta="Focused")
                if st_progress:
                    st_progress.progress(min(int(confidence * 100), 100))
            else:
                if state["is_focused"]:
                    state["total_focus"] += (time.time() - state["streak_start"])
                    state["is_focused"] = False
                if st_metric:
                    st_metric.metric("Live Focus Streak", "0.0s", delta="Looking Away", delta_color="inverse")
                if st_progress:
                    st_progress.progress(int(confidence * 100))

            # Backup stop key
            if cv2.waitKey(1) & 0xFF == ord('p'): 
                break

    except Exception:
        # Catch the interruption when 'Stop' is pressed in the web app
        pass

    finally:
        # --- 4. CLEANUP & SAVE ---
        # This section always runs to ensure audio is saved properly
        cap.release()
        state["active"] = False
        
        file_path = "interview_answer.wav"
        if audio_data:
            # Finalize the recording and write the file
            write(file_path, FS, np.concatenate(audio_data, axis=0))
        
        return file_path, state["total_focus"]