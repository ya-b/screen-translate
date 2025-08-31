import hashlib
import logging
from typing import List, Optional

from transformers import MarianMTModel, MarianTokenizer
from screen_translator.translator.translator import TranslatorBase

log = logging.getLogger(__name__)


class NoTranslator(TranslatorBase):

    def translate(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        return f"[translate]{text}"

    def translate_batch(self, texts: List[str], target_lang: str = 'zh') -> List[Optional[str]]:
        return [f"[translate]{x}" for x in texts]