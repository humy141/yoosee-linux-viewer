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
)

from app.camera_manager import CameraStore, CameraStreamThread
from app.motion_detector import MotionDetector
from app.recorder import Recorder
from ui.camera_dialog import AddCameraDialog


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
        self.init_ui()
        self.load_cameras()

    def init_ui(self):
        self.setWindowTitle(f"Yoosee Linux - {self.username}")
        self.resize(1200, 800)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        self.camera_list = QListWidget()
        self.camera_list.itemClicked.connect(self.on_camera_selected)
        left_layout.addWidget(self.camera_list)

        add_btn = QPushButton("Thêm camera")
        add_btn.clicked.connect(self.add_camera)
        left_layout.addWidget(add_btn)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.preview_label = QLabel("Camera preview")
        self.preview_label.setFixedHeight(500)
        self.preview_label.setStyleSheet("background: black; color: white; border: 1px solid #222;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.preview_label)

        toolbar = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.toggle_stream)
        self.record_btn = QPushButton("Ghi video")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.motion_btn = QPushButton("Motion ON")
        self.motion_btn.clicked.connect(self.toggle_motion)
        toolbar.addWidget(self.start_btn)
        toolbar.addWidget(self.record_btn)
        toolbar.addWidget(self.motion_btn)
        right_layout.addLayout(toolbar)

        self.status_label = QLabel("Sẵn sàng")
        right_layout.addWidget(self.status_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        right_layout.addWidget(self.log_box)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        layout.addWidget(splitter)

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
            self.log_box.append(f"Đã thêm camera: {camera['name']} ({camera['ip']})")
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
            self.status_label.setText("Stream đã dừng")
            return

        rtsp_url = self.camera_store.build_rtsp_url(self.current_camera)
        self.stream_thread = CameraStreamThread(rtsp_url)
        self.stream_thread.frame_ready.connect(self.on_frame_ready)
        self.stream_thread.error.connect(self.on_stream_error)
        self.stream_thread.start()
        self.status_label.setText(f"Đang phát: {self.current_camera['name']}")

    def on_stream_error(self, message):
        self.status_label.setText(message)
        self.log_box.append(message)

    def on_frame_ready(self, frame):
        if frame is None:
            return

        if self.motion_enabled and self.current_camera is not None:
            motion, contours, _ = self.motion_detector.detect(frame)
            if motion:
                self.status_label.setText("Phát hiện chuyển động")
                self.log_box.append(f"[{self.current_camera['name']}] Phát hiện chuyển động")

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
            self.log_box.append(f"Bắt đầu ghi hình: {self.current_camera['name']}")
        else:
            self.record_btn.setText("Ghi video")
            self.recorder.stop()
            self.log_box.append(f"Dừng ghi hình: {self.current_camera['name']}")

    def toggle_motion(self):
        self.motion_enabled = not self.motion_enabled
        self.motion_btn.setText("Motion ON" if self.motion_enabled else "Motion OFF")
        self.log_box.append(f"Motion detection: {'ON' if self.motion_enabled else 'OFF'}")
