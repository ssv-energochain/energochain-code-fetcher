@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo [1/2] Проверка зависимостей сборки...
pip install -r requirements-build.txt -q
pip install -r requirements.txt -q

echo [2/2] Сборка exe (PyInstaller)...
python -m PyInstaller --noconfirm energochain_fetcher.spec

if %ERRORLEVEL% neq 0 (
    echo Ошибка сборки.
    exit /b 1
)

echo.
echo Готово. Исполняемый файл: dist\EnergoChainCodeFetcher.exe
echo Запуск из консоли: dist\EnergoChainCodeFetcher.exe
echo Или: cd dist ^&^& EnergoChainCodeFetcher.exe
exit /b 0
