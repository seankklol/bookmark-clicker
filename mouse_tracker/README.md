# Mouse Tracker

A simple Python application that:
1. Shows the current mouse coordinates in real-time
2. Allows you to move the mouse to specific coordinates

## Requirements
- Python 3.6+
- tkinter (usually comes with Python)
- pyautogui

## Installation

1. Create a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install the required packages:
```
pip install -r requirements.txt
```

## Usage

Run the application:
```
python mouse_tracker.py
```

### Features
- The application shows your current mouse position in real-time
- Enter X and Y coordinates and click "Go To" to move your mouse to that position
- The status label will show success or error messages

## Note
This application requires permission to control your mouse.
