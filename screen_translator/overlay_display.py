import logging
import sys
from typing import List, Tuple

from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

log = logging.getLogger(__name__)


class TranslationLabel(QLabel):

    def __init__(
        self,
        original_text: str,
        translated_text: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ):
        super().__init__()

        self.original_text = original_text
        self.translated_text = translated_text
        self.original_rect = QRect(x, y, width, height)

        self.setText(translated_text)

        self.setStyleSheet(
            """
            QLabel {
                color: green;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
        """
        )

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)

        self.adjustSize()

        self.move(x, y + height + 5)

        self.setToolTip(f"Original: {original_text}")

        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.fade_out)
        self.opacity = 1.0

    def start_fade_timer(self, delay_ms: int = 5000):
        self.fade_timer.start(delay_ms)

    def fade_out(self):
        self.opacity -= 0.1
        if self.opacity <= 0:
            self.hide()
            self.fade_timer.stop()
        else:
            self.setWindowOpacity(self.opacity)


class OverlayWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.translation_labels: List[TranslationLabel] = []
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.showFullScreen()

    def add_translation(
        self,
        original_text: str,
        translated_text: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ):
        label = TranslationLabel(original_text, translated_text, x, y, width, height)
        label.setParent(self)
        label.show()

        label.start_fade_timer(5000)

        self.translation_labels.append(label)

    def clear_translations(self):
        for label in self.translation_labels:
            label.hide()
            label.deleteLater()

        self.translation_labels.clear()

    def update_translations(
        self, translations: List[Tuple[str, str, int, int, int, int]]
    ):
        self.clear_translations()

        for original, translated, x, y, w, h in translations:
            self.add_translation(original, translated, x, y, w, h)

    def paintEvent(self, event):
        super().paintEvent(event)


class DisplayManager:

    def __init__(self):
        self.app = None
        self.overlay_window = None
        self.is_initialized = False

    def initialize(self):
        if not self.is_initialized:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()

            self.overlay_window = OverlayWindow()

            self.is_initialized = True

    def show_translations(
        self, translations: List[Tuple[str, str, int, int, int, int]]
    ):
        if not self.is_initialized:
            self.initialize()

        if self.overlay_window:
            self.overlay_window.update_translations(translations)

    def clear_display(self):
        if self.overlay_window:
            self.overlay_window.clear_translations()

    def hide_overlay(self):
        if self.overlay_window:
            self.overlay_window.hide()

    def show_overlay(self):
        if self.overlay_window:
            self.overlay_window.show()

    def process_events(self):
        if self.app:
            self.app.processEvents()

    def exec(self):
        if self.app:
            self.app.exec()

    def quit(self):
        if self.overlay_window:
            self.overlay_window.close()
        if self.app:
            self.app.quit()


class SimpleOverlay(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setGeometry(0, 0, 1920, 1080)

    def show_text(self, text: str, x: int, y: int):
        label = QLabel(text, self)
        label.setStyleSheet(
            """
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: yellow;
                border: 1px solid yellow;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )

        label.adjustSize()
        label.move(x, y)
        label.show()

        QTimer.singleShot(3000, label.deleteLater)
