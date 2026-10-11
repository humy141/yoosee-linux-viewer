# Yoosee Linux Viewer

Linux viewer cho camera Yoosee / FNKVision / ONVIF, tập trung vào:
- khám phá và xác định đường link RTSP/ONVIF
- xem camera trực tiếp từ Linux
- ghi video và phát hiện chuyển động
- chuẩn bị cho v2 với PTZ, preset và điều khiển camera

## Mục tiêu của phiên bản hiện tại

Phiên bản v1 đang tập trung vào:
- dò tìm camera
- xác định URL RTSP đúng
- mở stream và xem trực tiếp
- ghi video
- motion detection
- log sự kiện rõ ràng

PTZ sẽ được làm ở phiên bản v2 riêng, không phải v1.

## Cấu trúc thư mục

- `app/` - logic xử lý camera, stream, motion, discovery
- `ui/` - giao diện chính, dialog thêm/quét camera
- `setup-deb13.sh` - cài đặt môi trường cho Debian 13
- `check-environment.sh` - kiểm tra môi trường trước khi chạy app
- `README_v1.md` - hướng dẫn v1 theo trọng tâm stream và link discovery
- `README_PTZ.md` - hướng dẫn PTZ cơ bản

## Yêu cầu môi trường

- Debian 13 / Ubuntu tương thích
- Python 3.7+
- PyQt5
- OpenCV
- FFmpeg
- SQLite

## Cài đặt môi trường

### 1. Cài đặt đầy đủ dependencies
```bash
chmod +x setup-deb13.sh check-environment.sh
sudo ./setup-deb13.sh
```

### 2. Kiểm tra môi trường
```bash
bash check-environment.sh
```

Nếu có lỗi, script sẽ chỉ ra package nào thiếu.

## Chạy app

Từ thư mục repo:

```bash
python3 main.py
```

Nếu chạy ở môi trường headless hoặc không có GUI:

```bash
export QT_QPA_PLATFORM=offscreen
python3 main.py
```

## Về camera RTSP

Các path phổ biến được ưu tiên trong v1:
- `/onvif2`
- `/stream1`
- `/stream`
- `/live`
- `/av0`, `/av1`
- `/media/video0`

Ví dụ:
```bash
rtsp://admin:admin123#@192.168.1.4:554/onvif2
```

## Sử dụng nhanh

- Chọn camera trong danh sách
- Nhấn "Bắt đầu" để xem
- Nhấn "Ghi video" để lưu video
- Bật "Phát hiện chuyển động" nếu cần
- Chạy "Quét tìm camera tự động" khi chưa biết URL

## Tài liệu liên quan

- `README_v1.md` - hướng dẫn v1 (xem camera + dò đường link)
- `README_PTZ.md` - hướng dẫn PTZ cơ bản

## Lưu ý quan trọng

- v1 tập trung vào stream và discovery, không phải PTZ
- PTZ sẽ được phát triển trong v2
- Một số camera hỗ trợ RTSP nhưng không hỗ trợ ONVIF chuẩn hoặc cần API riêng

## Troubleshooting

### Không mở được stream
- Kiểm tra IP / username / password
- Kiểm tra port RTSP 554 / 8554 / 322
- Thử các URL khác như `/onvif2`, `/stream1`, `/live`
- Kiểm tra firewall / mạng

### GUI không hiển thị
- Kiểm tra `DISPLAY`
- Nếu cần, dùng:
```bash
export QT_QPA_PLATFORM=offscreen
```

### Camera không cho RTSP
- Kiểm tra ONVIF endpoint
- Dùng tool dò link để xác định route stream có sẵn

## Roadmap

- v1: stream, discovery, view, recording, motion
- v2: PTZ camera control, presets, joystick, auto-home
