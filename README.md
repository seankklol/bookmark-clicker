# Bookmark Clicker

This script automates the detection and clicking of a specified bookmark icon within the active browser window on macOS.

## Features

- **Automatic Region Detection**: At startup, the script identifies the active browser window (supports Chrome, Safari, Firefox, Edge, and Brave) and confines its search to that area.
- **Image-Based Automation**: It repeatedly scans the region for a target image (`bookmark.png`) and clicks on every match.
- **User Control**: A global hotkey (`⌘+⇧+S`) allows you to pause and resume the automation at any time. A safety hotkey (`⌘+⇧+Q`) is available to stop the script immediately.
- **Configurable**: Key parameters like delays, click limits, and match confidence are easily adjustable within the script.
- **Logging**: All actions are logged to the console and a `bookmark_clicker.log` file for easy monitoring and debugging.

## Prerequisites

- macOS 12.0 or newer
- Python 3.10 or newer

## Setup & Installation

### 1. Grant Accessibility Permissions

For the script to control your mouse and take screenshots, you must grant accessibility permissions.

1.  Open **System Settings**.
2.  Go to **Privacy & Security** → **Accessibility**.
3.  Add your terminal application (e.g., `Terminal.app`, `iTerm.app`) or your code editor (e.g., `Visual Studio Code`) to the list and ensure it is enabled.

### 2. Set Up the Python Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# Navigate to the project directory
cd /path/to/bookmark-clicker

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

## Configuration

Before running the script, you can adjust its behavior by editing the `CONFIG` dictionary at the top of `bookmark_clicker.py`:

- `image_path`: The path to the bookmark image to be detected.
- `confidence`: The accuracy of the image match (0.0 to 1.0). Default is `0.90`.
- `click_delay`: The time in seconds to wait between each click. Default is `0.5`.
- `scan_delay`: The time in seconds to wait between each full scan of the screen region. Default is `1.0`.
- `watchdog_limit`: The maximum number of clicks before the script stops automatically. Default is `100`.

## Usage

1.  Make sure a supported browser window is open and is the frontmost window on your screen.
2.  Activate the virtual environment if you haven't already:
    ```bash
    source venv/bin/activate
    ```
3.  Run the script:
    ```bash
    python bookmark_clicker.py
    ```

### Hotkeys

- **Pause / Resume**: `⌘+⇧+S` (Command + Shift + S)
  - The script starts in a **paused** state. Press the hotkey once to begin the automation.
- **Quit**: `⌘+⇧+Q` (Command + Shift + Q)
  - This will gracefully stop the script and the hotkey listener.
# bookmark-clicker
