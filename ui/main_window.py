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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2

from app.camera_manager import CameraStore
from app.camera_stream import CameraStreamThread
from app.motion_detector import MotionDetector
from app.recorder import Recorder
from app.ptz_manager import ONVIFPTZManager
from ui.camera_dialog import AddCameraDialog
from ui.discovery_dialog import CameraDiscoveryDialog
from ui.ptz_dialog import PTZDialog
