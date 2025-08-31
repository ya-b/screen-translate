import logging
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from paddleocr import PaddleOCR

log = logging.getLogger(__name__)


class TextBox:

    def __init__(self, text: str, bbox: List[List[int]], confidence: float):
        self.text = text
        self.bbox = bbox
        self.confidence = confidence

        self.center_x, self.center_y = self._calculate_center()
        self.width, self.height = self._calculate_size()

    def _calculate_center(self) -> Tuple[int, int]:
        x_coords = [point[0] for point in self.bbox]
        y_coords = [point[1] for point in self.bbox]

        center_x = int(sum(x_coords) / len(x_coords))
        center_y = int(sum(y_coords) / len(y_coords))

        return center_x, center_y

    def _calculate_size(self) -> Tuple[int, int]:
        x_coords = [point[0] for point in self.bbox]
        y_coords = [point[1] for point in self.bbox]

        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)

        return width, height

    def get_rect(self) -> Tuple[int, int, int, int]:
        x_coords = [point[0] for point in self.bbox]
        y_coords = [point[1] for point in self.bbox]

        x = min(x_coords)
        y = min(y_coords)
        width = max(x_coords) - x
        height = max(y_coords) - y

        return x, y, width, height

    def __str__(self):
        return f"TextBox(text='{self.text}', center=({self.center_x}, {self.center_y}), confidence={self.confidence:.2f})"


class OCREngine:

    def __init__(self, lang=['en']):
        try:
            self.ocr = PaddleOCR()

            from main import logging_init
            logging_init()

            self.min_confidence = 0.5

            self.min_text_size = 10

            log.info(f"OCR engine initialized successfully, language: {lang}")

        except Exception as e:
            log.info(f"OCR engine initialization failed: {e}")
            self.ocr = None

    def set_confidence_threshold(self, threshold: float):
        self.min_confidence = threshold

    def set_min_text_size(self, size: int):
        self.min_text_size = size

    def recognize_text(self, image: np.ndarray) -> List[TextBox]:
        if self.ocr is None:
            log.info("OCR engine not initialized")
            return []

        try:
            results = self.ocr.predict(image)

            text_boxes = []

            for result in results:
                for i in range(len(result["rec_texts"])):
                    bbox = result["rec_polys"][i]
                    text = result["rec_texts"][i]
                    confidence = result["rec_scores"][i]

                    if confidence >= self.min_confidence:
                        text_box = TextBox(text, bbox, confidence)

                        if text_box.width >= self.min_text_size and text_box.height >= self.min_text_size:
                            text_boxes.append(text_box)

            return text_boxes

        except Exception as e:
            log.info(f"Text recognition failed: {e}")
            return []

    def recognize_text_with_filter(self, image: np.ndarray,
                                 target_languages: Optional[List[str]] = None) -> List[TextBox]:
        text_boxes = self.recognize_text(image)

        if not target_languages:
            return text_boxes

        filtered_boxes = []

        for text_box in text_boxes:
            text = text_box.text

            if self._contains_target_language(text, target_languages):
                filtered_boxes.append(text_box)

        return filtered_boxes

    def _contains_target_language(self, text: str, target_languages: List[str]) -> bool:
        for lang in target_languages:
            if lang == 'en':
                if any(ord('a') <= ord(c.lower()) <= ord('z') for c in text):
                    return True
            elif lang == 'ja':
                if any(0x3040 <= ord(c) <= 0x309F or
                      0x30A0 <= ord(c) <= 0x30FF or
                      0x4E00 <= ord(c) <= 0x9FAF
                      for c in text):
                    return True
            elif lang == 'ko':
                if any(0xAC00 <= ord(c) <= 0xD7AF for c in text):
                    return True
            elif lang == 'zh':
                if any(0x4E00 <= ord(c) <= 0x9FAF for c in text):
                    return True

        return False

    def draw_text_boxes(self, image: np.ndarray, text_boxes: List[TextBox]) -> np.ndarray:
        result_image = image.copy()

        for text_box in text_boxes:
            bbox = np.array(text_box.bbox, dtype=np.int32)
            cv2.polylines(result_image, [bbox], True, (0, 255, 0), 2)

            x, y = text_box.bbox[0]
            cv2.putText(result_image, text_box.text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        return result_image
