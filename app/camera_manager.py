import json
from pathlib import Path

import cv2
from PyQt5.QtCore import QThread, pyqtSignal

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
            "port": int(port or 554),
            "username": username,
            "password": password,
            "rtsp_url": f"rtsp://{username}:{password}@{ip}:{int(port or 554)}/stream1",
        }
        cameras.append(camera)
        self.save_cameras(cameras)
        return camera

    def build_rtsp_url(self, camera):
        if camera.get("rtsp_url"):
            return camera.get("rtsp_url")
        ip = camera.get("ip")
        port = camera.get("port", 554)
        username = camera.get("username") or "admin"
        password = camera.get("password") or "admin"
        return f"rtsp://{username}:{password}@{ip}:{port}/stream1"


class CameraStreamThread(QThread):
    frame_ready = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            self.error.emit(f"Không thể mở camera: {self.rtsp_url}")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            self.frame_ready.emit(frame)

        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait(2000)
