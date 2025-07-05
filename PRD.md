# Bookmark Clicker PRD

---

## 1. Purpose & Scope

* **Objective:** Automate detection and sequential clicking of every on-screen instance of an unchanged bookmark icon on macOS.
* **Scope:**

  * Python application with both CLI and UI interfaces
  * Global hotkey toggle (start/stop)
  * Static region handling (initial browser-window bounds only)
  * Fast, single-stage template matching
  * Modular architecture with separate components

*Note: Dynamic trimming, secondary edge-pattern checks, and the reset-counter hotkey are deferred to future iterations.*

---

## 2. Success Metrics

| Metric                 | Target                                   | Measurement Method                                   |
| ---------------------- | ---------------------------------------- | ---------------------------------------------------- |
| Detection Accuracy     | ≥ 95% true positives                     | Test suite on 1,000 labeled frames                   |
| False-Positive Rate    | ≤ 2%                                     | Same test suite                                      |
| Full-Cycle Time        | ≤ 300 ms per iteration                   | Profiling on Mac Mini M1 with downscale factor = 30% |
| Stability              | ≥ 8 hours continuous run                 | Long-run logging                                     |
| Hotkey Stop Latency    | ≤ 0.5 s from key-down to loop-pause flag | Measured over 100 toggles                            |
| Watchdog Stop Accuracy | Always respects user-defined click limit | Unit tests                                           |

---

## 3. User Stories

1. **Static Region Detection**
   *As a user*, I want the script to detect my browser window at launch and search that fixed region.
2. **High-Speed Matching**
   *As a user*, I expect fast detection via downscaling to exactly 30% and OpenCV's template matching at confidence ≥ 0.90.
3. **Configurable Delays & Limits**
   *As a user*, I want to set per-click delay, scan delay, and a maximum click count (`watchdog_limit`).
4. **Emergency Pause**
   *As a user*, I need ⌘+⇧+S to pause/resume the loop (≤ 0.5 s latency).
5. **User Interface Options**
   *As a user*, I want both a command-line interface and a graphical interface to control the application.

---

## 4. Functional Requirements

### 4.1 Core Automation Loop

* **Config Inputs:**

  * `image_path`
  * `confidence` (locked to 0.90)
  * `click_delay` (default 0.5 s)
  * `scan_delay` (default 1.0 s)
  * `watchdog_limit`

* **Behavior:**

  1. **Region Determination:**

     * At launch: run AppleScript to fetch the active browser window’s bounds into `region`.
  2. **Capture & Downscale:**

     * Screenshot `region`, downscale to **30%** via `cv2.resize`.
  3. **Fast Matching:**

     * Run `cv2.matchTemplate` → find all locations with match ≥ **0.90**.
     * Map matches back to full resolution.
  4. **Click & Count:**

     * Click each unique match center via `pyautogui.click`.
     * Increment counter; if ≥ `watchdog_limit`, auto-stop and log.
  5. **Iteration Delay:**

     * Wait `scan_delay` before next cycle.

### 4.2 Control Interface

* **Hotkeys:**

  * ⌘+⇧+S → Toggle pause/resume (latency ≤ 0.5 s measured as time from key-down to loop-pause flag set)
  * ⌘+⇧+Q → Exit application

* **User Interface:**

  * Command-line interface with headless mode
  * Optional graphical user interface for easier control

---

## 5. Non-Functional Requirements

| Attribute           | Requirement                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| **Performance**     | Full cycle ≤ 300 ms on Mac Mini M1 with downscale = 30%                 |
| **Reliability**     | MTBF ≥ 8 hours; watchdog always honored                                 |
| **Maintainability** | Modular: region detector, capture/downscale, matcher, clicker, controls |
| **Portability**     | macOS 12+; Python 3.10+                                                 |
| **Security**        | Local-only processing; no network I/O                                   |
| **Privacy**         | No persistent screenshots; logs contain no PII                          |

---

## 6. Technical Approach

| Component            | Technology / Library            | Notes                                  |
| -------------------- | ------------------------------- | -------------------------------------- |
| **Region Detection** | AppleScript via `subprocess`    | Fetch browser-window bounds at startup |
| **Downscale**        | `cv2.resize`                    | Fixed scale = 30%                      |
| **Template Match**   | `cv2.matchTemplate` or PyAutoGUI | Primary: OpenCV with confidence threshold = 0.90<br>Alternative: PyAutoGUI's locateOnScreen |
| **Clicking**         | `pyautogui.click`               | Center-of-match click                  |
| **Hotkeys**          | `pynput.keyboard.GlobalHotKeys` | ⌘+⇧+S pause/resume; ⌘+⇧+Q exit; latency ≤ 0.5 s |
| **Logging**          | Python `logging`                | Console + rotating file handler        |
| **UI**               | Native Python UI libraries      | Optional graphical interface          |

---

## 7. Permissions & Setup

1. **Accessibility Access:**

   * Enable Terminal/Python under System Preferences → Security & Privacy → Accessibility.
2. **Environment:**

   ```bash
   pip install -r requirements.txt
   ```

   Requirements include:
   * pyautogui
   * opencv-python
   * pillow
   * pynput
   * PyInstaller (for creating standalone executables)

---

## 8. Risks & Mitigations

| Risk                          | Mitigation                               |
| ----------------------------- | ---------------------------------------- |
| **Pipeline Overhead**         | Downscale to 30% + single-stage matching |
| **Region Detection Failures** | Fallback to on-demand click-and-drag ROI |
| **Hotkey Latency Spikes**     | Measure latency; log anomalies > 0.5 s   |

---

## 9. Implementation Architecture

1. **Project Structure:**
   * Standalone script (`bookmark_clicker.py`) for quick deployment
   * Modular package structure in `src/` directory:
     * `__main__.py`: Entry point with CLI and UI options
     * `matcher.py`: Image matching functionality
     * `clicker.py`: Click automation logic
     * `hotkey.py`: Hotkey management
     * `ui.py`: User interface components

2. **Execution Options:**
   * Run as standalone script: `python bookmark_clicker.py`
   * Run as package: `python -m src`
   * Run in headless mode: `python -m src --headless`

---

*All deferred to phase 2: dynamic trimming, secondary edge-pattern checks, reset-counter hotkey.*
