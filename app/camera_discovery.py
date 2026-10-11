import socket
import threading
import time
from typing import List, Dict, Optional
import cv2
import requests
from requests.auth import HTTPBasicAuth


class CameraDiscovery:
    """Tự động phát hiện camera trên mạng local, tối ưu cho FNKVision SEA-U2"""
    
    # Cấu hình cho FNKVision SEA-U2
    FNKVISION_PORTS = [554, 8554, 8080, 8000, 80]  # Port RTSP và HTTP
    FNKVISION_PATHS = [
        # RTSP paths phổ biến cho FNKVision
        "/stream1",
        "/stream",
        "/live",
        "/live/ch0",
        "/live/ch1",
        "/onvif/stream1",
        "/rtsp/stream1",
        "/media/stream1",
        # HTTP paths
        "/api/stream",
        "/cgi-bin/api/stream",
        "/mjpeg/1",
        "/mjpeg/ch1",
    ]
    
    TIMEOUT = 3
    FNKVISION_DEFAULT_CREDS = [
        ("admin", "admin"),
        ("admin", "12345"),
        ("root", "admin"),
        ("test", "test"),
    ]

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
    def test_rtsp_url(url: str) -> bool:
        """Kiểm tra xem RTSP URL có hoạt động không"""
        try:
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                return ret
        except Exception:
            pass
        return False

    @staticmethod
    def get_camera_info_http(ip: str, port: int, username: str, password: str) -> Optional[Dict]:
        """Lấy thông tin camera qua HTTP API (cho FNKVision)"""
        try:
            # Thử các endpoint phổ biến của FNKVision
            endpoints = [
                "/cgi-bin/api/apiStatus",
                "/api/status",
                "/cgi-bin/configManager.cgi?action=getConfig&name=SystemInfo",
            ]
            
            for endpoint in endpoints:
                url = f"http://{ip}:{port}{endpoint}"
                response = requests.get(
                    url,
                    auth=HTTPBasicAuth(username, password),
                    timeout=CameraDiscovery.TIMEOUT
                )
                if response.status_code == 200:
                    return {
                        "method": "HTTP",
                        "endpoint": endpoint,
                        "status_code": response.status_code
                    }
        except Exception:
            pass
        return None

    @staticmethod
    def discover_fnkvision_camera(
        ip: str,
        port: int,
        username: str,
        password: str,
        callback=None
    ) -> Optional[Dict]:
        """Tìm kiếm camera FNKVision SEA-U2 với thông tin cụ thể"""
        
        if callback:
            callback(f"Kiểm tra {ip}:{port}...")
        
        # Kiểm tra RTSP
        for path in CameraDiscovery.FNKVISION_PATHS:
            if "/" in path and path.startswith("/") and not "api" in path and not "mjpeg" in path:
                rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}{path}"
                if CameraDiscovery.test_rtsp_url(rtsp_url):
                    camera = {
                        "ip": ip,
                        "port": port,
                        "username": username,
                        "password": password,
                        "rtsp_url": rtsp_url,
                        "name": f"FNKVision {ip}",
                        "type": "RTSP (FNKVision)",
                        "model": "FNKVision SEA-U2"
                    }
                    if callback:
                        callback(f"✓ Tìm thấy RTSP: {rtsp_url}")
                    return camera
        
        # Kiểm tra HTTP
        http_info = CameraDiscovery.get_camera_info_http(ip, port, username, password)
        if http_info:
            camera = {
                "ip": ip,
                "port": port,
                "username": username,
                "password": password,
                "rtsp_url": f"http://{ip}:{port}",
                "name": f"FNKVision {ip}",
                "type": "HTTP (FNKVision)",
                "model": "FNKVision SEA-U2"
            }
            if callback:
                callback(f"✓ Tìm thấy HTTP: {camera['rtsp_url']}")
            return camera
        
        return None

    @staticmethod
    def discover_cameras(
        username: str = "admin",
        password: str = "admin",
        callback=None
    ) -> List[Dict]:
        """Tìm kiếm camera trên mạng local, ưu tiên FNKVision SEA-U2"""
        cameras = []
        gateway = CameraDiscovery.get_gateway()
        
        if not gateway:
            if callback:
                callback("Không tìm thấy gateway")
            return cameras

        if callback:
            callback(f"Quét mạng từ {gateway}...")
            callback(f"Sử dụng username: {username}")

        ip_range = CameraDiscovery.get_network_range(gateway)
        total_ips = len(ip_range)
        
        for idx, ip in enumerate(ip_range):
            if callback:
                callback(f"[{idx+1}/{total_ips}] Kiểm tra {ip}...")
            
            # Thử các cổng RTSP/HTTP
            for port in CameraDiscovery.FNKVISION_PORTS:
                if CameraDiscovery.test_port(ip, port):
                    if callback:
                        callback(f"  ✓ Cổng mở: {ip}:{port}")
                    
                    # Thử các credential mặc định của FNKVision
                    found = False
                    for test_user, test_pass in CameraDiscovery.FNKVISION_DEFAULT_CREDS:
                        camera = CameraDiscovery.discover_fnkvision_camera(
                            ip, port, test_user, test_pass, callback
                        )
                        if camera:
                            cameras.append(camera)
                            found = True
                            break
                    
                    # Nếu không tìm thấy với credential mặc định, thử credential được cung cấp
                    if not found and (username, password) not in CameraDiscovery.FNKVISION_DEFAULT_CREDS:
                        camera = CameraDiscovery.discover_fnkvision_camera(
                            ip, port, username, password, callback
                        )
                        if camera:
                            cameras.append(camera)
        
        if callback:
            callback(f"\nKết quả: Tìm thấy {len(cameras)} camera")
        
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
