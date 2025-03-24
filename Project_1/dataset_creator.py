from pynput import keyboard
import mediapipe as mp
import cv2
import pandas as pd
import os
import time

# Media Pipe, for Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Check if CSV exists, if not, create a new DataFrame with the column names
columns = ['key'] + ['last_key'] + \
          [f'left_{i}_x' for i in range(21)] + [f'left_{i}_y' for i in range(21)] + [f'left_{i}_z' for i in range(21)] + \
          [f'right_{i}_x' for i in range(21)] + [f'right_{i}_y' for i in range(21)] + [f'right_{i}_z' for i in range(21)]
file_path = 'keys.csv'
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns = pd.Index(columns))

# Camera Feed
cap = cv2.VideoCapture(0)
lKey = ord('\u23CE')

# On Key Press, Capture Hands
def on_press(key):
    global df
    global hands
    global cap
    global lKey
    special_keys = {
        keyboard.Key.space: '\u0020',
        keyboard.Key.enter: '\u23CE',
        keyboard.Key.tab: '\u0009',
        keyboard.Key.shift: '\u21E7',
        keyboard.Key.ctrl_l: '\u2303',
        keyboard.Key.ctrl_r: '\u2303',
        keyboard.Key.alt_l: '\u2325',
        keyboard.Key.alt_r: '\u2325',
        keyboard.Key.cmd: '\u2318',
        keyboard.Key.esc: '\u238B',
        keyboard.Key.backspace: '\u232B',
        keyboard.Key.delete: '\u2326',
    }
    cKey = None
    try:
        if hasattr(key, 'char') and key.char is not None:
            cKey = ord(key.char)
        else:
            # Handle special keys
            cKey = ord(special_keys.get(key, str(key)))
    except Exception as e:
        cKey = ord('\u0000')

    try:
        if not cap.isOpened():
            print(f"Camera Blocked with key {cKey}")
            return
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to Capture with key {cKey}")
            return
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            # Initialize empty lists for left and right hand landmarks
            left_hand_landmarks = [None] * 21
            right_hand_landmarks = [None] * 21

            # Sets Initial Counter
            key_counter = 0

            # Iterate through detected hands
            for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Extract x, y, z coordinates for each landmark
                landmarks = [(landmark.x, landmark.y, landmark.z) for landmark in hand_landmarks.landmark]

                # Store the landmarks in the respective hand variables
                if hand_index == 0:  # Left hand
                    left_hand_landmarks = landmarks
                elif hand_index == 1:  # Right hand
                    right_hand_landmarks = landmarks

            # Prepare the row data
            row = [cKey]
            row += [lKey]
            # Add left hand landmarks to the row (x, y, z for each of the 21 landmarks)
            row += [coord[0] for coord in left_hand_landmarks]  # left_x for all 21 landmarks
            row += [coord[1] for coord in left_hand_landmarks]  # left_y for all 21 landmarks
            row += [coord[2] for coord in left_hand_landmarks]  # left_z for all 21 landmarks

            # Add right hand landmarks to the row (x, y, z for each of the 21 landmarks)
            row += [coord[0] for coord in right_hand_landmarks]  # right_x for all 21 landmarks
            row += [coord[1] for coord in right_hand_landmarks]  # right_y for all 21 landmarks
            row += [coord[2] for coord in right_hand_landmarks]  # right_z for all 21 landmarks

            # Append the row into the DataFrame
            df.loc[len(df)] = row

                # Increment the key counter for the next row
            key_counter += 1
            lKey = cKey
    except:
        raise(AttributeError())

def save_data_to_csv():
    # Save the updated DataFrame to CSV after 1 minute
    global df
    print("Saving data to CSV...")
    df.to_csv(file_path, index=True)
    print("Data saved to keys.csv")

listener = keyboard.Listener(on_press=on_press)
listener.start()

try:
    time.sleep(3600)  # Sleep for 1 Hour
    save_data_to_csv()
except KeyboardInterrupt:
    print("Program interrupted.")
    save_data_to_csv()

