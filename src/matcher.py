"""
Image matching functionality using OpenCV for improved performance and accuracy.
"""
import cv2
import numpy as np
import pyautogui
from typing import List, Tuple, Optional
from config import (
    IMAGE_PATH, CONFIDENCE, USE_GRAYSCALE,
    DOWNSCALE_FACTOR
)

def match_template_at_scales(
    screenshot: np.ndarray,
    template: np.ndarray,
    scales: List[float] = [0.8, 1.0, 1.2]
) -> List[Tuple[int, int, int, int]]:
    """Perform multi-scale template matching.

    Args:
        screenshot: The screenshot to search in
        template: The template to search for
        scales: List of scales to try

    Returns:
        List of (x, y, w, h) tuples for each match
    """
    matches = []
    for scale in scales:
        scaled_template = cv2.resize(template, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= CONFIDENCE)
        for pt in zip(*locations[::-1]):
            matches.append((int(pt[0] / scale), int(pt[1] / scale),
                          int(scaled_template.shape[1] / scale),
                          int(scaled_template.shape[0] / scale)))
    return matches

def find_icon(region: Optional[Tuple[int, int, int, int]] = None) -> List[Tuple[int, int, int, int]]:
    """Find all instances of the bookmark icon in the specified region.

    Args:
        region: Optional (x, y, width, height) tuple to search within

    Returns:
        List of (x, y, width, height) tuples for each match found
    """
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = np.array(screenshot)

        # Load template
        if USE_GRAYSCALE:
            screenshot_cv = cv2.cvtColor(screenshot_cv, cv2.COLOR_RGB2GRAY)
            template = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
        else:
            template = cv2.imread(IMAGE_PATH, cv2.IMREAD_COLOR)

        if template is None:
            raise ValueError(f"Failed to load template image from {IMAGE_PATH}")

        # Apply downscaling if configured
        if DOWNSCALE_FACTOR < 1.0:
            h, w = screenshot_cv.shape[:2]
            new_h = int(h * DOWNSCALE_FACTOR)
            new_w = int(w * DOWNSCALE_FACTOR)
            screenshot_cv = cv2.resize(screenshot_cv, (new_w, new_h))
            template = cv2.resize(template, (0, 0),
                                fx=DOWNSCALE_FACTOR,
                                fy=DOWNSCALE_FACTOR)

        # Perform multi-scale matching
        return match_template_at_scales(screenshot_cv, template)

    except Exception as e:
        print(f"Error finding icon: {e}")
        return []
