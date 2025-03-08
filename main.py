import sys
import subprocess
import json
import os
import requests
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Slot, QTimer
from PySide6.QtWebChannel import QWebChannel

GITHUB_REPO = "https://raw.githubusercontent.com/danceqqq/Atherium/main/news.json"
CACHE_DIR = ".cache"
IMG_CACHE_DIR = "static/img/cached"


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игровой Лаунчер")
        self.setGeometry(100, 100, 1280, 720)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # Настройки WebView через страницу
        page = self.web_view.page()
        if page:
            settings = page.settings()
            # Включаем JavaScript
            settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)

        self.channel = QWebChannel()
        self.channel.registerObject("pyobject", self)
        self.web_view.page().setWebChannel(self.channel)

        # Показываем экран загрузки
        self.show_loading_screen()

        # Загружаем данные через 3 секунды
        QTimer.singleShot(3000, self.load_main_content)

    def load_main_content(self):
        self.news_data = self.load_news_data(force_update=True)
        self.cache_images()
        html_content = self.generate_html()
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(os.path.abspath("index.html")))

    def show_loading_screen(self):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Загрузка</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: #562c79;
                }}
                .loader-example {{
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                }}
                .loader-block {{
                    position: relative;
                    width: 4rem;
                    height: 4rem;
                }}
                .loader-item {{
                    position: absolute;
                    width: 2rem;
                    height: 2rem;
                    background: white;
                    animation: move 0.5s linear infinite;
                    border-radius: 50%;
                }}
                @keyframes move {{
                    0% {{ opacity: 0; }}
                    10% {{ opacity: 1; }}
                    70% {{ opacity: 0; }}
                    100% {{ opacity: 0; }}
                }}
                /* Позиции элементов */
                .loader-item:nth-of-type(1) {{ top: -2rem; left: -2rem; }}
                .loader-item:nth-of-type(2) {{ top: -2rem; left: 0; animation-delay: -0.0625s; }}
                .loader-item:nth-of-type(3) {{ top: -2rem; left: 2rem; animation-delay: -0.125s; }}
                .loader-item:nth-of-type(4) {{ top: 0; left: 2rem; animation-delay: -0.1875s; }}
                .loader-item:nth-of-type(5) {{ top: 2rem; left: 2rem; animation-delay: -0.25s; }}
                .loader-item:nth-of-type(6) {{ top: 2rem; left: 0; animation-delay: -0.3125s; }}
                .loader-item:nth-of-type(7) {{ top: 2rem; left: -2rem; animation-delay: -0.375s; }}
                .loader-item:nth-of-type(8) {{ top: 0; left: -2rem; animation-delay: -0.4375s; }}
            </style>
        </head>
        <body>
            <div class="loader-example">
                <div class="loader-block">
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                </div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)

    def load_news_data(self, force_update=False):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        cached_data = []
        new_data = []

        try:
            response = requests.get(GITHUB_REPO, timeout=5)
            response.raise_for_status()
            new_data = response.json()
            print("Успешно загружено с GitHub:", new_data)
        except Exception as e:
            print(f"Ошибка загрузки с GitHub: {str(e)}")

        if force_update or new_data != cached_data:
            try:
                with open(f"{CACHE_DIR}/news.json", "w") as f:
                    json.dump(new_data, f)
                cached_data = new_data
            except Exception as e:
                print(f"Ошибка записи кэша: {str(e)}")
        else:
            try:
                with open(f"{CACHE_DIR}/news.json", "r") as f:
                    cached_data = json.load(f)
            except:
                pass

        return new_data if new_data else cached_data

    def cache_images(self):
        if not os.path.exists(IMG_CACHE_DIR):
            os.makedirs(IMG_CACHE_DIR)

        for item in self.news_data:
            img_url = item.get("image_url", "")
            if img_url:
                img_name = os.path.basename(img_url)
                img_path = os.path.join(IMG_CACHE_DIR, img_name)

                try:
                    img_data = requests.get(img_url, timeout=5).content
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    print(f"Успешно загружено изображение: {img_url}")
                except Exception as e:
                    print(f"Ошибка загрузки изображения {img_url}: {str(e)}")

    def generate_html(self):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Игровой Лаунчер</title>
            <link rel="stylesheet" href="file:///{os.path.abspath('static/css/style.css').replace('\\', '/')}">
        </head>
        <body>
            <div class="loader-example">
                <div class="loader-block">
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                    <div class="loader-item"></div>
                </div>
            </div>
            <div class="news-section" style="display: none;">
                <h2>Новости и релизы</h2>
                <div class="news-grid">
        """

        for item in self.news_data:
            img_url = item.get("image_url", "")
            if img_url:
                img_name = os.path.basename(img_url)
                img_path = os.path.abspath(os.path.join(IMG_CACHE_DIR, img_name)).replace("\\", "/")
                if os.path.exists(img_path):
                    html += f"""
                    <div class="news-card" style="background-image: url('file:///{img_path}');">
                        <div class="news-content">
                            <h3>{item.get('title', 'Нет заголовка')}</h3>
                            <p>{item.get('text', 'Нет описания')}</p>
                        </div>
                    </div>
                    """
                else:
                    print(f"Ошибка: Файл не найден: {img_path}")
            else:
                print(f"Ошибка: Отсутствует image_url в записи: {item}")

        html += """
                </div>
            </div>
            <div class="footer" style="display: none;">
                <div class="input-group">
                    <input type="text" id="nickname" placeholder="Введите никнейм">
                    <button class="btn" onclick="launchGame()">Запустить</button>
                </div>
            </div>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script src="file:///{os.path.abspath('static/js/script.js').replace('\\', '/')}"></script>
            <script src="file:///{os.path.abspath('static/js/color-thief.js').replace('\\', '/')}"></script>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    new QWebChannel(qt.webChannelTransport, (channel) => {
                        window.pyobject = channel.objects.pyobject;
                        initialize();
                    });

                    // Скрываем лоадер и показываем меню через 3 секунды
                    setTimeout(() => {
                        document.querySelector('.loader-example').style.display = 'none';
                        document.querySelector('.news-section').style.display = 'flex';
                        document.querySelector('.footer').style.display = 'flex';
                    }, 3000);
                });
            </script>
        </body>
        </html>
        """
        return html

    @Slot(str)
    def launchGame(self, nickname):
        print(f"Запуск игры с ником: {nickname}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())