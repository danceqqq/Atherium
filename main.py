import sys
import json
import os
import random
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QColorDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Slot, QTimer, Qt
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

GITHUB_REPO = "https://raw.githubusercontent.com/danceqqq/Atherium/main/news.json"
CACHE_DIR = ".cache"
IMG_CACHE_DIR = "static/img/cached"
MUSIC_DIR = "music"
CONFIG_FILE = f"{CACHE_DIR}/config.json"


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игровой Лаунчер")
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Медиаплеер
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self.handle_media_status)

        # Создаем WebView
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # WebChannel
        self.channel = QWebChannel()
        self.channel.registerObject("pyobject", self)
        self.web_view.page().setWebChannel(self.channel)

        self.show_loading_screen()
        QTimer.singleShot(3000, self.load_main_content)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            QTimer.singleShot(0, self.load_random_music)

    def load_random_music(self):
        if os.path.exists(MUSIC_DIR):
            music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
            if music_files:
                random_music = random.choice(music_files)
                self.music_path = os.path.abspath(os.path.join(MUSIC_DIR, random_music))
                self.player.setSource(QUrl.fromLocalFile(self.music_path))
                self.player.play()

    def load_main_content(self):
        self.news_data = self.load_news_data(force_update=True)
        self.cache_images()
        html_content = self.generate_html()
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(os.path.abspath("index.html")))

        # Запуск музыки после загрузки
        QTimer.singleShot(2000, self.start_music)

    def show_loading_screen(self):
        config = self.load_config()
        loader_color = config.get("launcher_color", "#562c79")

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
                .loader {{
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    z-index: 100;
                }}
                .loader-item {{
                    width: 80px;
                    height: 80px;
                    background: white;
                    border-radius: 50%;
                    animation: pulse 1s infinite;
                }}
                @keyframes pulse {{
                    0% {{ transform: scale(0.8); opacity: 0.5; }}
                    50% {{ transform: scale(1); opacity: 1; }}
                    100% {{ transform: scale(0.8); opacity: 0.5; }}
            </style>
        </head>
        <body>
            <div class="loader">
                <div class="loader-item"></div>
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
        except Exception as e:
            print(f"Ошибка загрузки новостей: {str(e)}")

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
            except Exception as e:
                print(f"Ошибка чтения кэша: {str(e)}")

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
                    except Exception as e:
                        print(f"Ошибка загрузки изображения {img_url}: {str(e)}")

    def generate_html(self):
        config = self.load_config()
        nickname = config.get("saved_nickname", "")
        remember = config.get("remember_nickname", False)
        close_after = config.get("close_after_launch", False)
        volume = config.get("music_volume", 50)
        color = config.get("launcher_color", "#562c79")

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
        <body style="background: {color};">
            <!-- Верхняя панель -->
            <div class="top-bar">
                <div class="exit-btn" onclick="closeLauncher()">×</div>
            </div>

            <!-- Новости -->
            <div class="news-section">
                <h2>Новости и релизы</h2>
                <div class="news-grid">
        """

        if not self.news_data:
            html += "<p>Нет новостей</p>"
        else:
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
                        html += "<div class='news-card'><p>Ошибка загрузки изображения</p></div>"
                else:
                    html += "<div class='news-card'><p>Отсутствует image_url</p></div>"

        html += f"""
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="input-group">
                    <input type="text" id="nickname" placeholder="Введите никнейм" value="{nickname}">
                    <button class="btn" onclick="launchGame()">Запустить</button>
                    <button class="btn settings-btn" onclick="toggleSettings()">Настройки ⚙️</button>
                </div>
            </div>

            <!-- Настройки -->
            <div class="settings-menu">
                <div class="settings-content">
                    <h3>Настройки</h3>
                    <label>
                        <input type="checkbox" id="rememberNickname" class="checkbox" {'checked' if remember else ''}>
                        Запомнить ник
                    </label>
                    <br>
                    <label>
                        <input type="checkbox" id="closeAfterLaunch" class="checkbox" {'checked' if close_after else ''}>
                        Закрывать после запуска
                    </label>
                    <br><br>
                    <label>
                        Громкость
                        <input type="range" id="volumeSlider" min="0" max="100" value="{volume}">
                    </label>
                    <br><br>
                    <label>
                        Цвет фона
                        <div id="colorPreview" class="color-preview" style="background: {color};" onclick="openColorPicker()"></div>
                    </label>
                    <button class="btn" onclick="toggleSettings()">Закрыть</button>
                </div>
            </div>

            <script>
                new QWebChannel(qt.webChannelTransport, (channel) => {{
                    window.pyobject = channel.objects.pyobject;
                    initialize();
                }});

                // Скрытие загрузочного экрана
                setTimeout(() => {{
                    document.querySelector('.loader')?.remove();
                }}, 3000);

                // Сохранение конфига
                function saveConfig() {{
                    const nickname = document.getElementById('nickname').value || '';
                    const remember = document.getElementById('rememberNickname').checked;
                    const closeAfter = document.getElementById('closeAfterLaunch').checked;
                    const volume = document.getElementById('volumeSlider').value;
                    const color = document.getElementById('colorPreview').style.background;
                    window.pyobject.save_to_config(nickname, remember, closeAfter, volume, color);
                }}

                // Обработчики
                document.getElementById('volumeSlider')?.addEventListener('input', (e) => {{
                    window.pyobject.set_music_volume(e.target.value);
                    saveConfig();
                }});
                document.getElementById('rememberNickname')?.addEventListener('change', saveConfig);
                document.getElementById('closeAfterLaunch')?.addEventListener('change', saveConfig);
                document.querySelector('.btn')?.addEventListener('click', saveConfig);

                function closeLauncher() {{
                    window.pyobject.close_launcher();
                }}

                function launchGame() {{
                    const nickname = document.getElementById('nickname').value || 'Гость';
                    const closeAfter = document.getElementById('closeAfterLaunch').checked;
                    window.pyobject.launchGame(nickname, closeAfter);
                }}

                function toggleSettings() {{
                    const menu = document.querySelector('.settings-menu');
                    menu.classList.toggle('visible');
                    saveConfig();
                }}

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

    @Slot(str, bool, bool, int, str)
    def save_to_config(self, nickname, remember, close_after, volume, color):
        try:
            config = {
                "saved_nickname": nickname if remember else "",
                "remember_nickname": remember,
                "close_after_launch": close_after,
                "music_volume": int(volume),
                "launcher_color": color
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {str(e)}")

    @Slot(int)
    def set_music_volume(self, volume):
        self.audio_output.setVolume(int(volume) / 100)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {
                "saved_nickname": "",
                "remember_nickname": False,
                "close_after_launch": False,
                "music_volume": 50,
                "launcher_color": "#562c79"
            }

        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Исправленная валидация
                config["music_volume"] = min(max(int(config.get("music_volume", 50)), 0), 100)
                return config
        except Exception as e:
            print(f"Ошибка чтения конфига: {str(e)}")
            return {
                "saved_nickname": "",
                "remember_nickname": False,
                "close_after_launch": False,
                "music_volume": 50,
                "launcher_color": "#562c79"
            }

    @Slot()
    def start_music(self):
        config = self.load_config()
        self.audio_output.setVolume(config["music_volume"] / 100)
        self.load_random_music()

    @Slot()
    def close_launcher(self):
        self.player.stop()
        self.close()

    @Slot(result=str)
    def open_color_picker(self):
        color = QColorDialog.getColor().name()
        return color


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())