#!/usr/bin/env python3
import tkinter as tk
import pyautogui
import threading
import time

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Set up the UI
        self.setup_ui()
        
        # Start tracking mouse position
        self.tracking = True
        self.track_thread = threading.Thread(target=self.track_mouse)
        self.track_thread.daemon = True
        self.track_thread.start()
    
    def setup_ui(self):
        # Current position frame
        position_frame = tk.LabelFrame(self.root, text="Current Mouse Position", padx=10, pady=10)
        position_frame.pack(fill="x", padx=10, pady=10)
        
        self.position_label = tk.Label(position_frame, text="X: 0, Y: 0", font=("Arial", 14))
        self.position_label.pack()
        
        # Go to position frame
        goto_frame = tk.LabelFrame(self.root, text="Go To Position", padx=10, pady=10)
        goto_frame.pack(fill="x", padx=10, pady=10)
        
        # X coordinate input
        x_frame = tk.Frame(goto_frame)
        x_frame.pack(fill="x", pady=5)
        
        tk.Label(x_frame, text="X:").pack(side="left", padx=5)
        self.x_entry = tk.Entry(x_frame)
        self.x_entry.pack(side="left", fill="x", expand=True)
        
        # Y coordinate input
        y_frame = tk.Frame(goto_frame)
        y_frame.pack(fill="x", pady=5)
        
        tk.Label(y_frame, text="Y:").pack(side="left", padx=5)
        self.y_entry = tk.Entry(y_frame)
        self.y_entry.pack(side="left", fill="x", expand=True)
        
        # Go button
        self.go_button = tk.Button(goto_frame, text="Go To", command=self.go_to_position)
        self.go_button.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=5)
    
    def track_mouse(self):
        """Track the mouse position in a separate thread"""
        while self.tracking:
            x, y = pyautogui.position()
            self.position_label.config(text=f"X: {x}, Y: {y}")
            time.sleep(0.1)
    
    def go_to_position(self):
        """Move the mouse to the specified coordinates"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            
            # Get screen size
            screen_width, screen_height = pyautogui.size()
            
            # Check if coordinates are within screen bounds
            if 0 <= x <= screen_width and 0 <= y <= screen_height:
                pyautogui.moveTo(x, y, duration=0.5)
                self.status_label.config(text=f"Mouse moved to X: {x}, Y: {y}", fg="green")
            else:
                self.status_label.config(
                    text=f"Coordinates out of bounds (max: {screen_width}x{screen_height})", 
                    fg="red"
                )
        except ValueError:
            self.status_label.config(text="Please enter valid numbers", fg="red")
    
    def on_closing(self):
        """Clean up before closing"""
        self.tracking = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
