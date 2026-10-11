#!/bin/bash

# Check Environment - Kiểm tra môi trường trước khi chạy app
# Usage: bash check-environment.sh

echo "🔍 Kiểm tra môi trường Yoosee Linux Viewer"
echo "========================================="

echo ""

CHECK_PASSED=0
CHECK_FAILED=0
CHECK_WARN=0

check_command() {
    local cmd=$1
    local name=$2
    if command -v "$cmd" &> /dev/null; then
        local version=$("$cmd" --version 2>&1 | head -1)
        echo "✅ $name: $version"
        ((CHECK_PASSED++))
    else
        echo "❌ $name: Không tìm thấy"
        ((CHECK_FAILED++))
    fi
}

check_python_package() {
    local package=$1
    local name=$2
    if python3 -c "import $package" 2>/dev/null; then
        local version=$(python3 -c "import $package; print(getattr($package, '__version__', 'installed'))" 2>/dev/null)
        echo "✅ $name: $version"
        ((CHECK_PASSED++))
    else
        echo "❌ $name: Không tìm thấy"
        ((CHECK_FAILED++))
    fi
}

check_library() {
    local lib=$1
    local name=$2
    if ldconfig -p | grep -q "$lib"; then
        echo "✅ $name: Cài đặt"
        ((CHECK_PASSED++))
    else
        echo "⚠️  $name: Không tìm thấy"
        ((CHECK_WARN++))
    fi
}

echo "📋 1. Kiểm tra hệ thống"
echo "====================="
uname -a
echo ""

echo "📋 2. Kiểm tra Python"
echo "==================="
check_command "python3" "Python 3"
echo "Python path: $(which python3)"
python3_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
if python3 - <<'PY'
import sys
print(sys.version_info >= (3, 7))
PY
then
    echo "✅ Python 3.7+ requirement: PASS"
    ((CHECK_PASSED++))
else
    echo "❌ Python 3.7+ requirement: FAIL"
    ((CHECK_FAILED++))
fi
echo ""

echo "📋 3. Kiểm tra pip3"
echo "==================="
check_command "pip3" "pip3"
echo "pip3 path: $(which pip3)"

echo ""

echo "📋 4. Kiểm tra Python packages"
echo "=============================="
check_python_package "PyQt5" "PyQt5"
check_python_package "cv2" "OpenCV"
check_python_package "numpy" "NumPy"
check_python_package "requests" "Requests"
check_python_package "PIL" "Pillow"
echo ""

echo "📋 5. Kiểm tra Python packages tùy chọn"
echo "========================================"
if python3 -c "import zeep" 2>/dev/null; then
    echo "✅ Zeep (ONVIF): Installed"
    ((CHECK_PASSED++))
else
    echo "⚠️  Zeep (ONVIF): Không cài đặt (tùy chọn cho PTZ v2)"
    ((CHECK_WARN++))
fi

if python3 -c "import onvif" 2>/dev/null; then
    echo "✅ ONVIF client: Installed"
    ((CHECK_PASSED++))
else
    echo "⚠️  ONVIF client: Không cài đặt (tùy chọn cho PTZ v2)"
    ((CHECK_WARN++))
fi
echo ""

echo "📋 6. Kiểm tra System libraries"
echo "=============================="
check_library "libqt5gui" "Qt5 GUI"
check_library "libqt5core" "Qt5 Core"
check_library "libqt5network" "Qt5 Network"
check_library "libqt5widgets" "Qt5 Widgets"
check_library "libqt5opengl" "Qt5 OpenGL"
echo ""

echo "📋 7. Kiểm tra OpenGL/Display"
echo "============================"
check_library "libgl1" "OpenGL"
check_library "libx11" "X11"
check_library "libglib2" "GLib"
echo ""

echo "📋 8. Kiểm tra Video/Audio libraries"
echo "===================================="
check_library "libavcodec" "FFmpeg libavcodec"
check_library "libavformat" "FFmpeg libavformat"
check_library "libswscale" "FFmpeg libswscale"
check_command "ffmpeg" "FFmpeg"
echo ""

echo "📋 9. Kiểm tra RTSP/Network libraries"
echo "====================================="
check_library "libssl" "OpenSSL"
check_library "libcurl" "libcurl"
check_library "libsqlite3" "SQLite3"
echo ""

echo "📋 10. Kiểm tra tiện ích hệ thống"
echo "==============================="
check_command "sqlite3" "SQLite3 CLI"
check_command "curl" "curl"
check_command "wget" "wget"
check_command "git" "Git"
echo ""

echo "📋 11. Kiểm tra Display/GUI environment"
echo "====================================="
if [ -n "$DISPLAY" ]; then
    echo "✅ DISPLAY: $DISPLAY"
    ((CHECK_PASSED++))
else
    echo "⚠️  DISPLAY: Không tìm thấy (GUI có thể không hoạt động)"
    ((CHECK_WARN++))
fi

if command -v "xdpyinfo" &> /dev/null; then
    echo "✅ X11 display info: Available"
    ((CHECK_PASSED++))
else
    echo "⚠️  X11 display info: Không cài đặt"
    ((CHECK_WARN++))
fi
echo ""

echo "📋 12. Kiểm tra file cấu hình app"
echo "================================="
if [ -f "main.py" ]; then
    echo "✅ main.py: Tìm thấy"
    ((CHECK_PASSED++))
else
    echo "⚠️  main.py: Không tìm thấy (chạy script từ root directory của repo)"
    ((CHECK_WARN++))
fi

if [ -f "app/camera_manager.py" ]; then
    echo "✅ app/: Tìm thấy"
    ((CHECK_PASSED++))
else
    echo "⚠️  app/: Không tìm thấy"
    ((CHECK_WARN++))
fi

if [ -f "ui/main_window.py" ]; then
    echo "✅ ui/: Tìm thấy"
    ((CHECK_PASSED++))
else
    echo "⚠️  ui/: Không tìm thấy"
    ((CHECK_WARN++))
fi
echo ""

echo "📊 Kết quả kiểm tra"
echo "=================="
echo "✅ Passed: $CHECK_PASSED"
echo "⚠️  Warnings: $CHECK_WARN"
echo "❌ Failed: $CHECK_FAILED"
echo ""

if [ $CHECK_FAILED -eq 0 ]; then
    echo "🎉 Môi trường sẵn sàng! Bạn có thể chạy app:"
    echo "   python3 main.py"
    echo ""
    exit 0
else
    echo "❌ Có $CHECK_FAILED lỗi cần sửa trước khi chạy app"
    echo ""
    echo "💡 Hướng dẫn fix:"
    echo "1. Chạy setup script:"
    echo "   sudo bash setup-deb13.sh"
    echo ""
    echo "2. Hoặc cài đặt thủ công:"
    echo "   sudo apt-get install -y python3-pyqt5 python3-opencv python3-requests"
    echo ""
    echo "3. Hoặc cài via pip:"
    echo "   pip3 install PyQt5 opencv-python requests Pillow numpy"
    echo ""
    exit 1
fi
