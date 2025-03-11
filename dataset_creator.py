from pynput import keyboard
import threading
import mediapipe as mp
import cv2

# Function to be triggered when a specific key is pressed
def on_press(key):
    frame = cv2.imread("image.jpg")
    results = mp_hands.process(frame)
    if results.multi_hand_landmarks:
        print(key)
    else:
        print("No Hands")
# Start listening in a separate thread to avoid blocking other keyboard input
def listen_to_keyboard():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# MP Hands Model
mp_hands = mp.solutions.hands.Hands()

# Create a new thread for the listener
listener_thread = threading.Thread(target=listen_to_keyboard)
listener_thread.daemon = True  # Make the thread exit when the program exits
listener_thread.start()



while True:
    pass  # The main program loop can continue doing other tasks

