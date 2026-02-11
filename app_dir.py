"""Базовая директория приложения: рядом с .exe при сборке PyInstaller, иначе — каталог пакета."""
import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent
