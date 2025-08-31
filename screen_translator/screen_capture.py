import logging
import time
from typing import Optional, Tuple

import cv2
import numpy as np
import pyautogui
from PIL import Image

log = logging.getLogger(__name__)


class ScreenCapture:

    def __init__(self):
        pyautogui.FAILSAFE = False

        self.screen_width, self.screen_height = pyautogui.size()

        self.capture_region = None

    def set_capture_region(self, x: int, y: int, width: int, height: int):
        self.capture_region = (x, y, width, height)

    def capture_screen(self) -> Optional[np.ndarray]:
        try:
            if self.capture_region:
                screenshot = pyautogui.screenshot(region=self.capture_region)
            else:
                screenshot = pyautogui.screenshot()

            img_array = np.array(screenshot)

            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            return img_bgr

        except Exception as e:
            log.info(f"Screenshot failed: {e}")
            return None

    def capture_screen_pil(self) -> Optional[Image.Image]:
        try:
            if self.capture_region:
                screenshot = pyautogui.screenshot(region=self.capture_region)
            else:
                screenshot = pyautogui.screenshot()

            return screenshot

        except Exception as e:
            log.info(f"Screenshot failed: {e}")
            return None

    def save_screenshot(self, filename: str) -> bool:
        try:
            screenshot = self.capture_screen_pil()
            if screenshot:
                screenshot.save(filename)
                return True
            return False

        except Exception as e:
            log.info(f"Failed to save screenshot: {e}")
            return False

    def get_screen_size(self) -> Tuple[int, int]:
        return self.screen_width, self.screen_height


class ContinuousCapture:

    def __init__(self, capture_interval: float = 1.0):
        self.screen_capture = ScreenCapture()
        self.capture_interval = capture_interval
        self.is_running = False
        self.last_capture_time = 0

    def set_interval(self, interval: float):
        self.capture_interval = interval

    def should_capture(self) -> bool:
        current_time = time.time()
        if current_time - self.last_capture_time >= self.capture_interval:
            self.last_capture_time = current_time
            return True
        return False

    def start_capture(self):
        self.is_running = True

    def stop_capture(self):
        self.is_running = False

    def get_latest_screenshot(self) -> Optional[np.ndarray]:
        if not self.is_running:
            return None

        if self.should_capture():
            return self.screen_capture.capture_screen()

        return None
