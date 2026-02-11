import json
from pathlib import Path

from app_dir import get_base_dir

SETTINGS_FILE = "settings.json"
DEFAULTS = {
    "copy_to_clipboard": True,
    "always_on_top": False,
    "sms_subject": "SMS",
}


def _path() -> Path:
    return get_base_dir() / SETTINGS_FILE


def load_settings() -> dict:
    p = _path()
    if not p.exists():
        return DEFAULTS.copy()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = DEFAULTS.copy()
        out.update({k: v for k, v in data.items() if k in out})
        return out
    except Exception:
        return DEFAULTS.copy()


def save_settings(data: dict) -> None:
    with open(_path(), "w", encoding="utf-8") as f:
        json.dump({k: data.get(k, v) for k, v in DEFAULTS.items()}, f, ensure_ascii=False, indent=2)
