import json
from pathlib import Path
from app.config import CAMERA_FILE, ensure_config


class CameraStore:
    def __init__(self):
        ensure_config()

    def list_cameras(self):
        try:
            return json.loads(CAMERA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def save_cameras(self, cameras):
        CAMERA_FILE.write_text(json.dumps(cameras, indent=2), encoding="utf-8")

    def add_camera(self, name, ip, port, username, password):
        cameras = self.list_cameras()
        camera = {
            "id": len(cameras) + 1,
            "name": name,
            "ip": ip,
            "port": int(port),
            "username": username,
            "password": password,
            "rtsp_url": f"rtsp://{username}:{password}@{ip}:{port}/stream1",
        }
        cameras.append(camera)
        self.save_cameras(cameras)
        return camera

    def build_rtsp_url(self, camera):
        ip = camera.get("ip")
        port = camera.get("port", 554)
        username = camera.get("username") or "admin"
        password = camera.get("password") or "admin"
        return f"rtsp://{username}:{password}@{ip}:{port}/stream1"
