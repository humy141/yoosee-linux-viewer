import threading
import cv2
from PyQt5.QtCore import pyqtSignal, QThread


class CameraStreamThread(QThread):
    """Thread xem stream camera RTSP với error handling."""

    frame_ready = pyqtSignal(object)  # Emit frame khi có data
    error = pyqtSignal(str)  # Emit error message
    connected = pyqtSignal(bool)  # True/False khi connect/disconnect

    def __init__(self, rtsp_url, buffer_size=1):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.buffer_size = buffer_size
        self.running = False
        self.cap = None
        self.reconnect_attempts = 0
        self.max_reconnect = 5

    def run(self):
        self.running = True
        self.reconnect_attempts = 0

        while self.running and self.reconnect_attempts < self.max_reconnect:
            try:
                self.cap = cv2.VideoCapture(self.rtsp_url)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)

                # Kiểm tra có kết nối được không
                if not self.cap.isOpened():
                    raise Exception("Không thể mở stream")

                self.connected.emit(True)
                self.reconnect_attempts = 0

                # Đọc frame
                while self.running:
                    ret, frame = self.cap.read()
                    if not ret:
                        raise Exception("Không thể đọc frame")
                    self.frame_ready.emit(frame)

            except Exception as e:
                self.reconnect_attempts += 1
                self.connected.emit(False)
                error_msg = f"Lỗi stream: {str(e)} (Lần {self.reconnect_attempts}/{self.max_reconnect})"
                self.error.emit(error_msg)

                if self.cap:
                    self.cap.release()

                # Chờ trước khi reconnect
                if self.running and self.reconnect_attempts < self.max_reconnect:
                    self.msleep(2000)

        if self.reconnect_attempts >= self.max_reconnect:
            self.error.emit("Không thể kết nối camera sau nhiều lần thử")
            self.connected.emit(False)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()


__all__ = ["CameraStreamThread"]
