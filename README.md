# Yoosee Linux Viewer

Ứng dụng giám sát camera trên Linux, tương tự Yoosee, nhằm hỗ trợ camera IP FNKVision SEA-U2 và các camera RTSP/ONVIF tương thích.

## Tính năng chính

- Xem video trực tiếp từ camera
- Quản lý nhiều camera
- Ghi video tự động
- Phát hiện chuyển động
- Hiển thị nhật ký sự kiện bằng tiếng Việt
- Giao diện PyQt5 thân thiện với Linux
- Lưu thông tin camera trên máy cục bộ

## Môi trường phát triển

- Python 3.10+
- PyQt5
- OpenCV
- NumPy

## Cài đặt nhanh

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Hướng dẫn sử dụng

1. Mở ứng dụng.
2. Đăng nhập với tài khoản demo `admin` / `admin`.
3. Chọn "Thêm camera".
4. Nhập IP, port, username, password của camera.
5. Chọn camera rồi nhấn "Bắt đầu".
6. Có thể bật "Ghi video" và "Phát hiện chuyển động".

## Lưu ý

- Đây là phiên bản demo / nền tảng chạy trên Linux.
- Đối với camera FNKVision SEA-U2, cần kiểm tra đúng RTSP URL nhằm truy cập stream.
- Ví dụ: `rtsp://admin:password@192.168.1.10:554/stream1`

## Giấy phép

MIT
