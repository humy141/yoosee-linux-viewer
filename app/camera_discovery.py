import socket
import threading
import time
from typing import List, Dict, Optional
import cv2
import requests
from requests.auth import HTTPBasicAuth


class CameraDiscovery:
    """Tự động phát hiện camera trên mạng local"""
    
    COMMON_PORTS = [554, 8554, 8080, 8000, 80, 443]
    COMMON_PATHS = [
        "/stream1",
        "/stream",
        "/live",
        "/video",
        "/stream1/unicast",
        "/cam/realmonitor",
        "/h264/ch1",
        "/onvif/profile1/media/stream1",
    ]
    TIMEOUT = 2

    @staticmethod
    def get_gateway() -> Optional[str]:
        """Lấy gateway mặc định để scan mạng"""
        try:
            import subprocess
            result = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split("\n"):
                if "default via" in line:
                    parts = line.split()
                    gateway = parts[2]
                    return gateway
        except Exception:
            pass
        return None

    @staticmethod
    def get_network_range(gateway: str) -> List[str]:
        """Tính toán range IP từ gateway"""
        try:
            parts = gateway.split(".")
            network = f"{parts[0]}.{parts[1]}.{parts[2]}"
            return [f"{network}.{i}" for i in range(1, 255)]
        except Exception:
            return []

    @staticmethod
    def test_port(ip: str, port: int) -> bool:
        """Kiểm tra cổng có mở không"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CameraDiscovery.TIMEOUT)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    @staticmethod
    def test_rtsp_url(url: str, username: str = "admin", password: str = "admin") -> bool:
        """Kiểm tra xem RTSP URL có hoạt động không"""
        try:
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                cap.release()
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def test_http_stream(ip: str, port: int, username: str = "admin", password: str = "admin") -> Optional[str]:
        """Kiểm tra HTTP stream"""
        try:
            url = f"http://{ip}:{port}/"
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=CameraDiscovery.TIMEOUT
            )
            if response.status_code == 200:
                return url
        except Exception:
            pass
        return None

    @staticmethod
    def discover_cameras(
        username: str = "admin",
        password: str = "admin",
        callback=None
    ) -> List[Dict]:
        """Tìm kiếm camera trên mạng local"""
        cameras = []
        gateway = CameraDiscovery.get_gateway()
        
        if not gateway:
            if callback:
                callback("Không tìm thấy gateway")
            return cameras

        if callback:
            callback(f"Scanning mạng từ {gateway}...")

        ip_range = CameraDiscovery.get_network_range(gateway)
        
        for ip in ip_range:
            for port in CameraDiscovery.COMMON_PORTS:
                if CameraDiscovery.test_port(ip, port):
                    if callback:
                        callback(f"Phát hiện cổng mở: {ip}:{port}")
                    
                    # Thử RTSP
                    if port == 554 or port == 8554:
                        for path in CameraDiscovery.COMMON_PATHS:
                            rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}{path}"
                            if CameraDiscovery.test_rtsp_url(rtsp_url):
                                camera = {
                                    "ip": ip,
                                    "port": port,
                                    "username": username,
                                    "password": password,
                                    "rtsp_url": rtsp_url,
                                    "name": f"Camera {ip}",
                                    "type": "RTSP"
                                }
                                cameras.append(camera)
                                if callback:
                                    callback(f"✓ Tìm thấy camera: {rtsp_url}")
                                break
                    
                    # Thử HTTP
                    http_url = CameraDiscovery.test_http_stream(ip, port, username, password)
                    if http_url:
                        camera = {
                            "ip": ip,
                            "port": port,
                            "username": username,
                            "password": password,
                            "rtsp_url": http_url,
                            "name": f"Camera {ip}",
                            "type": "HTTP"
                        }
                        cameras.append(camera)
                        if callback:
                            callback(f"✓ Tìm thấy camera: {http_url}")
        
        return cameras


class AsyncCameraDiscovery(threading.Thread):
    """Phát hiện camera bất đồng bộ (chạy trong thread)"""
    
    def __init__(self, username: str = "admin", password: str = "admin", callback=None):
        super().__init__()
        self.daemon = True
        self.username = username
        self.password = password
        self.callback = callback
        self.result = []
        self.running = True

    def run(self):
        self.result = CameraDiscovery.discover_cameras(
            self.username,
            self.password,
            self.callback
        )

    def stop(self):
        self.running = False
