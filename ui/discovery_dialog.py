from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from app.link_discovery import CameraLinkDiscovery


class DiscoveryThread(QThread):
    """Thread dò tìm camera không block UI."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, ip, username, password):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password

    def run(self):
        self.progress.emit(f"🔍 Dò tìm camera {self.ip}...")
        discovery = CameraLinkDiscovery(self.ip, self.username, self.password)
        results = discovery.discover_all()
        self.progress.emit(f"✓ Hoàn tất dò tìm")
        self.finished.emit(results)


class CameraDiscoveryDialog(QDialog):
    """Dialog dò tìm camera và chọn RTSP stream."""

    camera_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dò tìm camera")
        self.resize(500, 400)
        self.discovery_results = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Input fields
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP Camera:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.4")
        ip_layout.addWidget(self.ip_input)
        layout.addLayout(ip_layout)

        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit()
        self.user_input.setText("admin")
        user_layout.addWidget(self.user_input)
        layout.addLayout(user_layout)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit()
        self.pass_input.setText("admin")
        self.pass_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.pass_input)
        layout.addLayout(pass_layout)

        # Scan button
        scan_btn = QPushButton("🔍 Dò tìm camera")
        scan_btn.clicked.connect(self.start_discovery)
        layout.addWidget(scan_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("Sẵn sàng")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def start_discovery(self):
        ip = self.ip_input.text().strip()
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not ip:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập IP camera")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        self.status_label.setText("Đang dò tìm...")

        self.thread = DiscoveryThread(ip, username, password)
        self.thread.progress.connect(self.on_progress)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_progress(self, message):
        self.status_label.setText(message)

    def on_finished(self, results):
        self.discovery_results = results
        self.progress_bar.setVisible(False)

        rtsp_streams = results.get("rtsp_streams", [])
        if rtsp_streams:
            self.status_label.setText(
                f"✓ Tìm thấy {len(rtsp_streams)} RTSP stream. Nhấn OK để chọn."
            )
            # Emit camera info
            camera_info = {
                "ip": results["camera_ip"],
                "name": f"Camera {results['camera_ip']}",
                "username": results["username"],
                "port": 554,
                "rtsp_url": rtsp_streams[0]["url"],
            }
            self.camera_selected.emit(camera_info)
        else:
            self.status_label.setText("✗ Không tìm thấy stream. Kiểm tra IP, user, password.")
            QMessageBox.warning(
                self, "Lỗi", "Không tìm thấy stream RTSP trên camera này."
            )


__all__ = ["CameraDiscoveryDialog"]
