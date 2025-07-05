"""
Main entry point for the bookmark clicker application.
"""
import argparse
import sys
import time
from src.clicker import Clicker
from src.hotkey import HotkeyListener
from src.ui import ClickerUI

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Bookmark Clicker")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no UI)"
    )
    args = parser.parse_args()
    
    # Create and start the clicker thread
    clicker = Clicker()
    
    # Set up the hotkey listener
    hotkey_listener = HotkeyListener(clicker)
    hotkey_listener.start()
    
    if args.headless:
        # Headless mode - start clicker immediately
        print("Starting bookmark clicker in headless mode")
        print("Press Cmd+Shift+S to toggle or Ctrl+C to exit")
        clicker.start()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            clicker.stop()
            hotkey_listener.stop()
    else:
        # UI mode
        ui = ClickerUI(clicker)
        ui.run()  # This blocks until the UI is closed
        
        # Clean up when UI exits
        hotkey_listener.stop()

if __name__ == "__main__":
    main()
