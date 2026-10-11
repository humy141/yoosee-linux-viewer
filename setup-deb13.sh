#!/bin/bash

# Setup Yoosee Linux Viewer - Debian 13 Full Environment Setup
# Cài đặt đầy đủ tất cả dependencies cho Debian 13 (Trixie)
# Usage: sudo bash setup-deb13.sh

set -e

echo "🔧 Yoosee Linux Viewer - Debian 13 Full Setup"
echo "============================================="
echo ""
echo "Script này sẽ cài đặt:"
echo "  - Python 3.11+"
echo "  - PyQt5 (GUI)"
echo "  - OpenCV (video processing)"
echo "  - FFmpeg (video recording)"
echo "  - ONVIF/SOAP libraries"
echo "  - SQLite (camera database)"
echo "  - Networking tools"
echo ""

# Kiểm tra root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Script này cần chạy với quyền root (sudo)"
    exit 1
fi

# Kiểm tra Debian 13
if ! grep -q "trixie\|13" /etc/os-release; then
    echo "⚠️  Warning: OS hiện tại không phải Debian 13"
    echo "Script vẫn cố gắng cài đặt..."
fi

echo "📋 Step 1: Cập nhật package list"
apt-get update
apt-get upgrade -y

echo ""
echo "📦 Step 2: Cài đặt Python 3.11+ & development tools"
apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    python3-wheel \
    build-essential \
    cmake \
    git

echo "Phiên bản Python: $(python3 --version)"
echo "Phiên bản pip: $(pip3 --version)"

echo ""
echo "📦 Step 3: Cài đặt X11 Display Server libraries"
apt-get install -y \
    libx11-dev \
    libx11-6 \
    libxext-dev \
    libxext6 \
    libxrender-dev \
    libxrender1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfontconfig1-dev

echo ""
echo "📦 Step 4: Cài đặt OpenGL/Rendering libraries"
apt-get install -y \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libglib2.0-dev

echo ""
echo "📦 Step 5: Cài đặt Qt5 libraries (PyQt5)"
apt-get install -y \
    qtbase5-dev \
    libqt5gui5 \
    libqt5core5t64 \
    libqt5dbus5 \
    libqt5network5 \
    libqt5widgets5 \
    libqt5opengl5 \
    libqt5svg5 \
    libqt5concurrent5

echo ""
echo "📦 Step 6: Cài đặt Image libraries (cho OpenCV)"
apt-get install -y \
    libjpeg62-turbo \
    libjpeg62-turbo-dev \
    libpng16-16 \
    libpng-dev \
    libtiff6 \
    libtiff-dev \
    libwebp7 \
    libwebp-dev

echo ""
echo "📦 Step 7: Cài đặt Video/Audio libraries (cho FFmpeg)"
apt-get install -y \
    ffmpeg \
    libavcodec60 \
    libavcodec-extra \
    libavformat60 \
    libswscale7 \
    libavutil58 \
    libswresample4 \
    libavdevice60

echo ""
echo "📦 Step 8: Cài đặt RTSP/Network libraries"
apt-get install -y \
    libssl-dev \
    libssl3 \
    libcurl4-openssl-dev \
    libcurl4 \
    curl \
    wget

echo ""
echo "📦 Step 9: Cài đặt SQLite (camera database)"
apt-get install -y \
    sqlite3 \
    libsqlite3-dev

echo ""
echo "📦 Step 10: Cài đặt Networking & System utilities"
apt-get install -y \
    net-tools \
    iputils-ping \
    dnsutils \
    netcat-traditional \
    telnet

echo ""
echo "📦 Step 11: Cài đặt encoding/compression libraries"
apt-get install -y \
    libbz2-dev \
    zlib1g \
    zlib1g-dev

echo ""
echo "📦 Step 12: Cài đặt system fonts (cho UI)"
apt-get install -y \
    fonts-dejavu \
    fonts-dejavu-core \
    fontconfig

echo ""
echo "🐍 Step 13: Cập nhật pip & setuptools"
pip3 install --upgrade pip setuptools wheel

echo ""
echo "📦 Step 14: Cài đặt Python packages cơ bản"
pip3 install \
    PyQt5==5.15.9 \
    PyQt5-sip==12.13.0 \
    opencv-python==4.8.1.78 \
    numpy==1.24.3 \
    requests==2.31.0 \
    Pillow==10.0.0

echo ""
echo "📦 Step 15: Cài đặt ONVIF libraries (cho PTZ v2 - optional)"
pip3 install \
    zeep==4.2.1 \
    onvif-zeep==0.2.12 || echo "⚠️  ONVIF packages có thể bị skip nếu lỗi"

echo ""
echo "📦 Step 16: Cài đặt Python development tools"
pip3 install \
    ipython \
    jupyter \
    pytest

echo ""
echo "📦 Step 17: Clean up cache"
apt-get clean
apt-get autoremove -y
pip3 cache purge

echo ""
echo "✅ Setup Debian 13 hoàn tất!"
echo ""
echo "📊 Kiểm tra cài đặt:"
echo "========================"
echo ""
echo "Python 3:"
python3 --version

echo ""
echo "pip3:"
pip3 --version

echo ""
echo "Python libraries check:"
python3 << 'EOF'
import sys
print("📦 PyQt5:", end=" ")
try:
    import PyQt5
    print(f"✓ {PyQt5.__version__}")
except ImportError as e:
    print(f"✗ {e}")

print("📦 OpenCV:", end=" ")
try:
    import cv2
    print(f"✓ {cv2.__version__}")
except ImportError as e:
    print(f"✗ {e}")

print("📦 NumPy:", end=" ")
try:
    import numpy
    print(f"✓ {numpy.__version__}")
except ImportError as e:
    print(f"✗ {e}")

print("📦 Pillow:", end=" ")
try:
    import PIL
    print(f"✓ {PIL.__version__}")
except ImportError as e:
    print(f"✗ {e}")

print("📦 Requests:", end=" ")
try:
    import requests
    print(f"✓ {requests.__version__}")
except ImportError as e:
    print(f"✗ {e}")

print("📦 ONVIF/Zeep:", end=" ")
try:
    import zeep
    print(f"✓ {zeep.__version__}")
except ImportError:
    print("⚠️  Optional (PTZ v2)")
EOF

echo ""
echo "FFmpeg:"
ffmpeg -version | head -1

echo ""
echo "SQLite3:"
sqlite3 --version

echo ""
echo "🚀 Hướng dẫn chạy app:"
echo "======================="
echo "1. Clone/download repo:"
echo "   git clone <repo-url>"
echo "   cd yoosee-linux-viewer"
echo ""
echo "2. (Optional) Tạo Python virtual environment:"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo ""
echo "3. Chạy app:"
echo "   python3 main.py"
echo ""
echo "📝 Troubleshooting:"
echo "==================="
echo "- Nếu lỗi PyQt5/Display: export QT_QPA_PLATFORM=offscreen"
echo "- Nếu lỗi OpenCV: pip3 install --upgrade opencv-python"
echo "- Nếu lỗi RTSP: kiểm tra ffmpeg -version"
echo "- Nếu lỗi ONVIF: optional, chỉ cần cho PTZ v2"
echo ""
echo "✨ Setup hoàn tất. Enjoy! 🎉"
