import hashlib
import logging
import random
import time
from typing import List, Optional

import httpx
from screen_translator.translator.translator import TranslatorBase, create_default_translator

log = logging.getLogger(__name__)

class BaiduTranslator(TranslatorBase):

    def __init__(self, app_id: str, secret_key: str):
        self.app_id = app_id
        self.secret_key = secret_key
        self.base_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def _generate_sign(self, query: str, salt: str) -> str:
        sign_str = self.app_id + query + salt + self.secret_key
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    def translate(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        if not text.strip():
            return None

        try:
            salt = str(random.randint(32768, 65536))
            sign = self._generate_sign(text, salt)

            params = {
                'q': text,
                'from': 'auto',
                'to': target_lang,
                'appid': self.app_id,
                'salt': salt,
                'sign': sign
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)

                if response.status_code == 200:
                    result = response.json()

                    if 'trans_result' in result:
                        return result['trans_result'][0]['dst']
                    else:
                        log.info(f"Baidu translation error: {result}")
                        return None
                else:
                    log.info(f"Baidu translation request failed: {response.status_code}")
                    return None

        except Exception as e:
            log.info(f"Baidu translation exception: {e}")
            return None

    def translate_batch(self, texts: List[str], target_lang: str = 'zh') -> List[Optional[str]]:
        results = []
        for text in texts:
            result = self.translate(text, target_lang)
            results.append(result)
            time.sleep(0.1)
        return results
