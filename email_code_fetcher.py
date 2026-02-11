import re
from imap_tools import MailBox, AND
import time

CODE_REGEX = re.compile(r"\d{4}")
# Формат темы письма с кодом: "4 цифры, пробел, тире" (напр. "5787 — ..." или "2727 - ...")
SUBJECT_CODE_FORMAT = re.compile(r"\d{4}\s+[—\-]")
# При передаче subject_contains (кортеж) включается режим платформы: фильтр по формату темы, без фильтра по To
PLATFORM_OTP_SUBJECT_MARKERS = ()
# В теле SMS-писем: код в теле, тема = номер телефона. Фильтр по телу, чтобы не брать левые цифры.
SMS_BODY_MARKER = "одноразовый код для подтверждения номера телефона на Платформе"
WAIT_TIMEOUT = 20  # Максимальное время ожидания кода (секунд)

DEBUG_EMAIL_FETCH = False

# Размер порции при обходе папки (ищем по всем непрочитанным, от новых к старым)
EMAIL_FETCH_CHUNK = 20


def get_auth_code_from_email(
    recipient_email: str,
    folder: str,
    imap_user: str,
    imap_password: str,
    imap_host: str,
    imap_port: int = 993,
    subject_contains: str | tuple[str, ...] | None = None,
) -> str | None:
    """
    Ищет последнее (самое свежее) непрочитанное письмо в папке folder.
    Обходит все непрочитанные от новых к старым, пока не найдёт письмо с кодом или не проверит всю папку.
    Если задан subject_contains (любое не-None) — учитываются только письма, тема которых в формате «4 цифры, пробел, тире» (напр. «5787 — ...»).

    :param subject_contains: если не None — режим платформы: фильтр по формату темы, без фильтра по To
    :return: строка с 4-значным кодом, либо None если не найден во всей папке
    """
    if DEBUG_EMAIL_FETCH:
        print("[DEBUG get_auth_code_from_email] Параметры:")
        print(f"  recipient_email={recipient_email!r}, folder={folder!r}")
        print(f"  imap_host={imap_host}, imap_port={imap_port}")
        print(f"  subject_contains={subject_contains!r}")
    try:
        with MailBox(imap_host, port=imap_port).login(imap_user, imap_password) as mailbox:
            mailbox.folder.set(folder)
            filter_by_to = subject_contains is None
            # В режиме платформы (subject_contains не None) — фильтр по формату "4 цифры, пробел, тире"
            _subject_ok = lambda s: SUBJECT_CODE_FORMAT.search(s) if subject_contains is not None else True
            criteria = AND(seen=False) if not filter_by_to else AND(to=recipient_email, seen=False)
            start = 0
            msg_idx = 0
            while True:
                messages = list(
                    mailbox.fetch(
                        criteria,
                        reverse=True,
                        limit=slice(start, start + EMAIL_FETCH_CHUNK),
                        mark_seen=False,
                    )
                )
                if not messages:
                    break
                if DEBUG_EMAIL_FETCH:
                    print(f"[DEBUG] Папка {folder!r}, порция {start}..{start + len(messages)}, всего писем в порции: {len(messages)}")
                for msg in messages:
                    msg_idx += 1
                    subj = msg.subject or ""
                    if DEBUG_EMAIL_FETCH:
                        print(f"  Письмо {msg_idx}: subject={subj!r}, date={msg.date}")
                    if subject_contains is not None and not _subject_ok(subj):
                        if DEBUG_EMAIL_FETCH:
                            print(f"    -> пропуск: тема не в формате «4 цифры, пробел, тире»")
                        continue
                    match = CODE_REGEX.search(msg.subject or "")
                    if not match:
                        match = CODE_REGEX.search(msg.text or "")
                    if match:
                        if DEBUG_EMAIL_FETCH:
                            print(f"    -> код найден: {match.group(0)!r}")
                        return match.group(0)
                    if DEBUG_EMAIL_FETCH:
                        print(f"    -> тема подходит, но 4-значный код в теме/теле не найден")
                start += EMAIL_FETCH_CHUNK
    except Exception as e:
        if DEBUG_EMAIL_FETCH:
            print(f"[DEBUG] Ошибка: {type(e).__name__}: {e}")
    if DEBUG_EMAIL_FETCH:
        print("[DEBUG] Вся папка проверена, код не найден")
    return None


def get_auth_code_from_sms(
    imap_user: str,
    imap_password: str,
    imap_host: str,
    imap_port: int = 993,
    folder: str = "sms",
    body_contains: str | None = None,
) -> str | None:
    """
    Ищет последнее (самое свежее) непрочитанное письмо в папке folder (по умолчанию «sms»).
    Тема письма = номер телефона, код берётся только из тела письма.
    Если задан body_contains — учитываются только письма, в теле которых есть эта подстрока.

    :param imap_user: логин IMAP (корпоративная почта)
    :param imap_password: пароль IMAP
    :param imap_host: хост IMAP
    :param imap_port: порт IMAP (по умолчанию 993)
    :param folder: папка для поиска (по умолчанию "sms")
    :param body_contains: если задано — только письма с этой подстрокой в теле (например SMS_BODY_MARKER)
    :return: строка с 4-значным кодом, либо None если не найден
    """
    body_marker = body_contains or SMS_BODY_MARKER
    try:
        with MailBox(imap_host, port=imap_port).login(imap_user, imap_password) as mailbox:
            mailbox.folder.set(folder)
            criteria = AND(seen=False)
            start = 0
            while True:
                messages = list(
                    mailbox.fetch(
                        criteria,
                        reverse=True,
                        limit=slice(start, start + EMAIL_FETCH_CHUNK),
                        mark_seen=False,
                    )
                )
                if not messages:
                    break
                for msg in messages:
                    body = msg.text or ""
                    if body_marker and body_marker not in body:
                        continue
                    match = CODE_REGEX.search(body)
                    if match:
                        return match.group(0)
                start += EMAIL_FETCH_CHUNK
    except Exception:
        pass
    return None
