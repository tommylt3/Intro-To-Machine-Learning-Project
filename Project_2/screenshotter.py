from PIL import ImageGrab
import numpy as np
from pynput import keyboard
from pynput.keyboard import Controller
import pyautogui
import asyncio
import threading

cKey = None
injection_controller = Controller()

def get_image(left, top, width, height):
    printscreen_pil = ImageGrab.grab((left, top, left + width, top + height))
    printscreen_numpy = np.array(printscreen_pil.getdata(), dtype='uint8') \
        .reshape((printscreen_pil.size[1], printscreen_pil.size[0], 3))
    return printscreen_numpy

# Function that will insert key presses
async def inject_key(key):
    pyautogui.press(key)
    print(f"Pressed {key}")

# Function that will be called on key press
def on_press(key):
    try:
        if key.char == '3':
            asyncio.run_coroutine_threadsafe(inject_key('w'), loop)
        elif key.char == '4':
            asyncio.run_coroutine_threadsafe(inject_key('a'), loop)
    except AttributeError:
        pass

# Function to run the listener in a thread
def listen_for_keypress():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Main async function
async def main():
    global loop
    loop = asyncio.get_event_loop()

    # Run the listener in a separate thread since it's blocking
    threading.Thread(target=listen_for_keypress, daemon=True).start()

    # Run your main task, e.g., capture an image periodically
    while True:
        await asyncio.sleep(5)

# Start the async program
if __name__ == "__main__":
    asyncio.run(main())

