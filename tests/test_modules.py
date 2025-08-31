import sys
import time
from typing import List
import logging

log = logging.getLogger(__name__)

def test_screen_capture():
    log.info("=== Testing Screen Capture Module ===")
    try:
        from screen_translator.screen_capture import ScreenCapture

        capture = ScreenCapture()
        width, height = capture.get_screen_size()
        log.info(f"✓ Screen size: {width}x{height}")

        screenshot = capture.capture_screen()
        if screenshot is not None:
            log.info(f"✓ Screenshot successful, image size: {screenshot.shape}")
            return True
        else:
            log.info("✗ Screenshot failed")
            return False

    except Exception as e:
        log.info(f"✗ Screen capture module test failed: {e}")
        return False


def test_ocr_engine():
    log.info("\n=== Testing OCR Engine ===")
    try:
        from screen_translator.ocr_engine import OCREngine

        log.info("Initializing OCR engine...")
        ocr_engine = OCREngine(lang=['ch'])

        if ocr_engine.ocr is not None:
            log.info("✓ OCR engine initialized successfully")
        else:
            log.info("✗ OCR engine initialization failed")

        from screen_translator.screen_capture import ScreenCapture

        capture = ScreenCapture()
        screenshot = capture.capture_screen()
        if screenshot is not None:
            texts = ocr_engine.recognize_text_with_filter(screenshot, ["en"])
            log.info(texts)
        return True
    except Exception as e:
        log.info(f"✗ OCR engine test failed: {e}")
        return False


def test_translator():
    log.info("\n=== Testing Translation Module ===")
    try:
        from screen_translator.translator.translator import create_default_translator

        translator = create_default_translator()

        test_texts = ["Hello", "World", "Game"]
        log.info("Testing translation:")

        success_count = 0
        for text in test_texts:
            result = translator.translate(text)
            if result:
                log.info(f"  '{text}' -> '{result}'")
                success_count += 1
            else:
                log.info(f"  '{text}' -> Translation failed")

        if success_count > 0:
            log.info(f"✓ Translation test successful ({success_count}/{len(test_texts)})")
            return True
        else:
            log.info("✗ All translations failed")
            return False

    except Exception as e:
        log.info(f"✗ Translation module test failed: {e}")
        return False


def test_display_manager():
    log.info("\n=== Testing Display Manager ===")
    try:
        from screen_translator.overlay_display import DisplayManager

        display_manager = DisplayManager()
        log.info("✓ Display manager created successfully")
        display_manager.initialize()

        display_manager.show_translations([("Hello", "你好", 0, 0, 1920, 1080)])
        display_manager.process_events()

        display_manager.quit()
        return True

    except Exception as e:
        log.info(f"✗ Display manager test failed: {e}")
        return False

