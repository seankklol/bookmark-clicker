"""
Configuration settings for the bookmark clicker application.
"""

# Image matching settings
IMAGE_PATH = "/Users/chiusean/Downloads/bookmark-clicker/images/bookmark.png"
CONFIDENCE = 0.90

# Timing settings
CLICK_DELAY = 0.5
SCAN_DELAY = 1.0

# Operation settings
WATCHDOG_LIMIT = 100
DOWNSCALE_FACTOR = 0.5  # Less aggressive downscaling
USE_GRAYSCALE = True
BLACKLIST_DURATION = 5  # Extended blacklist duration

# Region settings
TOOLBAR_HEIGHT = 80  # Height of browser toolbar in pixels

# Hotkey settings
TOGGLE_HOTKEY = "<cmd>+<shift>+s"
EXIT_HOTKEY = "<cmd>+<shift>+q"
