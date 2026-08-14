@echo off
title RETROLENS - Setup dan Jalankan
color 0A
echo.
echo  ================================================
echo       RETROLENS - Hand Tracking Filter App
echo  ================================================
echo.

REM Cek Python tersedia
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python tidak ditemukan di sistem ini.
    echo.
    echo  Silakan install Python 3.9 atau lebih baru dari:
    echo  https://www.python.org/downloads/
    echo.
    echo  Pastikan centang "Add Python to PATH" saat install.
    echo.
    pause
    exit /b 1
)

REM Buat venv jika belum ada
if not exist "venv\" (
    echo  [1/3] Membuat virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  [ERROR] Gagal membuat virtual environment.
        pause
        exit /b 1
    )
)

REM Install dependencies
echo  [2/3] Menginstal / memperbarui dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo  [ERROR] Gagal menginstal dependencies.
    pause
    exit /b 1
)

REM Jalankan launcher
echo  [3/3] Menjalankan RETROLENS Launcher...
echo.
pythonw launcher.py 2>nul
if errorlevel 1 (
    python launcher.py
)