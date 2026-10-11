from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QTextEdit,
    QLineEdit,
    QFormLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from app.camera_discovery import AsyncCameraDiscovery


class DiscoveryThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, username="admin", password="admin"):
        super().__init__()
        self.username = username
        self.password = password
        self.discovery = None

    def run(self):
        self.discovery = AsyncCameraDiscovery(
            self.username,
            self.password,
            self.log.emit
        )
        self.discovery.start()
        self.discovery.join()
        self.finished.emit(self.discovery.result)


class CameraDiscoveryDialog(QDialog):
    """Dialog để phát hiện camera tự động"""
    
    camera_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tìm kiếm camera tự động")
        self.resize(550, 500)
        self.discovered_cameras = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Cấu hình
        config_layout = QFormLayout()
        self.username_input = QLineEdit("admin")
        self.password_input = QLineEdit("admin")
        self.password_input.setEchoMode(QLineEdit.Password)
        config_layout.addRow("Username", self.username_input)
        config_layout.addRow("Mật khẩu", self.password_input)
        layout.addLayout(config_layout)

        # Nút scan
        scan_btn = QPushButton("Scan mạng để tìm camera")
        scan_btn.clicked.connect(self.start_discovery)
        layout.addWidget(scan_btn)

        # Log
        layout.addWidget(QLabel("Quá trình tìm kiếm:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.log_box)

        # Danh sách camera được phát hiện
        layout.addWidget(QLabel("Camera được phát hiện:"))
        self.camera_list = QListWidget()
        self.camera_list.itemClicked.connect(self.on_camera_selected)
        layout.addWidget(self.camera_list)

        # Nút hành động
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Chọn camera")
        select_btn.clicked.connect(self.select_camera)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def start_discovery(self):
        username = self.username_input.text().strip() or "admin"
        password = self.password_input.text().strip() or "admin"
        
        self.log_box.clear()
        self.log_box.append("Bắt đầu tìm kiếm camera trên mạng...")
        
        self.discovery_thread = DiscoveryThread(username, password)
        self.discovery_thread.log.connect(self.on_log)
        self.discovery_thread.finished.connect(self.on_discovery_finished)
        self.discovery_thread.start()

    def on_log(self, message):
        self.log_box.append(message)

    def on_discovery_finished(self, cameras):
        self.discovered_cameras = cameras
        self.camera_list.clear()
        
        if cameras:
            self.log_box.append(f"\n✓ Tìm thấy {len(cameras)} camera")
            for cam in cameras:
                item_text = f"{cam['name']} ({cam['ip']}:{cam['port']}) - {cam['type']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, cam)
                self.camera_list.addItem(item)
        else:
            self.log_box.append("\n✗ Không tìm thấy camera nào")

    def on_camera_selected(self, item):
        self.current_camera = item.data(Qt.UserRole)

    def select_camera(self):
        if hasattr(self, 'current_camera'):
            self.camera_selected.emit(self.current_camera)
            self.accept()
