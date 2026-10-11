import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Yoosee Linux")
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
