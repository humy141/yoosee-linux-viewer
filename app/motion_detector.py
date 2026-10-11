import cv2
from PyQt5.QtCore import QThread, pyqtSignal


class CameraStreamThread(QThread):
    frame_ready = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            self.error.emit(f"Không thể mở camera: {self.rtsp_url}")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            self.frame_ready.emit(frame)

        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait(2000)
