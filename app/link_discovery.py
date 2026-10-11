import socket
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET


class CameraLinkDiscovery:
    """Dò tìm RTSP link, ONVIF endpoint, và kiểm tra kết nối camera."""

    # RTSP streams phổ biến cho camera
    RTSP_PATHS = [
        "/onvif2",
        "/stream1",
        "/stream",
        "/live",
        "/av0",
        "/av1",
        "/media/video0",
        "/h264/ch0/main/av_stream",
        "/h264/ch0/sub/av_stream",
        "/live/ch0",
        "/live/ch1",
        "/mjpeg/ch0",
        "/video0",
    ]

    # ONVIF endpoints
    ONVIF_PATHS = [
        "/onvif/device_service",
        "/onvif/DeviceService",
        "/onvif/media_service",
        "/onvif/MediaService",
    ]

    # Các port phổ biến cho RTSP
    RTSP_PORTS = [554, 8554, 322]

    # Các port phổ biến cho ONVIF (HTTP)
    HTTP_PORTS = [80, 8080, 8000, 8888, 81]

    def __init__(self, camera_ip, username="admin", password="admin", timeout=5):
        self.camera_ip = camera_ip
        self.username = username
        self.password = password
        self.timeout = timeout
        self.results = {}

    def is_port_open(self, port):
        """Kiểm tra port có mở không."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.camera_ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def test_rtsp_url(self, url):
        """Test RTSP URL bằng cách kết nối (không stream full)."""
        try:
            import cv2
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                cap.release()
                return True
            cap.release()
            return False
        except Exception:
            return False

    def discover_rtsp_streams(self):
        """Tìm RTSP stream available."""
        results = []
        self.results["rtsp_streams"] = []

        for port in self.RTSP_PORTS:
            if not self.is_port_open(port):
                continue

            for path in self.RTSP_PATHS:
                # Build URL with auth
                if self.username and self.password:
                    url = f"rtsp://{self.username}:{self.password}@{self.camera_ip}:{port}{path}"
                else:
                    url = f"rtsp://{self.camera_ip}:{port}{path}"

                # Test URL
                if self.test_rtsp_url(url):
                    result = {
                        "url": url,
                        "port": port,
                        "path": path,
                        "status": "OK",
                    }
                    results.append(result)
                    self.results["rtsp_streams"].append(result)

        return results

    def discover_onvif_endpoints(self):
        """Tìm ONVIF endpoints."""
        results = []
        self.results["onvif_endpoints"] = []

        for port in self.HTTP_PORTS:
            if not self.is_port_open(port):
                continue

            for path in self.ONVIF_PATHS:
                url = f"http://{self.camera_ip}:{port}{path}"

                try:
                    resp = requests.get(
                        url,
                        auth=HTTPBasicAuth(self.username, self.password),
                        timeout=self.timeout,
                        verify=False,
                    )
                    if resp.status_code in (200, 401, 403, 405):
                        result = {
                            "url": url,
                            "port": port,
                            "path": path,
                            "status_code": resp.status_code,
                            "status": "FOUND",
                        }
                        results.append(result)
                        self.results["onvif_endpoints"].append(result)
                except Exception as e:
                    pass

        return results

    def test_credentials(self):
        """Test xem username/password có đúng không."""
        self.results["credentials_test"] = {}

        # Test ONVIF auth
        for port in self.HTTP_PORTS:
            if not self.is_port_open(port):
                continue
            url = f"http://{self.camera_ip}:{port}/onvif/device_service"
            try:
                resp = requests.get(
                    url,
                    auth=HTTPBasicAuth(self.username, self.password),
                    timeout=self.timeout,
                    verify=False,
                )
                if resp.status_code == 200:
                    self.results["credentials_test"]["http_auth"] = "SUCCESS"
                    return True
                elif resp.status_code == 401:
                    self.results["credentials_test"]["http_auth"] = "FAILED - Invalid credentials"
                    return False
            except Exception:
                pass

        self.results["credentials_test"]["http_auth"] = "UNKNOWN"
        return None

    def discover_all(self):
        """Dò tìm tất cả thông tin camera."""
        self.results = {
            "camera_ip": self.camera_ip,
            "username": self.username,
        }

        # Test credentials trước
        self.test_credentials()

        # Tìm RTSP streams
        self.discover_rtsp_streams()

        # Tìm ONVIF endpoints
        self.discover_onvif_endpoints()

        return self.results

    def get_best_rtsp_url(self):
        """Lấy RTSP URL tốt nhất (ưu tiên /onvif2, sau đó /stream1)."""
        if not self.results.get("rtsp_streams"):
            return None

        # Ưu tiên /onvif2
        for stream in self.results["rtsp_streams"]:
            if "/onvif2" in stream["url"]:
                return stream["url"]

        # Sau đó /stream1
        for stream in self.results["rtsp_streams"]:
            if "/stream1" in stream["url"]:
                return stream["url"]

        # Cuối cùng lấy cái đầu tiên
        return self.results["rtsp_streams"][0]["url"] if self.results["rtsp_streams"] else None


__all__ = ["CameraLinkDiscovery"]
