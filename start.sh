#!/bin/bash

echo "================================================"
echo "          DVC.AI - DIGITAL ASSISTANT"
echo "    Trợ lý dịch vụ công và cổng Kiến thức"
echo "================================================"
echo ""

echo "[1/3] Kiem tra moi truong..."
echo ""

# Kiem tra Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 khong duoc cai dat!"
    echo "Vui long cai dat Python3"
    exit 1
fi

# Kiem tra Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js khong duoc cai dat!"
    echo "Vui long cai dat Node.js tu https://nodejs.org"
    exit 1
fi

echo "[2/3] Khoi dong Backend (FastAPI)..."
echo ""

# Khoi dong backend trong terminal moi
gnome-terminal --title="Backend - FastAPI" -- bash -c "
    cd be
    echo 'Dang khoi dong Backend...'
    python3 main.py
    exec bash
" 2>/dev/null || \
xterm -title 'Backend - FastAPI' -e "
    cd be
    echo 'Dang khoi dong Backend...'
    python3 main.py
    exec bash
" 2>/dev/null || \
echo "Khoi dong backend trong background..."

echo "Cho Backend khoi dong... (5 giay)"
sleep 5

echo "[3/3] Khoi dong Frontend (ReactJS)..."
echo ""

# Khoi dong frontend trong terminal moi
gnome-terminal --title="Frontend - ReactJS" -- bash -c "
    cd fe
    echo 'Dang cai dat dependencies...'
    npm install
    echo 'Dang khoi dong Frontend...'
    npm start
    exec bash
" 2>/dev/null || \
xterm -title 'Frontend - ReactJS' -e "
    cd fe
    echo 'Dang cai dat dependencies...'
    npm install
    echo 'Dang khoi dong Frontend...'
    npm start
    exec bash
" 2>/dev/null || \
echo "Khoi dong frontend trong background..."

echo ""
echo "================================================"
echo "THONG TIN TRUY CAP:"
echo "================================================"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "TAI KHOAN MAC DINH:"
echo "Username: admin"
echo "Password: password123"
echo "================================================"
echo "THEME: Mệnh Thổ (Earth Element) - Tone màu ấm áp"
echo "BRANDING: DVC.AI - AI Assistant for Government"
echo "================================================"
echo ""
echo "Cac ung dung dang chay trong cac cua so terminal rieng biet."
echo "Nhan Ctrl+C de thoat."
echo ""

# Keep script running
read -p "Nhan Enter de thoat..."
