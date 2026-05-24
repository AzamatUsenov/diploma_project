@echo off
title JobPlatform - Full Stack
echo ========================================
echo   JobPlatform - Backend + Frontend
echo ========================================
echo.

:: Запуск backend в новом окне
start "JobPlatform Backend" cmd /k "cd /d %~dp0 && call start.bat"

:: Пауза чтобы backend поднялся
timeout /t 5 /nobreak > nul

:: Запуск Flutter frontend
echo Запуск Flutter...
cd /d "%~dp0frontend_app"
flutter run -d chrome
