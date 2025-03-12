import sys
import json
import os
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QColorDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Slot, QTimer, Qt
from PySide6.QtWebChannel import QWebChannel

GITHUB_REPO = "https://raw.githubusercontent.com/danceqqq/Atherium/main/news.json"
CACHE_DIR = ".cache"
IMG_CACHE_DIR = "static/img/cached"
CONFIG_FILE = f"{CACHE_DIR}/config.json"


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игровой Лаунчер")
        self.setGeometry(100, 100, 1280, 720)

        # Убираем стандартную рамку окна
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Создаем WebView для отображения HTML-контента
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        page = self.web_view.page()
        if page:
            settings = page.settings()
            settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)

        self.channel = QWebChannel()
        self.channel.registerObject("pyobject", self)
        self.web_view.page().setWebChannel(self.channel)

        self.show_loading_screen()
        QTimer.singleShot(3000, self.load_main_content)

    def load_main_content(self):
        self.news_data = self.load_news_data(force_update=True)
        self.cache_images()
        html_content = self.generate_html()
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(os.path.abspath("index.html")))

    def show_loading_screen(self):
        config = self.load_config()
        loader_color = config.get("launcher_color", "#562c79")  # Цвет загрузочного экрана

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
                    background: {loader_color};
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

                if not os.path.exists(img_path):
                    try:
                        img_data = requests.get(img_url, timeout=5).content
                        with open(img_path, "wb") as f:
                            f.write(img_data)
                        print(f"Успешно загружено изображение: {img_url}")
                    except Exception as e:
                        print(f"Ошибка загрузки изображения {img_url}: {str(e)}")

    def generate_html(self):
        config = self.load_config()
        nickname = config.get("saved_nickname", "")
        remember_nickname = config.get("remember_nickname", False)
        close_after_launch = config.get("close_after_launch", False)
        launcher_color = config.get("launcher_color", "#562c79")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Игровой Лаунчер</title>
            <link rel="stylesheet" href="file:///{os.path.abspath('static/css/style.css').replace('\\', '/')}">
            <script src="file:///{os.path.abspath('static/js/script.js').replace('\\', '/')}"></script>
            <script src="file:///{os.path.abspath('static/js/color-thief.js').replace('\\', '/')}"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body style="background: {launcher_color};">
            <!-- Верхняя панель -->
            <div class="top-bar">
                <div class="exit-btn" onclick="closeLauncher()">×</div>
            </div>

            <!-- Экран загрузки -->
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

            <!-- Новости -->
            <div class="news-section" style="opacity: 0; transform: translateY(100px);">
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

        html += f"""
                </div>
            </div>

            <!-- Footer -->
            <div class="footer" style="opacity: 0; transform: translateY(50px);">
                <div class="input-group">
                    <input type="text" id="nickname" placeholder="Введите никнейм" value="{nickname}">
                    <button class="btn" onclick="launchGame()">Запустить</button>
                    <button class="btn settings-btn" onclick="toggleSettings()">Настройки ⚙️</button>
                </div>
            </div>

            <!-- Настройки -->
            <div class="settings-menu" style="right: -300px; opacity: 0;">
                <div class="settings-content">
                    <h3>Настройки</h3>
                    <label>
                        <input type="checkbox" id="rememberNickname" class="checkbox" {'checked' if remember_nickname else ''}>
                        Запомнить имя пользователя
                    </label>
                    <br>
                    <label>
                        <input type="checkbox" id="closeAfterLaunch" class="checkbox" {'checked' if close_after_launch else ''}>
                        Закрывать лаунчер после запуска
                    </label>
                    <br><br>
                    <label>
                        Цвет лаунчера
                        <div id="colorPreview" class="color-preview" style="background: {launcher_color};" onclick="openColorPicker()"></div>
                    </label>
                    <button class="btn" onclick="toggleSettings()">Закрыть</button>
                </div>
            </div>

            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    new QWebChannel(qt.webChannelTransport, (channel) => {{
                        window.pyobject = channel.objects.pyobject;
                        initialize();
                    }});

                    // Плавное появление главного меню
                    setTimeout(() => {{
                        document.querySelector('.loader-example').style.display = 'none';
                        document.querySelector('.news-section').style.opacity = '1';
                        document.querySelector('.news-section').style.transform = 'translateY(0)';
                        document.querySelector('.footer').style.opacity = '1';
                        document.querySelector('.footer').style.transform = 'translateY(0)';
                    }}, 3000);

                    // Сохранение конфига
                    function saveConfig() {{
                        const nickname = document.getElementById('nickname').value || '';
                        const remember = document.getElementById('rememberNickname').checked;
                        const closeAfterLaunch = document.getElementById('closeAfterLaunch').checked;
                        const launcherColor = document.getElementById('colorPreview').style.background;
                        window.pyobject.save_to_config(nickname, remember, closeAfterLaunch, launcherColor);
                    }}

                    // Обработчики событий
                    document.getElementById('rememberNickname').addEventListener('change', saveConfig);
                    document.getElementById('closeAfterLaunch').addEventListener('change', saveConfig);
                    document.querySelector('.btn').addEventListener('click', saveConfig);
                }});

                // Закрытие лаунчера
                function closeLauncher() {{
                    window.pyobject.close_launcher();
                }}

                // Выбор цвета
                function openColorPicker() {{
                    window.pyobject.open_color_picker((newColor) => {{
                        document.getElementById('colorPreview').style.background = newColor;
                        document.body.style.background = newColor;
                        saveConfig();
                    }});
                }}
            </script>
        </body>
        </html>
        """
        return html

    @Slot(str, bool, bool, str)
    def save_to_config(self, nickname, remember_nickname, close_after_launch, launcher_color):
        """Сохраняет конфигурацию в config.json"""
        try:
            # Преобразуем цвет в строку, если он не является строкой
            if not isinstance(launcher_color, str):
                launcher_color = self.normalize_color(launcher_color)

            config = {
                "saved_nickname": nickname if remember_nickname else "",
                "remember_nickname": remember_nickname,
                "close_after_launch": close_after_launch,
                "launcher_color": launcher_color
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            print("Конфиг успешно сохранён.")
        except Exception as e:
            print(f"Ошибка сохранения конфига: {str(e)}")

    def normalize_color(self, color):
        """Преобразует цвет в формат #RRGGBB"""
        if isinstance(color, dict):
            # Если цвет передан как объект CSS (например, rgb(r, g, b))
            r, g, b = color.get("r", 0), color.get("g", 0), color.get("b", 0)
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
        elif isinstance(color, str):
            # Если цвет уже строка, возвращаем его без изменений
            return color
        else:
            # Если что-то пошло не так, возвращаем цвет по умолчанию
            return "#562c79"

    def load_config(self):
        """Загружает конфигурацию из config.json"""
        if not os.path.exists(CONFIG_FILE):
            return {
                "saved_nickname": "",
                "remember_nickname": False,
                "close_after_launch": False,
                "launcher_color": "#562c79"
            }

        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Проверка корректности цвета
                if not isinstance(config.get("launcher_color"), str):
                    config["launcher_color"] = "#562c79"
                return config
        except Exception as e:
            print(f"Ошибка чтения конфига: {str(e)}")
            return {
                "saved_nickname": "",
                "remember_nickname": False,
                "close_after_launch": False,
                "launcher_color": "#562c79"
            }

    @Slot(result=str)
    def open_color_picker(self):
        """Открывает диалог выбора цвета и возвращает выбранный цвет"""
        color = QColorDialog.getColor().name()
        return color

    @Slot()
    def close_launcher(self):
        """Закрывает приложение"""
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())