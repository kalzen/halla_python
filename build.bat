@echo off
echo ========================================
echo    HALLA MEASUREMENT SYSTEM BUILDER
echo ========================================
echo.

echo Đang kích hoạt virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Đang cài đặt dependencies...
pip install -r requirements.txt

echo.
echo Đang build ứng dụng với PyInstaller...
pyinstaller main.spec

echo.
echo ========================================
echo Build hoàn thành!
echo File exe: dist\main.exe
echo ========================================
pause 