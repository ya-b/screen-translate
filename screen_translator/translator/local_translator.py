import hashlib
import logging
from typing import List, Optional

from transformers import MarianMTModel, MarianTokenizer
from screen_translator.translator.translator import TranslatorBase

log = logging.getLogger(__name__)



class LocalTranslator(TranslatorBase):

    model_name = "Helsinki-NLP/opus-mt-en-zh"

    def __init__(self):
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self.model = MarianMTModel.from_pretrained(self.model_name)
        log.info(f"{self.model_name} model loaded.")

    def translate(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        return self.translate_batch([text], target_lang)[0]

    def translate_batch(self, texts: List[str], target_lang: str = 'zh') -> List[Optional[str]]:
        batch = self.tokenizer(texts, return_tensors="pt", padding=True)
        gen = self.model.generate(**batch)
        translated = [self.tokenizer.decode(t, skip_special_tokens=True) for t in gen]
        return translated