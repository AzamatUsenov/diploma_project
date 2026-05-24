@echo off
title JobPlatform - WebSocket Server (Port 8001)
echo ========================================
echo   JobPlatform - WebSocket Server (Daphne)
echo ========================================
echo.

cd /d "%~dp0backend"

echo Запуск Daphne ASGI сервера на порту 8001...
echo.
echo  WebSocket:     ws://127.0.0.1:8001/ws/live/<session_id>/?token=...
echo  HTTP:          http://127.0.0.1:8001
echo  Live Coding:   http://127.0.0.1:8001/live/
echo  API Docs:      http://127.0.0.1:8001/api/docs/
echo.
echo  (Основной HTTP API должен работать на порту 8000)
echo.
echo  Ctrl+C для остановки
echo ========================================
echo.

daphne -b 0.0.0.0 -p 8001 config.asgi:application
