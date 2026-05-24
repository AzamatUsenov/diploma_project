@echo off
title JobPlatform - Full Stack
echo ========================================
echo   JobPlatform - Автозапуск
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/4] Установка зависимостей...
pip install -r requirements.txt -q

echo [2/4] Миграции...
python manage.py migrate --run-syncdb

echo [3/4] Загрузка тестовых данных...
python manage.py seed_data

echo [4/5] Проверка порта 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Найден процесс на порту 8000 (PID: %%a), завершаем...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [5/5] Запуск сервера (Daphne + WebSocket)...
echo.
echo  Backend:    http://127.0.0.1:8000
echo  Live Coding: http://127.0.0.1:8000/live/
echo  API Docs:   http://127.0.0.1:8000/api/docs/
echo  Admin:      http://127.0.0.1:8000/admin/
echo.
echo  Ctrl+C для остановки
echo ========================================
echo.

daphne -b 0.0.0.0 -p 8000 config.asgi:applicationPS C:\Users\User\diploma_project\backend> daphne -b 0.0.0.0 -p 8000 config.asgi:application
Starting server at tcp:port=8000:interface=0.0.0.0
HTTP/2 support not enabled (install the http2 and tls Twisted extras)
Configuring endpoint tcp:port=8000:interface=0.0.0.0
Listen failure: Couldn't listen on 0.0.0.0:8000: [WinError 10048] Обычно разрешается только одно использование адреса сокета (протокол/сетевой адрес/порт).
PS C:\Users\User\diploma_project\backend> 

