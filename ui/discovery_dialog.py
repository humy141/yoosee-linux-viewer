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
    QComboBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from app.camera_discovery import AsyncCameraDiscovery, CameraDiscovery


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
    """Dialog để phát hiện camera tự động, tối ưu cho FNKVision SEA-U2"""
    
    camera_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tìm kiếm camera tự động (FNKVision SEA-U2)")
        self.resize(600, 550)
        self.discovered_cameras = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tiêu đề
        title = QLabel("Quét mạng để tìm camera FNKVision SEA-U2")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Cấu hình
        config_layout = QFormLayout()
        
        # Preset credentials cho FNKVision
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("admin / admin", ("admin", "admin"))
        self.preset_combo.addItem("admin / 12345", ("admin", "12345"))
        self.preset_combo.addItem("root / admin", ("root", "admin"))
        self.preset_combo.addItem("Nhập tùy chỉnh", None)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        config_layout.addRow("Credential FNKVision", self.preset_combo)
        
        self.username_input = QLineEdit("admin")
        self.username_input.setEnabled(False)
        config_layout.addRow("Username (tùy chỉnh)", self.username_input)
        
        self.password_input = QLineEdit("admin")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setEnabled(False)
        config_layout.addRow("Mật khẩu (tùy chỉnh)", self.password_input)
        
        layout.addLayout(config_layout)

        # Nút scan
        scan_btn = QPushButton("🔍 Bắt đầu quét mạng")
        scan_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        scan_btn.clicked.connect(self.start_discovery)
        layout.addWidget(scan_btn)

        # Log
        layout.addWidget(QLabel("Quá trình quét:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("font-size: 11px; font-family: monospace;")
        self.log_box.setPlaceholderText("Nhấn 'Bắt đầu quét mạng' để tìm camera...")
        layout.addWidget(self.log_box)

        # Danh sách camera được phát hiện
        layout.addWidget(QLabel("Camera được phát hiện:"))
        self.camera_list = QListWidget()
        self.camera_list.itemClicked.connect(self.on_camera_selected)
        layout.addWidget(self.camera_list)

        # Nút hành động
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("✓ Chọn camera")
        select_btn.setStyleSheet("background-color: #0d6efd; color: white;")
        select_btn.clicked.connect(self.select_camera)
        cancel_btn = QPushButton("✕ Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def on_preset_changed(self, index):
        data = self.preset_combo.currentData()
        if data is None:
            self.username_input.setEnabled(True)
            self.password_input.setEnabled(True)
        else:
            self.username_input.setText(data[0])
            self.password_input.setText(data[1])
            self.username_input.setEnabled(False)
            self.password_input.setEnabled(False)

    def start_discovery(self):
        username = self.username_input.text().strip() or "admin"
        password = self.password_input.text().strip() or "admin"
        
        self.log_box.clear()
        self.log_box.append("═" * 60)
        self.log_box.append("🔍 BẮT ĐẦU QUÉT MẠNG TÌM CAMERA FNKVISION SEA-U2")
        self.log_box.append("═" * 60)
        self.log_box.append(f"Username: {username}")
        self.log_box.append(f"Thời gian quét: ~2-3 phút (tùy kích thước mạng)")
        self.log_box.append("─" * 60)
        
        self.discovery_thread = DiscoveryThread(username, password)
        self.discovery_thread.log.connect(self.on_log)
        self.discovery_thread.finished.connect(self.on_discovery_finished)
        self.discovery_thread.start()

    def on_log(self, message):
        self.log_box.append(message)
        # Tự động scroll xuống
        scrollbar = self.log_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_discovery_finished(self, cameras):
        self.discovered_cameras = cameras
        self.camera_list.clear()
        
        self.log_box.append("═" * 60)
        if cameras:
            self.log_box.append(f"✓ TÌM THẤY {len(cameras)} CAMERA")
            self.log_box.append("═" * 60)
            for idx, cam in enumerate(cameras, 1):
                self.log_box.append(f"{idx}. {cam['name']} ({cam['ip']}:{cam['port']})")
                self.log_box.append(f"   - Type: {cam['type']}")
                self.log_box.append(f"   - URL: {cam['rtsp_url']}")
                item_text = f"{cam['name']} - {cam['ip']}:{cam['port']} ({cam['type']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, cam)
                self.camera_list.addItem(item)
        else:
            self.log_box.append("✗ KHÔNG TÌM THẤY CAMERA NÀO")
            self.log_box.append("═" * 60)
            self.log_box.append("\nGợi ý:")
            self.log_box.append("1. Kiểm tra camera và máy Linux có cùng mạng không")
            self.log_box.append("2. Thử đổi credential (password mặc định có thể khác)")
            self.log_box.append("3. Kiểm tra camera có bật RTSP stream không")
            self.log_box.append("4. Nếu vẫn không tìm thấy, thêm camera thủ công")

    def on_camera_selected(self, item):
        self.current_camera = item.data(Qt.UserRole)

    def select_camera(self):
        if hasattr(self, 'current_camera'):
            self.camera_selected.emit(self.current_camera)
            self.accept()
