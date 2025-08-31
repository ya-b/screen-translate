import logging
import logging.config
import signal
import sys

import yaml

from screen_translator.config import get_config
from screen_translator.screen_translator import ScreenTranslator
from screen_translator.translator.baidu_translator import BaiduTranslator
from screen_translator.translator.google_translator import GoogleTranslator
from screen_translator.translator.local_translator import LocalTranslator
from screen_translator.translator.no_translator import NoTranslator


log = logging.getLogger(__name__)


def logging_init():
    try:
        with open("logging.yaml", "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        log.info("Logging configuration restored after PaddleOCR initialization")
    except Exception as e:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)s] %(levelname)s %(name)s - [%(module)s,%(funcName)s,%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        log.info(f"Used basic logging config due to error: {e}")


def setup_signal_handlers(translator):
    def signal_handler(signum, frame):
        log.info(f"\nReceived signal {signum}, stopping translator...")
        translator.exit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def create_translator_with_config():
    config = get_config()

    translator = ScreenTranslator(config.source_languages, config.target_language, config.capture_interval)

    translator.set_min_text_length(config.min_text_length)

    translator.ocr_engine.set_confidence_threshold(config.min_confidence)
    translator.ocr_engine.set_min_text_size(config.min_text_size)

    translator.translator.set_cache_enabled(config.translation_cache_enabled)
    if config.translator.type == 'baidu' and config.translator.baidu:
        translator.add_translator(BaiduTranslator(config.translator.baidu.baidu_app_id, config.translator.baidu.baidu_secret_key))
    elif config.translator.type == 'google':
        translator.add_translator(GoogleTranslator())
    elif config.translator.type == 'local':
        translator.add_translator(LocalTranslator())
    else:
        translator.add_translator(NoTranslator())
    return translator


def print_usage():
    log.info("=== Real-time Screen Translator ===")
    log.info(
        "Function: Real-time screen capture, recognize foreign text and translate to Chinese"
    )

    log.info("Usage:")
    log.info("  python main.py              - Start translator")
    log.info("  python main.py --config     - Show current configuration")
    log.info("  python main.py --test       - Run test mode")

    log.info("Controls:")
    log.info("  Ctrl+C                      - Stop translator")

    log.info("Config file: config.yaml")
    log.info("Supported languages: English(en), Japanese(ja), Korean(ko)")


def main():
    logging_init()
    print_usage()
    try:
        translator = create_translator_with_config()

        setup_signal_handlers(translator)

        log.info("Starting translator...")
        log.info("Tip: Make sure game or application window is visible")
        log.info("Press Ctrl+C to stop translation")
        log.info("-" * 50)

        translator.exec()

    except KeyboardInterrupt:
        log.info("\nUser interrupted...")
    except Exception as e:
        log.info(f"Program error: {e}", exc_info=True)
    finally:
        if "translator" in locals():
            translator.exit()

        log.info("Program exited")


if __name__ == "__main__":
    main()
