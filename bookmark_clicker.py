"""
Bookmark Clicker

This script automates the detection and clicking of a specified bookmark icon within the
active browser window on macOS.

Functionality:
- At launch, it determines the active browser window's region.
- It repeatedly scans this region for a bookmark image.
- It clicks on each found instance of the bookmark.
- A global hotkey (Command+Shift+S) can be used to pause and resume the script.
- The script stops automatically after a predefined number of clicks (watchdog_limit).

Usage:
1. Make sure you have enabled Accessibility permissions for your terminal or IDE.
   (System Settings -> Privacy & Security -> Accessibility)
2. Run `pip install -r requirements.txt`.
3. Update the CONFIG section in the script if needed.
4. Run the script: `python bookmark_clicker.py`
"""
import subprocess
import time
import logging
import sys
import os
import threading
from typing import Optional, Tuple, List

import cv2
import numpy as np
import pyautogui
from pynput import keyboard
from PIL import Image

# --- CONFIGURATION ---
from src.config import (
    IMAGE_PATH, CONFIDENCE, CLICK_DELAY, SCAN_DELAY,
    WATCHDOG_LIMIT, DOWNSCALE_FACTOR, USE_GRAYSCALE,
    BLACKLIST_DURATION, TOOLBAR_HEIGHT, TOGGLE_HOTKEY
)

CONFIG = {
    "image_path": IMAGE_PATH,
    "confidence": CONFIDENCE,
    "click_delay": CLICK_DELAY,
    "scan_delay": SCAN_DELAY,
    "watchdog_limit": WATCHDOG_LIMIT,
    "downscale_factor": DOWNSCALE_FACTOR,
    "use_grayscale": USE_GRAYSCALE,
    "blacklist_duration": BLACKLIST_DURATION,
    "hotkey": TOGGLE_HOTKEY
}

# --- GLOBAL STATE ---
STATE = {
    "paused": True,
    "running": True,
    "click_count": 0,
    "region": None, # (x, y, width, height)
}

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("bookmark_clicker.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def get_browser_region() -> Optional[Tuple[int, int, int, int]]:
    """Gets the active browser window's toolbar region using AppleScript."""
    applescript = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    try
        tell application frontApp
            if frontApp is in {"Google Chrome", "Safari", "Firefox", "Microsoft Edge", "Brave Browser"} then
                get bounds of front window
            else
                error "Active window is not a supported browser."
            end if
        end tell
    on error
        return missing value
    end try
    '''
    try:
        proc = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(applescript)

        if proc.returncode != 0 or "missing value" in stdout:
            logging.error(f"AppleScript Error: {stderr.strip()}")
            return None

        bounds_str = stdout.strip()
        x, y, x2, y2 = [int(v) for v in bounds_str.split(', ')]
        logging.info(f"Detected browser region: ({x}, {y}, {x2-x}, {y2-y})")
        # Only return the toolbar region
        return (x, y, x2 - x, TOOLBAR_HEIGHT)
    except Exception as e:
        logging.error(f"Failed to execute AppleScript: {e}")
        return None

def group_rectangles(rects: List[Tuple[int, int, int, int]], threshold: int = 10) -> List[Tuple[int, int, int, int]]:
    """Groups overlapping rectangles to avoid multiple clicks on the same item."""
    if not rects:
        return []

    # Sort rectangles by their x-coordinate
    rects.sort(key=lambda r: r[0])
    
    grouped = []
    current_group = list(rects[0])

    for i in range(1, len(rects)):
        rect = rects[i]
        # Check for overlap or proximity
        if rect[0] < current_group[0] + current_group[2] + threshold:
            # Merge rectangles
            new_x2 = max(current_group[0] + current_group[2], rect[0] + rect[2])
            new_y2 = max(current_group[1] + current_group[3], rect[1] + rect[3])
            current_group[0] = min(current_group[0], rect[0])
            current_group[1] = min(current_group[1], rect[1])
            current_group[2] = new_x2 - current_group[0]
            current_group[3] = new_y2 - current_group[1]
        else:
            grouped.append(tuple(current_group))
            current_group = list(rect)
    
    grouped.append(tuple(current_group))
    return grouped

def automation_loop():
    """The main loop for screenshotting, matching, and clicking."""
    logging.info("Automation loop started. Press hotkey to begin.")

    # Initialize blacklist and history for coordinates
    blacklist = {}  # (x, y) -> rounds left
    last_clicked = set()

    try:
        # Load and process template image
        template = cv2.imread(CONFIG["image_path"], cv2.IMREAD_GRAYSCALE)
        if template is None:
            logging.error(f"Failed to load template image from {CONFIG['image_path']}")
            STATE["running"] = False
            return
    except Exception as e:
        logging.error(f"Failed to load template: {e}")
        STATE["running"] = False
        return

    h, w = template.shape
    while STATE["running"]:
        if STATE["paused"]:
            time.sleep(0.5)
            continue

        try:
            # Refresh browser region periodically
            new_region = get_browser_region()
            if new_region:
                STATE['region'] = new_region
            else:
                logging.warning('Browser region lost. Falling back to full screen.')
                STATE['region'] = (0, 0, *pyautogui.size())

            # Take a screenshot of the browser region
            try:
                screenshot = pyautogui.screenshot(region=STATE["region"])
            except pyautogui.FailSafeException:
                logging.error('PyAutoGUI fail-safe triggered. Stopping.')
                STATE['running'] = False
                continue
            
            # Convert screenshot for template matching
            screenshot_cv = np.array(screenshot)
            if CONFIG['use_grayscale']:
                screenshot_cv = cv2.cvtColor(screenshot_cv, cv2.COLOR_RGB2GRAY)
                template = cv2.imread(CONFIG["image_path"], cv2.IMREAD_GRAYSCALE)
            else:
                template = cv2.imread(CONFIG["image_path"], cv2.IMREAD_COLOR)

            # Downscale both images for faster processing if needed
            if CONFIG['downscale_factor'] < 1.0:
                h, w = screenshot_cv.shape[:2]
                new_h = int(h * CONFIG["downscale_factor"])
                new_w = int(w * CONFIG["downscale_factor"])
                screenshot_cv = cv2.resize(screenshot_cv, (new_w, new_h))
                template = cv2.resize(template, (0, 0), fx=CONFIG["downscale_factor"], fy=CONFIG["downscale_factor"])

            # Perform multi-scale template matching
            matches = match_template_at_scales(screenshot_cv, template)

            unique_rects = group_rectangles(matches)

            if not unique_rects:
                logging.info("No bookmarks found in this scan.")
            else:
                logging.info(f"Found {len(unique_rects)} unique bookmarks.")

            # --- BLACKLIST LOGIC START ---
            # Decrement blacklist and remove expired
            expired = []
            for coord in blacklist:
                blacklist[coord] -= 1
                if blacklist[coord] <= 0:
                    expired.append(coord)
            for coord in expired:
                del blacklist[coord]

            current_clicked = set()
            # 3. Click & Count
            for rect in unique_rects:
                if STATE["paused"] or not STATE["running"]:
                    break
                
                # Validate coordinates are within screen bounds
                screen_width, screen_height = pyautogui.size()
                if not (0 <= rect[0] <= screen_width and 0 <= rect[1] <= screen_height):
                    logging.warning(f'Invalid coordinate {rect} outside screen bounds ({screen_width}x{screen_height})')
                    continue

                # Map back to full resolution
                original_x = int((rect[0] + rect[2] / 2)) + STATE["region"][0]
                original_y = int((rect[1] + rect[3] / 2)) + STATE["region"][1]

                # Blacklist check
                if coord in blacklist:
                    logging.info(f"Skipping blacklisted coordinate {coord}")
                    continue

                # If this coordinate was clicked last round, blacklist it for 2 rounds
                if coord in last_clicked:
                    blacklist[coord] = CONFIG['blacklist_duration']
                    logging.info(f"Blacklisting coordinate {coord} for {CONFIG['blacklist_duration']} rounds")
                    continue

                pyautogui.click(original_x, original_y)
                STATE["click_count"] += 1
                logging.info(f"Clicked bookmark #{STATE['click_count']} at ({original_x}, {original_y})")
                current_clicked.add(coord)

                if STATE["click_count"] >= CONFIG["watchdog_limit"]:
                    logging.info(f"Watchdog limit of {CONFIG['watchdog_limit']} reached. Stopping.")
                    STATE["running"] = False
                    break

                time.sleep(CONFIG["click_delay"])

            # Update last_clicked for next round
            last_clicked = current_clicked
            # --- BLACKLIST LOGIC END ---

        except Exception as e:
            logging.error(f"An error occurred in the automation loop: {e}")
            # Optional: could pause or stop on error
            # STATE["paused"] = True

        time.sleep(CONFIG["scan_delay"])

    logging.info("Automation loop finished.")

def on_toggle_pause():
    """Callback function for the hotkey to toggle pause/resume."""
    STATE["paused"] = not STATE["paused"]
    status = "Paused" if STATE["paused"] else "Resumed"
    logging.info(f"--- {status} ---")

def on_exit():
    """Callback function to stop the script."""
    logging.info("Exit hotkey pressed. Shutting down.")
    STATE["running"] = False

def main():
    """Main function to set up and run the application."""
    logging.info("Starting Bookmark Clicker.")

    # Set up a listener for the exit hotkey first, so the user can always quit.
    exit_listener = keyboard.GlobalHotKeys({
        '<cmd>+<shift>+q': on_exit
    })
    exit_listener.start()
    logging.info("Press <cmd>+<shift>+q to quit at any time.")

    # Check for accessibility permissions (heuristic)
    if not pyautogui.onScreen(0, 0):
        logging.warning("Accessibility permissions may not be granted. This is a common cause of issues.")
        logging.warning("Please ensure your terminal/IDE has accessibility access in System Settings.")

    # Repeatedly try to get the browser region until successful
    logging.info("Attempting to detect a supported browser window...")
    logging.info("Please make sure the browser is the frontmost window.")
    
    while STATE["region"] is None and STATE["running"]:
        STATE["region"] = get_browser_region()
        if STATE["region"] is None:
            # Check if we should stop, in case the exit hotkey was pressed
            if not STATE["running"]:
                break
            logging.info("Browser not detected. Retrying in 2 seconds...")
            time.sleep(2)
    
    if not STATE["running"] or STATE["region"] is None:
        logging.info("Could not detect browser or shutdown was requested. Exiting.")
        exit_listener.stop()
        return
    
    logging.info("Browser detected successfully!")

    # Start the automation loop in a separate thread
    automation_thread = threading.Thread(target=automation_loop, daemon=True)
    automation_thread.start()

    # Set up and start the hotkey listener for pausing
    # We can't just add to the existing listener, so we stop it and create a new one.
    exit_listener.stop()
    hotkey_map = {
        CONFIG["hotkey"]: on_toggle_pause,
        '<cmd>+<shift>+q': on_exit,
    }
    
    listener = keyboard.GlobalHotKeys(hotkey_map)
    listener.start()
    logging.info(f"Hotkey listener started. Press {CONFIG['hotkey']} to toggle pause/resume.")
    
    try:
        # Keep the main thread alive to listen for hotkeys
        automation_thread.join()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Shutting down.")
    finally:
        STATE["running"] = False
        if listener.is_alive():
            listener.stop()
        logging.info("Application has been shut down.")

if __name__ == "__main__":
    main()
