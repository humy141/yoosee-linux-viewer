# Yoosee Linux Viewer - v1 (Stream & Link Discovery)

## Phiên bản v1 - Focus trên Xem Camera & Dò Đường Link

v1 là phiên bản nền tảng tập trung vào 3 điểm chính:
- **Xem stream RTSP từ camera trực tiếp**
- **Dò tìm & kiểm tra RTSP link, ONVIF endpoint**
- **Ghi video, phát hiện chuyển động, UI log**

## Tính năng v1

### 1. Dò tìm camera (Link Discovery)
- Quét IP để tìm RTSP port (554, 8554, 322)
- Thử tất cả RTSP path phổ biến:
  - `/onvif2` (ưu tiên cho FNKVision)
  - `/stream1`
  - `/stream`
  - `/live`
  - `/av0`, `/av1`
  - v.v.
- Thử ONVIF endpoint (port 80, 8080, 8000, 8888)
- Test credential (username/password)
- Return URL RTSP tốt nhất

### 2. Xem stream camera
- Mở RTSP stream bằng OpenCV
- Buffer nhỏ để giảm lag
- Tự động reconnect nếu disconnect
- Log lỗi rõ ràng: "auth failed", "timeout", "connection refused"
- Hiển thị frame real-time trong preview

### 3. Quản lý camera
- Thêm camera thủ công (IP + user/pass)
- Quét camera tự động (dò link)
- Lưu vào SQLite (cameras.db)
- Xem danh sách camera

### 4. Recording & Motion Detection
- Ghi video khi bấm "Ghi video"
- Phát hiện chuyển động real-time
- Log sự kiện

### 5. UI & Log
- Danh sách camera
- Preview stream
- Log event chi tiết
- Nút bắt đầu/dừng stream
- Nút ghi video
- Nút phát hiện chuyển động

## Không có trong v1

❌ PTZ (sẽ làm v2)  
❌ Preset vị trí (sẽ làm v2)  
❌ Joystick điều khiển (sẽ làm v2)  

## Cách dùng v1

### 1. Chạy app
```bash
python3 main.py
```

### 2. Thêm camera thủ công
- Nhấn "Thêm camera thủ công"
- Nhập IP, username, password
- App sẽ dò tìm RTSP URL tự động
- Lưu vào SQLite

### 3. Quét camera tự động
- Nhấn "Quét tìm camera tự động"
- Nhập IP, username, password
- App sẽ dò tìm RTSP stream
- Hiển thị kết quả
- Nhấn OK để thêm vào danh sách

### 4. Xem camera
- Chọn camera từ danh sách
- Nhấn "Bắt đầu" để mở stream
- Xem preview trực tiếp

### 5. Ghi video
- Chọn camera
- Nhấn "Ghi video" để bắt đầu ghi
- Nhấn "Dừng ghi" để lưu file

### 6. Phát hiện chuyển động
- Bấm "Phát hiện chuyển động: BẬT"
- Nếu có chuyển động, log sẽ hiển thị

## File quan trọng v1

- `app/link_discovery.py` - Dò RTSP link & ONVIF
- `app/camera_stream.py` - Thread xem stream RTSP
- `app/camera_manager.py` - Lưu/quản lý camera
- `app/motion_detector.py` - Phát hiện chuyển động
- `app/recorder.py` - Ghi video
- `ui/main_window.py` - Giao diện chính
- `ui/discovery_dialog.py` - Dialog dò tìm camera
- `ui/camera_dialog.py` - Dialog thêm camera

## Test v1 với camera SEA-U2

Ví dụ camera:
- IP: 192.168.1.4
- RTSP: rtsp://192.168.1.4:554/onvif2
- User: admin
- Pass: admin123#

Bước test:
1. Chạy app
2. Dò tìm camera: 192.168.1.4 / admin / admin123#
3. Kiểm tra log:
   - "✓ Tìm thấy X RTSP stream"
   - "✓ Tìm thấy ONVIF endpoint"
4. Xem stream trực tiếp
5. Kiểm tra chất lượng video, lag, reconnect

## Lỗi thường gặp & cách fix

### Lỗi: "Không thể mở stream"
- Kiểm tra IP, port (mặc định 554)
- Kiểm tra firewall
- Thử user/pass khác

### Lỗi: "Invalid credentials"
- User/password sai
- Kiểm tra dấu `#` trong password

### Lỗi: "Connection timeout"
- Camera offline
- Mạng không ổn định
- Port RTSP bị chặn

### Lỗi: "Không tìm thấy stream"
- Camera không hỗ trợ RTSP
- RTSP bị tắt trên camera
- Port RTSP khác (không phải 554)
- Path RTSP khác (thêm vào RTSP_PATHS)

## Plan v2

v2 sẽ thêm:
- PTZ control (pan/tilt/zoom)
- Preset vị trí camera
- Joystick điều khiển
- Auto home sau timeout
- Kiểm tra PTZ support tự động

## Ghi chú

- v1 **không bao gồm PTZ** để giữ nguyên focus trên stream & link discovery
- PTZ sẽ là core feature của v2
- Camera FNKVision SEA-U2 có thể cần debug endpoint PTZ riêng nếu ONVIF không standard
