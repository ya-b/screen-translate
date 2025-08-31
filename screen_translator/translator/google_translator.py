import logging
import time
from typing import List, Optional

import httpx
from screen_translator.translator.translator import TranslatorBase, create_default_translator

log = logging.getLogger(__name__)

class GoogleTranslator(TranslatorBase):

    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"

    def translate(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        if not text.strip():
            return None

        try:
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': target_lang,
                'dt': 't',
                'q': text
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params, headers=headers)

                if response.status_code == 200:
                    result = response.json()

                    if result and result[0]:
                        translated_text = ''.join([item[0] for item in result[0] if item[0]])
                        return translated_text
                    else:
                        return None
                else:
                    log.info(f"Google translation request failed: {response.status_code}")
                    return None

        except Exception as e:
            log.info(f"Google translation exception: {e}")
            return None

    def translate_batch(self, texts: List[str], target_lang: str = 'zh') -> List[Optional[str]]:
        results = []
        for text in texts:
            result = self.translate(text, target_lang)
            results.append(result)
            time.sleep(0.1)
        return results
