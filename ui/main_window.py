import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QTextEdit,
    QMessageBox,
    QSplitter,
    QFrame,
)

from app.camera_manager import CameraStore, CameraStreamThread
from app.motion_detector import MotionDetector
from app.recorder import Recorder
from ui.camera_dialog import AddCameraDialog
from ui.discovery_dialog import CameraDiscoveryDialog


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.camera_store = CameraStore()
        self.motion_detector = MotionDetector()
        self.recorder = Recorder(output_dir="recordings")
        self.current_camera = None
        self.stream_thread = None
        self.recording = False
        self.motion_enabled = True
        self.events = []
        self.init_ui()
        self.load_cameras()
        self.log_event("Hệ thống sẵn sàng")

    def init_ui(self):
        self.setWindowTitle(f"Yoosee Linux - {self.username}")
        self.resize(1300, 850)

        root = QWidget(self)
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.camera_list = QListWidget()
        self.camera_list.setStyleSheet("font-size: 12px;")
        self.camera_list.itemClicked.connect(self.on_camera_selected)

        add_btn = QPushButton("Thêm camera thủ công")
        add_btn.clicked.connect(self.add_camera)
        
        discovery_btn = QPushButton("Quét tìm camera tự động")
        discovery_btn.clicked.connect(self.discover_cameras)
        discovery_btn.setStyleSheet("background-color: #0d6efd; color: white; font-weight: bold;")

        left_layout.addWidget(QLabel("Danh sách camera"))
        left_layout.addWidget(self.camera_list)
        left_layout.addWidget(discovery_btn)
        left_layout.addWidget(add_btn)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        top_menu = QHBoxLayout()
        menu_items = ["Trang chủ", "Camera", "Video", "Cảnh báo", "Cài đặt"]
        for item in menu_items:
            btn = QPushButton(item)
            btn.setFixedHeight(36)
            top_menu.addWidget(btn)
        right_layout.addLayout(top_menu)

        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)

        self.preview_label = QLabel("Xem trực tiếp")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedHeight(530)
        self.preview_label.setStyleSheet(
            "background: black; color: white; border: 1px solid #333; font-size: 18px;"
        )
        preview_layout.addWidget(self.preview_label)

        right_layout.addWidget(preview_frame)

        toolbar = QHBoxLayout()
        self.start_btn = QPushButton("Bắt đầu")
        self.start_btn.clicked.connect(self.toggle_stream)
        self.record_btn = QPushButton("Ghi video")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.motion_btn = QPushButton("Phát hiện chuyển động: BẬT")
        self.motion_btn.clicked.connect(self.toggle_motion)
        toolbar.addWidget(self.start_btn)
        toolbar.addWidget(self.record_btn)
        toolbar.addWidget(self.motion_btn)
        right_layout.addLayout(toolbar)

        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setStyleSheet("font-weight: bold; color: #0d6efd;")
        right_layout.addWidget(self.status_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Nhật ký sự kiện...")
        self.log_box.setStyleSheet("font-size: 12px;")
        right_layout.addWidget(self.log_box)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        root_layout.addWidget(splitter)

    def log_event(self, message):
        self.events.append(message)
        self.log_box.append(message)

    def load_cameras(self):
        cameras = self.camera_store.list_cameras()
        self.camera_list.clear()
        for camera in cameras:
            item = QListWidgetItem(f"{camera['name']} - {camera['ip']}")
            item.setData(Qt.UserRole, camera)
            self.camera_list.addItem(item)

    def add_camera(self):
        dialog = AddCameraDialog(self)
        if dialog.exec_():
            values = dialog.values()
            if not values["name"] or not values["ip"]:
                QMessageBox.warning(self, "Lỗi", "Tên và IP không được bỏ trống.")
                return
            camera = self.camera_store.add_camera(
                values["name"],
                values["ip"],
                values["port"],
                values["username"],
                values["password"],
            )
            self.log_event(f"Đã thêm camera: {camera['name']} ({camera['ip']})")
            self.load_cameras()

    def discover_cameras(self):
        """Mở dialog để phát hiện camera tự động"""
        dialog = CameraDiscoveryDialog(self)
        dialog.camera_selected.connect(self.on_camera_discovered)
        dialog.exec_()

    def on_camera_discovered(self, camera):
        """Xử lý camera được phát hiện"""
        # Lưu camera
        existing = self.camera_store.list_cameras()
        camera["id"] = len(existing) + 1
        camera["name"] = f"Camera {camera['ip']}"
        
        self.camera_store.add_camera(
            camera["name"],
            camera["ip"],
            str(camera["port"]),
            camera["username"],
            camera["password"],
        )
        
        self.log_event(f"✓ Thêm camera phát hiện: {camera['name']} ({camera['ip']})")
        self.load_cameras()

    def on_camera_selected(self, item):
        self.current_camera = item.data(Qt.UserRole)
        self.status_label.setText(f"Đã chọn: {self.current_camera['name']}")

    def toggle_stream(self):
        if self.current_camera is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn camera trước.")
            return
        if self.stream_thread is not None and self.stream_thread.isRunning():
            self.stream_thread.stop()
            self.stream_thread = None
            self.status_label.setText("Luồng xem đã dừng")
            self.log_event(f"Đã dừng xem {self.current_camera['name']}")
            return

        rtsp_url = self.camera_store.build_rtsp_url(self.current_camera)
        self.stream_thread = CameraStreamThread(rtsp_url)
        self.stream_thread.frame_ready.connect(self.on_frame_ready)
        self.stream_thread.error.connect(self.on_stream_error)
        self.stream_thread.start()
        self.status_label.setText(f"Đang xem: {self.current_camera['name']}")
        self.log_event(f"Bắt đầu xem {self.current_camera['name']}")

    def on_stream_error(self, message):
        self.status_label.setText(message)
        self.log_event(message)

    def on_frame_ready(self, frame):
        if frame is None:
            return

        if self.motion_enabled and self.current_camera is not None:
            motion, _, _ = self.motion_detector.detect(frame)
            if motion:
                self.status_label.setText("Đã phát hiện chuyển động")
                self.log_event(f"[{self.current_camera['name']}] Phát hiện chuyển động")

        if self.recording:
            if self.recorder.writer is None:
                self.recorder.start(self.current_camera['name'], frame)
            self.recorder.write(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(self.preview_label.size(), Qt.KeepAspectRatio)
        self.preview_label.setPixmap(pixmap)

    def toggle_recording(self):
        if self.current_camera is None:
            QMessageBox.warning(self, "Lỗi", "Chọn camera trước khi ghi video.")
            return
        self.recording = not self.recording
        if self.recording:
            self.record_btn.setText("Dừng ghi")
            self.log_event(f"Bắt đầu ghi hình: {self.current_camera['name']}")
        else:
            self.record_btn.setText("Ghi video")
            self.recorder.stop()
            self.log_event(f"Dừng ghi hình: {self.current_camera['name']}")

    def toggle_motion(self):
        self.motion_enabled = not self.motion_enabled
        status = "BẬT" if self.motion_enabled else "TẮT"
        self.motion_btn.setText(f"Phát hiện chuyển động: {status}")
        self.log_event(f"Phát hiện chuyển động: {status}")


__all__ = ["MainWindow"]
