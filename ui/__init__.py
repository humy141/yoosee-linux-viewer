import os
from datetime import datetime

import cv2


class Recorder:
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.writer = None
        self.current_file = None

    def start(self, camera_name, frame):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{camera_name}_{timestamp}.mp4"
        self.current_file = os.path.join(self.output_dir, file_name)
        height, width, _ = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.current_file, fourcc, 20.0, (width, height))

    def write(self, frame):
        if self.writer is not None:
            self.writer.write(frame)

    def stop(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
