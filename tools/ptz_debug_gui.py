import sys
import json
import threading
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QCheckBox,
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt


class PTZDiscoveryThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, ip, username, password, ports=None):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
        self.ports = ports or [80, 8080, 8000, 8888, 554, 81]
        self.results = {}

    def run(self):
        self.log.emit(f"🔍 Bắt đầu quét PTZ cho camera {self.ip}...\n")
        self.log.emit(f"Username: {self.username}\n")
        self.log.emit(f"Password: ****** (có dấu #)\n")
        self.log.emit(f"Ports sẽ quét: {self.ports}\n")
        self.log.emit("="*60 + "\n")
        
        # Quét ONVIF endpoints
        self.log.emit("\n[1] Quét ONVIF Device Service...\n")
        onvif_results = self.scan_onvif_endpoints()
        self.results["onvif"] = onvif_results
        
        # Quét ONVIF Media Service
        self.log.emit("\n[2] Quét ONVIF Media Service...\n")
        media_results = self.scan_onvif_media()
        self.results["media"] = media_results
        
        # Quét ONVIF PTZ Service
        self.log.emit("\n[3] Quét ONVIF PTZ Service...\n")
        ptz_results = self.scan_onvif_ptz()
        self.results["ptz"] = ptz_results
        
        # Quét CGI endpoints
        self.log.emit("\n[4] Quét CGI endpoints...\n")
        cgi_results = self.scan_cgi_endpoints()
        self.results["cgi"] = cgi_results
        
        # Tóm tắt
        self.log.emit("\n" + "="*60)
        self.log.emit("📊 TÓM TẮT KẾT QUẢ QUÉT\n")
        
        found_any = False
        for service_type, results in self.results.items():
            for result in results:
                if result.get("found"):
                    found_any = True
                    self.log.emit(f"✓ {service_type.upper()}: {result['url']}")
        
        if not found_any:
            self.log.emit("⚠ Không tìm thấy endpoint PTZ nào.\n")
            self.log.emit("Gợi ý:\n")
            self.log.emit("1. Kiểm tra username/password có đúng không\n")
            self.log.emit("2. Kiểm tra camera có bật ONVIF không\n")
            self.log.emit("3. Thử các port khác (8080, 8000, v.v.)\n")
        
        self.finished.emit(self.results)

    def scan_onvif_endpoints(self):
        endpoints = [
            "/onvif/device_service",
            "/onvif/DeviceService",
            "/onvif/device",
            "/onvif/Device",
        ]
        results = []
        for port in self.ports:
            for endpoint in endpoints:
                url = f"http://{self.ip}:{port}{endpoint}"
                if self.test_endpoint(url):
                    self.log.emit(f"✓ Tìm thấy: {url}\n")
                    results.append({"url": url, "found": True, "type": "onvif_device"})
        return results

    def scan_onvif_media(self):
        endpoints = [
            "/onvif/media_service",
            "/onvif/MediaService",
            "/onvif/media",
            "/onvif/Media",
        ]
        results = []
        for port in self.ports:
            for endpoint in endpoints:
                url = f"http://{self.ip}:{port}{endpoint}"
                if self.test_endpoint(url):
                    self.log.emit(f"✓ Tìm thấy: {url}\n")
                    results.append({"url": url, "found": True, "type": "onvif_media"})
        return results

    def scan_onvif_ptz(self):
        endpoints = [
            "/onvif/ptz_service",
            "/onvif/PTZService",
            "/onvif/ptz",
            "/onvif/PTZ",
        ]
        results = []
        for port in self.ports:
            for endpoint in endpoints:
                url = f"http://{self.ip}:{port}{endpoint}"
                if self.test_endpoint(url):
                    self.log.emit(f"✓ TÌM THẤY PTZ: {url}\n")
                    results.append({"url": url, "found": True, "type": "onvif_ptz"})
        return results

    def scan_cgi_endpoints(self):
        endpoints = [
            "/cgi-bin/ptz.cgi",
            "/cgi-bin/ptz",
            "/cgi-bin/ptzControl.cgi",
            "/cgi-bin/ptzControl",
            "/cgi-bin/camera.cgi",
            "/cgi-bin/api/ptz",
            "/api/ptz",
            "/ptz",
        ]
        results = []
        for port in self.ports:
            for endpoint in endpoints:
                url = f"http://{self.ip}:{port}{endpoint}"
                if self.test_endpoint(url):
                    self.log.emit(f"✓ Tìm thấy: {url}\n")
                    results.append({"url": url, "found": True, "type": "cgi"})
        return results

    def test_endpoint(self, url):
        try:
            resp = requests.get(
                url,
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=3,
                verify=False,
            )
            return resp.status_code in [200, 401, 403, 405]
        except Exception:
            return False


class PTZDebugGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.thread = None

    def init_ui(self):
        self.setWindowTitle("PTZ Discovery Tool - FNKVision SEA-U2")
        self.resize(800, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tiêu đề
        title = QLabel("🔍 Công cụ tìm kiếm endpoint PTZ")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Input fields
        input_layout = QVBoxLayout()
        
        # IP
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP Camera:"))
        self.ip_input = QLineEdit("192.168.1.4")
        ip_layout.addWidget(self.ip_input)
        input_layout.addLayout(ip_layout)
        
        # Username
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit("admin")
        user_layout.addWidget(self.user_input)
        input_layout.addLayout(user_layout)
        
        # Password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit("admin123#")
        self.pass_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.pass_input)
        input_layout.addLayout(pass_layout)
        
        # Ports
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Ports (cách nhau bằng dấu phẩy):"))
        self.port_input = QLineEdit("80,8080,8000,8888,554,81")
        port_layout.addWidget(self.port_input)
        input_layout.addLayout(port_layout)
        
        layout.addLayout(input_layout)
        
        # Nút quét
        scan_btn = QPushButton("🚀 Bắt đầu quét PTZ")
        scan_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px;")
        scan_btn.clicked.connect(self.start_scan)
        layout.addWidget(scan_btn)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Log output
        layout.addWidget(QLabel("📋 Nhật ký quét:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.log_output)
        
        # Nút lưu
        save_btn = QPushButton("💾 Lưu kết quả vào file JSON")
        save_btn.clicked.connect(self.save_results)
        layout.addWidget(save_btn)

    def start_scan(self):
        ip = self.ip_input.text().strip()
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        ports_str = self.port_input.text().strip()
        
        try:
            ports = [int(p.strip()) for p in ports_str.split(",")]
        except ValueError:
            self.log_output.setText("❌ Lỗi: Ports phải là số, cách nhau bằng dấu phẩy\n")
            return
        
        if not ip:
            self.log_output.setText("❌ Lỗi: Vui lòng nhập IP camera\n")
            return
        
        self.log_output.clear()
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.thread = PTZDiscoveryThread(ip, username, password, ports)
        self.thread.log.connect(self.append_log)
        self.thread.finished.connect(self.scan_finished)
        self.thread.start()

    def append_log(self, message):
        self.log_output.insertPlainText(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def scan_finished(self, results):
        self.progress.setVisible(False)
        self.results = results
        self.log_output.insertPlainText("\n✅ Quét hoàn tất!\n")

    def save_results(self):
        if not hasattr(self, "results"):
            self.log_output.insertPlainText("❌ Chưa có kết quả quét. Hãy quét trước.\n")
            return
        
        filename = "ptz_discovery_report.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.log_output.insertPlainText(f"\n💾 Kết quả đã lưu vào: {filename}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PTZDebugGUI()
    window.show()
    sys.exit(app.exec_())
