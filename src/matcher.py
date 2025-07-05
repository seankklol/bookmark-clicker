"""
Image matching functionality using PyAutoGUI and OpenCV.
"""
import pyautogui
from config import IMAGE_PATH, CONFIDENCE

def find_icon():
    """
    Attempts to locate the bookmark icon on screen.
    
    Returns:
        Box object with coordinates if found, None otherwise.
    """
    try:
        return pyautogui.locateOnScreen(IMAGE_PATH, confidence=CONFIDENCE)
    except Exception as e:
        print(f"Error finding icon: {e}")
        return None
