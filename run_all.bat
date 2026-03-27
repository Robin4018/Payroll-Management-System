@echo off
echo Starting Django Server and Celery Worker...
cd /d %~dp0

:: Start Django Server in a new window
start "Django Server" cmd /k "venv\Scripts\python.exe manage.py runserver"

:: Start Celery Worker in a new window
echo Starting Celery Worker...
start "Celery Worker" cmd /k "venv\Scripts\python.exe -m celery -A backend worker -l info -P eventlet"

echo Both processes started!
pause
