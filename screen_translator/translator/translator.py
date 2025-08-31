import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import httpx

log = logging.getLogger(__name__)


class TranslatorBase(ABC):

    @abstractmethod
    def translate(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        pass

    @abstractmethod
    def translate_batch(self, texts: List[str], target_lang: str = 'zh') -> List[Optional[str]]:
        pass




class TranslatorManager:

    def __init__(self):
        self.translators: List[TranslatorBase] = []
        self.current_translator_index = 0

        self.translation_cache: Dict[str, str] = {}
        self.cache_enabled = True

    def add_translator(self, translator: TranslatorBase):
        self.translators.append(translator)

    def set_cache_enabled(self, enabled: bool):
        self.cache_enabled = enabled

    def clear_cache(self):
        self.translation_cache.clear()

    def translate(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        if not text.strip():
            return None

        cache_key = f"{text}_{target_lang}"
        if self.cache_enabled and cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        for i in range(len(self.translators)):
            translator_index = (self.current_translator_index + i) % len(self.translators)
            translator = self.translators[translator_index]

            try:
                result = translator.translate(text, target_lang)
                if result:
                    self.current_translator_index = translator_index

                    if self.cache_enabled:
                        self.translation_cache[cache_key] = result

                    return result
            except Exception as e:
                log.info(f"Translator {translator.__class__.__name__} failed: {e}")
                continue

        return None

    def translate_batch(self, texts: List[str], target_lang: str = 'zh') -> List[Optional[str]]:
        results = []
        for text in texts:
            result = self.translate(text, target_lang)
            results.append(result)
        return results


def create_default_translator() -> TranslatorManager:
    manager = TranslatorManager()
    return manager

