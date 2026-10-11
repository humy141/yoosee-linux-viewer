from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout


class PTZDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Điều khiển PTZ")
        self.resize(320, 260)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Điều khiển góc nhìn"))

        grid = QGridLayout()
        self.up_btn = QPushButton("↑")
        self.left_btn = QPushButton("←")
        self.center_btn = QPushButton("●")
        self.right_btn = QPushButton("→")
        self.down_btn = QPushButton("↓")
        self.zoom_in_btn = QPushButton("Zoom +")
        self.zoom_out_btn = QPushButton("Zoom -")

        grid.addWidget(self.up_btn, 0, 1)
        grid.addWidget(self.left_btn, 1, 0)
        grid.addWidget(self.center_btn, 1, 1)
        grid.addWidget(self.right_btn, 1, 2)
        grid.addWidget(self.down_btn, 2, 1)
        grid.addWidget(self.zoom_in_btn, 0, 2)
        grid.addWidget(self.zoom_out_btn, 2, 2)

        layout.addLayout(grid)

        btns = QHBoxLayout()
        ok_btn = QPushButton("Đóng")
        ok_btn.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(ok_btn)
        layout.addLayout(btns)
