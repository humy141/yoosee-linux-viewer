from PyQt5.QtWidgets import QDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm camera")
        self.resize(420, 220)

        self.name_input = QLineEdit()
        self.ip_input = QLineEdit()
        self.port_input = QLineEdit("554")
        self.username_input = QLineEdit("admin")
        self.password_input = QLineEdit("admin")
        self.password_input.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Tên camera", self.name_input)
        form.addRow("IP", self.ip_input)
        form.addRow("Port", self.port_input)
        form.addRow("Username", self.username_input)
        form.addRow("Password", self.password_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(btn_layout)

    def values(self):
        return {
            "name": self.name_input.text().strip(),
            "ip": self.ip_input.text().strip(),
            "port": self.port_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
        }
