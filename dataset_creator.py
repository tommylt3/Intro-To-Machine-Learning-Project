from pynput import keyboard
import mediapipe as mp
import cv2
import pandas as pd

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
pressed_keys = list()
df = pd.DataFrame()
cap = cv2.VideoCapture(0)

def on_press(key):
    global pressed_keys
    pressed_keys += [key]

def on_release(key):
    global df
    global hands
    global cap
    try:
        if not cap.isOpened():
            print(f"Camera Blocked with key {key.char}")
            return
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to Capture with key {key.char}")
            return
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        if results.multi_hand_landmarks:
            print(len(results.multi_hand_landmarks))

    except:
        raise(AttributeError())

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

while True:
    pass
