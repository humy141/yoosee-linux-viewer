from PyQt5.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox

from ui.main_window import MainWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yoosee Linux - Đăng nhập")
        self.resize(420, 250)

        container = QWidget(self)
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        title = QLabel("Yoosee Linux")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        self.user_input = QLineEdit("admin")
        self.pass_input = QLineEdit("admin")
        self.pass_input.setEchoMode(QLineEdit.Password)
        form.addRow("Tài khoản", self.user_input)
        form.addRow("Mật khẩu", self.pass_input)
        layout.addLayout(form)

        btn = QPushButton("Đăng nhập")
        btn.clicked.connect(self.login)
        layout.addWidget(btn)

    def login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        if username and password:
            self.close()
            self.main = MainWindow(username)
            self.main.show()
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập thông tin đăng nhập.")
