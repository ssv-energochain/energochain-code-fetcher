import configparser
from pathlib import Path
from typing import NamedTuple

from app_dir import get_base_dir

CONFIG_NAME = "config.ini"
DEFAULT_HOST = "imap.yandex.ru"
DEFAULT_PORT = 993


class PersonalConfig(NamedTuple):
    email: str
    password: str
    folder: str


class CorporateConfig(NamedTuple):
    email: str
    password: str


def _path() -> Path:
    return get_base_dir() / CONFIG_NAME


def _section(cfg: configparser.ConfigParser, name: str) -> dict:
    return dict(cfg[name]) if cfg.has_section(name) else {}


def load_imap_config() -> tuple[str, int, PersonalConfig, CorporateConfig, dict]:
    """
    Читает config.ini.
    Возвращает (host, port, personal_config, corporate_config, ui_dict).
    ui_dict: copy_to_clipboard (bool), always_on_top (bool).
    """
    path = _path()
    if not path.exists():
        return (
            DEFAULT_HOST,
            DEFAULT_PORT,
            PersonalConfig("", "", "INBOX"),
            CorporateConfig("", ""),
            {"copy_to_clipboard": True, "always_on_top": False},
        )
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")
    imap = _section(cfg, "imap")
    personal = _section(cfg, "personal")
    corporate = _section(cfg, "corporate")
    ui = _section(cfg, "ui")

    host = imap.get("host", DEFAULT_HOST).strip()
    try:
        port = int(imap.get("port", str(DEFAULT_PORT)).strip())
    except ValueError:
        port = DEFAULT_PORT

    personal_config = PersonalConfig(
        email=personal.get("email", "").strip(),
        password=personal.get("password", "").strip(),
        folder=(personal.get("folder", "INBOX").strip() or "INBOX"),
    )
    corporate_config = CorporateConfig(
        email=corporate.get("email", "").strip(),
        password=corporate.get("password", "").strip(),
    )
    ui_dict = {
        "copy_to_clipboard": ui.get("copy_to_clipboard", "true").strip().lower() in ("1", "true", "yes"),
        "always_on_top": ui.get("always_on_top", "false").strip().lower() in ("1", "true", "yes"),
    }
    return host, port, personal_config, corporate_config, ui_dict


def save_config(
    host: str,
    port: int,
    personal: PersonalConfig,
    corporate: CorporateConfig,
    copy_to_clipboard: bool,
    always_on_top: bool,
) -> None:
    """Перезаписывает config.ini новыми данными."""
    cfg = configparser.ConfigParser()
    cfg["imap"] = {"host": host, "port": str(port)}
    cfg["personal"] = {
        "email": personal.email,
        "password": personal.password,
        "folder": personal.folder,
    }
    cfg["corporate"] = {
        "email": corporate.email,
        "password": corporate.password,
    }
    cfg["ui"] = {
        "copy_to_clipboard": "true" if copy_to_clipboard else "false",
        "always_on_top": "true" if always_on_top else "false",
    }
    with open(_path(), "w", encoding="utf-8") as f:
        cfg.write(f)
