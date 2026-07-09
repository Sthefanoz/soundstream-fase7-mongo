@echo off
title SoundStream (MongoDB) - servidor
cd /d "%~dp0soundstream"
echo ============================================
echo   SoundStream NoSQL (MongoDB Atlas)
echo   Abriendo en http://127.0.0.1:8000/
echo   (para detener: cierra esta ventana o Ctrl+C)
echo ============================================
start "" http://127.0.0.1:8000/
"%~dp0.venv\Scripts\python.exe" manage.py runserver
pause
