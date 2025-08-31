import logging
import time
from typing import Dict, List, Tuple

from PyQt6.QtCore import QThread, pyqtSignal

from screen_translator.ocr_engine import OCREngine, TextBox
from screen_translator.overlay_display import DisplayManager
from screen_translator.screen_capture import ContinuousCapture
from screen_translator.translator.translator import create_default_translator

log = logging.getLogger(__name__)


class ScreenTranslator(QThread):

    update_signal = pyqtSignal(object)

    def __init__(self, source_languages: List[str], target_language: str, capture_interval: float = 2.0):
        super().__init__()
        self.source_languages = source_languages
        self.target_language = target_language
        self.screen_capture = ContinuousCapture(capture_interval)
        self.ocr_engine = OCREngine(lang=source_languages)
        self.translator = create_default_translator()
        self.display_manager = DisplayManager()

        self.is_running = False
        self.translation_thread = None

        self.min_text_length = 2
        self.show_original = True

        self.stats = {
            'total_captures': 0,
            'total_texts': 0,
            'total_translations': 0,
            'avg_process_time': 0.0
        }

        log.info("Screen translator initialized successfully")

    def set_capture_interval(self, interval: float):
        self.screen_capture.set_interval(interval)


    def set_min_text_length(self, length: int):
        self.min_text_length = length

    def add_translator(self, translator):
        self.translator.add_translator(translator)

    def process_frame(self) -> bool:
        start_time = time.time()

        try:
            screenshot = self.screen_capture.get_latest_screenshot()
            if screenshot is None:
                return False

            self.stats['total_captures'] += 1

            text_boxes = self.ocr_engine.recognize_text_with_filter(
                screenshot, self.source_languages
            )

            if not text_boxes:
                return True

            filtered_texts = self._filter_texts(text_boxes)
            if not filtered_texts:
                return True

            self.stats['total_texts'] += len(filtered_texts)

            translations = self._translate_texts(filtered_texts)

            if translations:
                self.update_signal.emit(translations)
                self.stats['total_translations'] += len(translations)

            process_time = time.time() - start_time
            self.stats['avg_process_time'] = (
                self.stats['avg_process_time'] * 0.9 + process_time * 0.1
            )

            return True

        except Exception as e:
            log.info(f"Error processing frame: {e}")
            return False

    def _filter_texts(self, text_boxes: List[TextBox]) -> List[TextBox]:
        filtered = []

        for text_box in text_boxes:
            text = text_box.text.strip()

            if len(text) < self.min_text_length:
                continue

            if text.isdigit():
                continue

            if all(not c.isalnum() for c in text):
                continue

            filtered.append(text_box)

        return filtered

    def _translate_texts(self, text_boxes: List[TextBox]) -> List[Tuple[str, str, int, int, int, int]]:
        translations = []
        
        translated_texts = self.translator.translate_batch([x.text for x in text_boxes], 'zh')

        for idx, text_box in enumerate(text_boxes):
            original_text = text_box.text

            translated_text = translated_texts[idx]

            if translated_text and translated_text != original_text:
                x, y, width, height = text_box.get_rect()

                translations.append((
                    original_text,
                    translated_text,
                    x, y, width, height
                ))
        return translations

    def _display_translations(self, translations):
        try:
            self.display_manager.show_translations(translations)
            self.display_manager.process_events()
        except Exception as e:
            log.info(f"Error displaying translations: {e}")

    def run(self):
        log.info("Translation loop started")

        while self.is_running:
            try:
                success = self.process_frame()
                if not success:
                    time.sleep(0.1)

                time.sleep(0.05)

            except Exception as e:
                log.info(f"Translation loop error: {e}")
                time.sleep(1)

        log.info("Translation loop ended")

    def exec(self):
        if self.is_running:
            log.info("Translator is already running")
            return

        log.info("Starting real-time screen translation...")

        self.display_manager.initialize()

        self.screen_capture.start_capture()

        self.update_signal.connect(self._display_translations)

        self.is_running = True

        self.start()
        log.info("Real-time translation started")
        log.info("Press Ctrl+C to stop translation")
        self.display_manager.exec()

    def exit(self):
        if not self.is_running:
            return

        log.info("Stopping real-time translation...")

        self.is_running = False

        self.screen_capture.stop_capture()

        if self.translation_thread and self.translation_thread.is_alive():
            self.translation_thread.join(timeout=2)

        self.display_manager.clear_display()

        log.info("Real-time translation stopped")

    def get_stats(self) -> Dict:
        return self.stats.copy()

    def print_stats(self):
        stats = self.get_stats()
        log.info(f"\n=== Performance Statistics ===")
        log.info(f"Total captures: {stats['total_captures']}")
        log.info(f"Recognized texts: {stats['total_texts']}")
        log.info(f"Translated texts: {stats['total_translations']}")
        log.info(f"Average processing time: {stats['avg_process_time']:.3f}s")
