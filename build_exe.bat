@echo off
title RETROLENS - Build EXE
echo.
echo  Membangun RETROLENS.exe dengan PyInstaller...
echo.
call venv\Scripts\activate.bat
pip install pyinstaller -q --disable-pip-version-check
pyinstaller --onefile --noconsole --name RETROLENS ^
    --add-data "hand_landmarker.task;." ^
    --add-data "selfie_segmenter.tflite;." ^
    --hidden-import mediapipe ^
    --hidden-import cv2 ^
    launcher.py
echo.
echo  Build selesai! File ada di folder: dist\RETROLENS.exe
echo.
pause