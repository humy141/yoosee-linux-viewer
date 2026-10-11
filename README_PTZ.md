# YOosee Linux Viewer PTZ Support

## Mục tiêu

Bản PTZ cơ bản này giúp app Linux có thể gửi lệnh điều khiển góc nhìn (pan/tilt) và zoom nếu camera hỗ trợ ONVIF PTZ.

## Tính năng

- ONVIF PTZ manager base
- UI điều khiển PTZ trong giao diện chính
- Nút lên / xuống / trái / phải / center / zoom in / zoom out / stop
- Log event PTZ

## Lưu ý quan trọng

PTZ chỉ hoạt động nếu camera thật sự hỗ trợ **ONVIF PTZ** hoặc **API PTZ riêng của hãng**.

Nếu camera không hỗ trợ PTZ, ứng dụng sẽ log lỗi như:
- "Không tìm thấy service PTZ qua ONVIF"

## Cách dùng

1. Chọn camera trong danh sách
2. Nhấn nút "Điều khiển PTZ"
3. Dùng nút:
   - ↑: lên
   - ↓: xuống
   - ←: trái
   - →: phải
   - ●: về giữa
   - Zoom + / Zoom -: phóng to / thu nhỏ
   - Dừng: ngừng di chuyển

## Cập nhật sau này

Bạn có thể cập nhật lên v2 bằng cách:
- thêm preset vị trí (home, left, right, top, bottom)
- thêm điều khiển joystick
- thêm kiểm tra ONVIF PTZ tự động
- thêm API riêng cho FNKVision nếu camera không hỗ trợ ONVIF chuẩn

## Ghi chú

Đây là phiên bản PTZ cơ bản. Với camera FNKVision SEA-U2, nếu it không hoạt động ngay, cần phát hiện endpoint PTZ thực tế của camera bằng debug tool riêng.
