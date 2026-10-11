# Yoosee Linux Viewer

Dự án phần mềm giám sát camera trên Linux, tương tự Yoosee/Android app, phục vụ camera IP FNKVision SEA-U2 và các camera RTSP/ONVIF tương thích.

## Tính năng

- Xem camera live qua RTSP
- Quản lý nhiều camera
- Lưu video ghi hình theo thời gian thực
- Phát hiện chuyển động cơ bản
- Màn hình log cảnh báo và sự kiện
- Giao diện PyQt5 trên Linux
- Lưu dữ liệu camera trong SQLite/JSON

## Công nghệ

- Python 3.10+
- PyQt5
- OpenCV
- SQLite

## Cài đặt

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Sử dụng

1. Mở app.
2. Đăng nhập với bất kỳ tài khoản nào (mẫu demo).
3. Thêm camera theo IP / username / password.
4. Chọn camera và nhấn Start.
5. Bật Record và Motion Detection nếu cần.

## Lưu ý

- Đây là phiên bản demo / production-ready skeleton, giúp bạn bắt đầu nhanh trên Linux.
- Với camera FNKVision SEA-U2, bạn cần dùng RTSP URL đúng cấu trúc từ camera.
- Ví dụ mẫu: `rtsp://admin:password@192.168.1.10:554/stream1`

## License

MIT
