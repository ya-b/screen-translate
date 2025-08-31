import logging
import os
import yaml
from dataclasses import asdict, dataclass
from typing import Optional

log = logging.getLogger(__name__)

from typing import List, Optional
from pydantic import BaseModel, Field


class BaiduConfig(BaseModel):
    baidu_app_id: str
    baidu_secret_key: str


class LocalConfig(BaseModel):
    model: str


class TranslatorConfig(BaseModel):
    type: str = Field(..., description="翻译器类型: google, baidu, local")
    baidu: Optional[BaiduConfig] = None
    local: Optional[LocalConfig] = None


class AppConfig(BaseModel):
    # 翻译器
    translator: TranslatorConfig

    # 截图设置
    capture_interval: float = 2.0
    capture_region: Optional[List[int]] = None

    # OCR 设置
    ocr_language: str = "ch"
    min_confidence: float = 0.5
    min_text_size: int = 10
    min_text_length: int = 2

    # 翻译设置
    source_languages: List[str] = ["en"]
    target_language: str = "ch"
    translation_cache_enabled: bool = True

    # 显示设置
    show_original: bool = True
    display_duration: int = 5000
    font_size: int = 12
    background_opacity: int = 180

    # 性能设置
    max_concurrent_translations: int = 5
    enable_gpu_acceleration: bool = False


def get_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)