# EnergoChain Code Fetcher

Десктопное приложение для быстрого получения одноразовых кодов из почты (IMAP): личная и корпоративная почта, несколько папок, режим SMS. Код показывается в окне и при необходимости копируется в буфер обмена.

## Возможности

- **Личная почта** — коды из указанной папки (по умолчанию INBOX), фильтр по формату темы «4 цифры — …».
- **Корпоративная почта** — те же коды из папок: uneco, eak, sale, svet1, autotest.
- **SMS** — коды из писем в папке «sms» (тема = номер, код в теле письма).
- Настройки хранятся в `config.ini`, доп. опции UI — в `settings.json`.
- Опции: копирование результата в буфер, окно поверх всех окон.

## Требования

- Python 3.11+ (для запуска из исходников)
- IMAP-доступ к почте (пароль приложения для Яндекса и аналогов)

## Конфигурация

Первый запуск или кнопка **Настройки** в приложении создаёт/редактирует `config.ini` в папке с программой (рядом с exe или с исходниками).

Пример структуры (можно скопировать из `config_example.ini`):

```ini
[imap]
host = imap.yandex.ru
port = 993

[personal]
email = your_personal@example.com
password = your_app_password
folder = INBOX

[corporate]
email = your_corporate@example.com
password = your_app_password

[ui]
copy_to_clipboard = true
always_on_top = false
```

Нужен **пароль приложения**, не основной пароль аккаунта.

## Запуск

### Из исходников (разработка)

1. Клонировать/открыть проект, перейти в каталог проекта.
2. Создать виртуальное окружение (по желанию):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Запустить приложение:
   ```bash
   python app.py
   ```

`config.ini` и `settings.json` будут в каталоге с `app.py`.

### Готовый исполняемый файл

1. Собрать приложение (см. раздел «Сборка» — Windows или Linux).
2. **Windows:** двойной клик по `dist\EnergoChainCodeFetcher.exe` или из консоли:
   ```bash
   dist\EnergoChainCodeFetcher.exe
   ```
3. **Linux:** из терминала:
   ```bash
   ./dist/EnergoChainCodeFetcher
   ```

При первом запуске рядом с исполняемым файлом создаются `config.ini` и `settings.json`.

## Сборка

Сборка одним файлом через PyInstaller. Исполняемый файл получается **под ту ОС, на которой запускается PyInstaller** (кросс-компиляции нет).

### Windows

1. Установить зависимости для сборки и приложения:
   ```bash
   pip install -r requirements-build.txt
   pip install -r requirements.txt
   ```
2. Собрать:
   ```bash
   python -m PyInstaller --noconfirm energochain_fetcher.spec
   ```
   либо запустить скрипт:
   ```bash
   build.bat
   ```

Результат: один файл `dist\EnergoChainCodeFetcher.exe`. Его можно скопировать в любое место; при первом запуске в этой папке появятся `config.ini` и `settings.json`.

### Linux

Сборку нужно выполнять **в Linux** (нативная система, WSL2, Docker и т.п.). Используется тот же `energochain_fetcher.spec`.

1. Установить зависимости системы для tkinter (если ещё не стоят):
   ```bash
   # Debian/Ubuntu
   sudo apt install python3-tk
   # Fedora
   sudo dnf install python3-tkinter
   ```
2. Установить зависимости Python и собрать:
   ```bash
   pip install -r requirements-build.txt -r requirements.txt
   python -m PyInstaller --noconfirm energochain_fetcher.spec
   ```
3. Результат: исполняемый файл `dist/EnergoChainCodeFetcher` (без расширения .exe). Запуск:
   ```bash
   ./dist/EnergoChainCodeFetcher
   ```
   или скопировать `dist/EnergoChainCodeFetcher` в нужную папку и запускать оттуда. Рядом с бинарником при первом запуске создаются `config.ini` и `settings.json`.

## Структура проекта

| Файл / папка | Назначение |
|--------------|------------|
| `app.py` | Точка входа, GUI (tkinter), кнопки и логика запросов кодов |
| `config_loader.py` | Загрузка/сохранение `config.ini` (IMAP, личная/корпоративная почта, UI) |
| `email_code_fetcher.py` | Получение кодов по IMAP (письма и SMS) |
| `settings_store.py` | Доп. настройки в `settings.json` |
| `app_dir.py` | Базовая директория приложения (для exe и запуска из исходников) |
| `config_example.ini` | Пример конфигурации |
| `energochain_fetcher.spec` | Конфиг PyInstaller для сборки exe |
| `requirements.txt` | Зависимости приложения (imap-tools) |
| `requirements-build.txt` | Зависимости для сборки (pyinstaller) |
| `build.bat` | Скрипт сборки exe под Windows |

После сборки появляются каталоги `build/` и `dist/` (их можно добавить в `.gitignore`).
