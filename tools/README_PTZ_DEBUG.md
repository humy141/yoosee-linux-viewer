# PTZ Debug Tool - Công cụ tìm kiếm endpoint PTZ

## Mục đích

Công cụ này giúp tìm kiếm endpoint PTZ (Pan/Tilt/Zoom) trên camera FNKVision SEA-U2 hoặc các camera ONVIF khác.

Nếu camera của bạn có hỗ trợ PTZ trên Yoosee/Android/Windows nhưng app Linux không nhận diện được, công cụ này sẽ giúp:
- Quét các endpoint ONVIF phổ biến
- Quét các CGI endpoint của FNKVision
- Tìm ra đường dẫn PTZ đúng
- Tạo report JSON để bạn xác nhận

## Cách dùng

### GUI Mode (Dễ dùng nhất)

```bash
cd yoosee-linux-viewer
python tools/ptz_debug_gui.py
```

Sau đó:
1. Nhập IP camera: `192.168.1.4`
2. Nhập username: `admin`
3. Nhập password: `admin123#` (có dấu #)
4. Nhập ports: `80,8080,8000,8888,554,81`
5. Nhấn "🚀 Bắt đầu quét PTZ"
6. Xem kết quả trong nhật ký
7. Nhấn "💾 Lưu kết quả" để lưu vào file JSON

### Command Line Mode

```bash
python tools/ptz_debug_tool.py --ip 192.168.1.4 --user admin --pass "admin123#" --port 80 --out ptz_report.json
```

## Kết quả

Công cụ sẽ tìm kiếm các endpoint sau:

### ONVIF Device Service
- `/onvif/device_service`
- `/onvif/DeviceService`
- `/onvif/device`

### ONVIF Media Service
- `/onvif/media_service`
- `/onvif/MediaService`
- `/onvif/media`

### ONVIF PTZ Service ⭐
- `/onvif/ptz_service`
- `/onvif/PTZService`
- `/onvif/ptz`

### CGI Endpoints (FNKVision API)
- `/cgi-bin/ptz.cgi`
- `/cgi-bin/ptzControl.cgi`
- `/cgi-bin/camera.cgi`
- `/api/ptz`

## Giải thích kết quả

Nếu bạn thấy trong nhật ký:

```
✓ TÌM THẤY PTZ: http://192.168.1.4:80/onvif/ptz_service
```

Có nghĩa:
- Camera có endpoint ONVIF PTZ
- Địa chỉ: `http://192.168.1.4:80/onvif/ptz_service`
- Điều này có thể được dùng để điều khiển PTZ trong app

## Nếu không tìm thấy endpoint nào

1. Kiểm tra username/password có đúng không
2. Kiểm tra camera có bật ONVIF không (xem web admin camera)
3. Thử các port khác
4. Gửi report JSON cho developer để phân tích thêm

## File JSON Output

File `ptz_discovery_report.json` sẽ chứa:
- Danh sách tất cả endpoint được quét
- Status code của mỗi endpoint
- Loại endpoint (ONVIF hoặc CGI)

```json
{
  "onvif": [
    {
      "url": "http://192.168.1.4:80/onvif/device_service",
      "found": true,
      "type": "onvif_device"
    }
  ],
  "ptz": [
    {
      "url": "http://192.168.1.4:80/onvif/ptz_service",
      "found": true,
      "type": "onvif_ptz"
    }
  ]
}
```

## Tiếp theo

Khi bạn có kết quả:
1. Chia sẻ file JSON hoặc screenshot nhật ký
2. Mình sẽ phân tích endpoint PTZ của camera bạn
3. Cập nhật app Linux để hỗ trợ endpoint đó
4. Bạn sẽ có PTZ hoạt động giống Yoosee trên Android
