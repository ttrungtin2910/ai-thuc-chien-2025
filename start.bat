@echo off
echo ================================================
echo          DVC.AI - DIGITAL ASSISTANT
echo    Trợ lý dịch vụ công và cổng Kiến thức
echo ================================================
echo.

echo [1/3] Kiem tra moi truong...
echo.

REM Kiem tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python khong duoc cai dat!
    echo Vui long cai dat Python tu https://python.org
    pause
    exit /b 1
)

REM Kiem tra Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js khong duoc cai dat!
    echo Vui long cai dat Node.js tu https://nodejs.org
    pause
    exit /b 1
)

echo [2/3] Khoi dong Backend (FastAPI)...
echo.

REM Khoi dong backend trong terminal moi
start "Backend - FastAPI" cmd /k "cd /d be && echo Dang khoi dong Backend... && python main.py"

echo Cho Backend khoi dong... (5 giay)
timeout /t 5 /nobreak >nul

echo [3/3] Khoi dong Frontend (ReactJS)...
echo.

REM Khoi dong frontend trong terminal moi
start "Frontend - ReactJS" cmd /k "cd /d fe && echo Dang cai dat dependencies... && npm install && echo Dang khoi dong Frontend... && npm start"

echo.
echo ================================================
echo THONG TIN TRUY CAP:
echo ================================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo TAI KHOAN MAC DINH:
echo Username: admin
echo Password: password123
echo ================================================
echo THEME: Mệnh Thổ (Earth Element) - Tone màu ấm áp
echo BRANDING: DVC.AI - AI Assistant for Government
echo ================================================
echo.
echo Cac ung dung dang chay trong cac cua so terminal rieng biet.
echo Dong terminal nay de thoat.
echo.
pause
