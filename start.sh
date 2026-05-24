#!/bin/bash
set -e

echo "========================================"
echo "  JobPlatform - Автозапуск"
echo "========================================"
echo ""

cd "$(dirname "$0")/backend"

echo "[1/4] Установка зависимостей..."
pip install -r requirements.txt -q

echo "[2/4] Миграции..."
python manage.py migrate --run-syncdb

echo "[3/4] Загрузка тестовых данных..."
python manage.py seed_data

echo "[4/5] Проверка порта 8000..."
PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Найден процесс на порту 8000 (PID: $PID), завершаем..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

echo "[5/5] Запуск сервера (Daphne + WebSocket)..."
echo ""
echo "  Backend:     http://127.0.0.1:8000"
echo "  Live Coding: http://127.0.0.1:8000/live/"
echo "  API Docs:    http://127.0.0.1:8000/api/docs/"
echo "  Admin:       http://127.0.0.1:8000/admin/"
echo ""
echo "  Ctrl+C для остановки"
echo "========================================"
echo ""

daphne -b 0.0.0.0 -p 8000 config.asgi:application
