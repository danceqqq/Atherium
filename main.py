import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Slot
from PySide6.QtWebChannel import QWebChannel
import os


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игровой Лаунчер")
        self.setGeometry(100, 100, 1280, 720)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # Инициализация канала связи
        self.channel = QWebChannel()
        self.channel.registerObject("pyobject", self)
        self.web_view.page().setWebChannel(self.channel)

        # Загрузка HTML из файла с правильным базовым URL
        html_path = os.path.abspath("templates/index.html")
        self.web_view.load(QUrl.fromLocalFile(html_path))

    @Slot(str)
    def launchGame(self, nickname):
        print(f"Запуск игры с ником: {nickname}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())