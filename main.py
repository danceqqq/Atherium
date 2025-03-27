import sys
import json
import os
import random
import requests
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QColorDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Slot, QTimer, Qt
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

GITHUB_REPO = "https://raw.githubusercontent.com/danceqqq/Atherium/main/news.json"
GITHUB_COMMITS_API = "https://api.github.com/repos/danceqqq/Atherium/commits?per_page=4"
CACHE_DIR = ".cache"
IMG_CACHE_DIR = "static/img/cached"
MUSIC_DIR = "music"
MUSIC_IMG_DIR = "img/music"
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

        # WebView
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # WebChannel
        self.channel = QWebChannel()
        self.channel.registerObject("pyobject", self)
        self.web_view.page().setWebChannel(self.channel)

        self.show_loading_screen()
        QTimer.singleShot(3000, self.load_main_content)

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

    def load_music_list(self):
        if not os.path.exists(MUSIC_DIR):
            return []

        music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
        music_list = []

        for music_file in music_files:
            track_name = os.path.splitext(music_file)[0]
            cover_url = ""

            if os.path.exists(MUSIC_IMG_DIR):
                for ext in ['.jpg', '.jpeg', '.png']:
                    img_path = os.path.join(MUSIC_IMG_DIR, f"{track_name}{ext}")
                    if os.path.exists(img_path):
                        cover_url = f"file:///{os.path.abspath(img_path).replace('\\', '/')}"
                        break

            music_list.append({
                "track_name": track_name,
                "file_path": os.path.abspath(os.path.join(MUSIC_DIR, music_file)).replace('\\', '/'),
                "cover_url": cover_url if cover_url else "file:///" + os.path.abspath(
                    "static/img/no_music.png").replace('\\', '/')
            })

        return music_list

    def load_github_commits(self):
        try:
            response = requests.get(GITHUB_COMMITS_API, timeout=5)
            response.raise_for_status()
            commits = response.json()
            commits_html = ""

            for commit in commits[:4]:
                message = commit['commit']['message']
                author = commit['commit']['author']['name']
                date = datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%d.%m.%Y %H:%M")

                commits_html += f"""
                <div class="commit-card">
                    <div class="commit-header">
                        <div class="commit-info">
                            <div class="commit-author">{author}</div>
                            <div class="commit-date">{date}</div>
                        </div>
                    </div>
                    <div class="commit-message">{message}</div>
                </div>
                """

            return commits_html
        except Exception as e:
            print(f"Ошибка загрузки коммитов: {str(e)}")
            return "<p>Не удалось загрузить обновления</p>"

    def load_random_music(self):
        music_list = self.load_music_list()
        if not music_list:
            return

        selected_track = random.choice(music_list)
        self.current_music = selected_track["track_name"]
        music_path = selected_track["file_path"]

        QTimer.singleShot(500, lambda: self.update_music_ui(selected_track))
        self.player.setSource(QUrl.fromLocalFile(music_path))
        QTimer.singleShot(1000, self.player.play)

    @Slot(str)
    def play_selected_track(self, track_name):
        music_list = self.load_music_list()
        selected_track = next((t for t in music_list if t["track_name"] == track_name), None)

        if selected_track:
            self.current_music = track_name
            self.player.setSource(QUrl.fromLocalFile(selected_track["file_path"]))
            self.player.play()
            QTimer.singleShot(100, lambda: self.update_music_ui(selected_track))

    def update_music_ui(self, track_info):
        self.web_view.page().runJavaScript(f"""
            (function() {{
                const musicBanner = document.querySelector('.music-banner');
                musicBanner.style.backgroundImage = "url('{track_info['cover_url']}')";
                musicBanner.style.backgroundSize = "cover";
                musicBanner.style.backgroundPosition = "center";
                musicBanner.style.borderRadius = "15px";
                document.getElementById('musicTitle').innerText = "{track_info['track_name']}";

                document.querySelectorAll('.music-track').forEach(track => {{
                    track.classList.remove('active');
                    if(track.dataset.trackName === "{track_info['track_name']}") {{
                        track.classList.add('active');
                    }}
                }});
            }})();
        """)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            QTimer.singleShot(2000, self.load_random_music)

    def load_main_content(self):
        self.news_data = self.load_news_data(force_update=True)
        self.cache_images()
        self.music_list = self.load_music_list()
        self.github_commits = self.load_github_commits()
        html_content = self.generate_html()
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(os.path.abspath("index.html")))
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
                    overflow: hidden;
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

    def generate_html(self):
        config = self.load_config()
        nickname = config.get("saved_nickname", "")
        remember = config.get("remember_nickname", False)
        close_after = config.get("close_after_launch", False)
        volume = config.get("music_volume", 50)
        color = config.get("launcher_color", "#562c79")

        music_list_html = ""
        for track in self.music_list:
            music_list_html += f"""
            <div class="music-track" data-track-name="{track['track_name']}" onclick="window.pyobject.play_selected_track('{track['track_name']}')">
                <img src="{track['cover_url']}" onerror="this.src='file:///{os.path.abspath('static/img/no_music.png').replace('\\', '/')}'">
                <h4>{track['track_name']}</h4>
            </div>
            """

        news_cards_html = ""
        if not self.news_data:
            news_cards_html = "<p>Нет новостей</p>"
        else:
            for item in self.news_data:
                img_url = item.get("image_url", "")
                img_path = ""
                if img_url:
                    img_name = os.path.basename(img_url)
                    img_path = os.path.abspath(os.path.join(IMG_CACHE_DIR, img_name)).replace("\\", "/")
                    if not os.path.exists(img_path):
                        img_path = os.path.abspath("static/img/no_news.png").replace("\\", "/")

                title = item.get('title', 'Нет заголовка')
                text = item.get('text', 'Нет описания')[:150] + "..."

                news_cards_html += f"""
                <div class="card" style="background-image: url('file:///{img_path}');">
                    <div class="card__content">
                        <p class="card__title">{title}</p>
                        <p class="card__description">{text}</p>
                    </div>
                </div>
                """

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
        <body style="background: {color}; overflow: hidden;">
            <!-- Верхняя панель -->
            <div class="top-bar">
                <!-- Пустой placeholder для выравнивания -->
            </div>

            <!-- Вкладки -->
            <div class="tabs">
                <div class="tab active" onclick="showMain()">
                    <svg class="tab-icon" viewBox="0 0 24 24">
                        <path d="M3 17h18v-2H3v2zm0 3h18v-1H3v1zm0-7h18v-3H3v3zm4-3v2H5v-2h2zm0-4v2H5V7h2zm4 0v2H9V7h2zm4 0v2h-2V7h2zm4 0v2h-2V7h2zm-8 4v2h-2v-2h2zm0 4v2h-2v-2h2zm0 4v2h-2v-2h2zm8-8v2h-2v-2h2zm0 4v2h-2v-2h2zm0 4v2h-2v-2h2z"/>
                    </svg>
                    <span class="tab-text">Главная страница</span>
                </div>
                <div class="tab" onclick="showMusic()">
                    <svg class="tab-icon" viewBox="0 0 24 24">
                        <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-8z"/>
                    </svg>
                    <span class="tab-text">Музыка</span>
                </div>
                <div class="tab" onclick="showFeedback()">
                    <svg class="tab-icon" viewBox="0 0 24 24">
                        <path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                    </svg>
                    <span class="tab-text">Обратная связь</span>
                </div>
                <div class="tab" onclick="showGitHub()">
                    <svg class="tab-icon" viewBox="0 0 24 24">
                        <path d="M12 0C5.37 0 0 5.37 0 12c0 10.93 9.07 20 20 20s20-9.07 20-20S22.93 0 12 0zm4 16c0 1.11-.89 2-2 2s-2-.89-2-2 .89-2 2-2 2 1.11 2 2zm-6 0c0 1.11-.89 2-2 2s-2-.89-2-2 .89-2 2-2 2 1.11 2 2zm6-8c0 2.21-1.79 4-4 4s-4-1.79-4-4 1.79-4 4-4 4 1.79 4 4zm-6 0c0 2.21-1.79 4-4 4s-4-1.79-4-4 1.79-4 4-4 4 1.79 4 4zm10 4c0 2.21-1.79 4-4 4s-4-1.79-4-4 1.79-4 4-4 4 1.79 4 4z"/>
                    </svg>
                    <span class="tab-text">GitHub</span>
                </div>
                <div class="tab exit-tab" onclick="closeLauncher()">
                    <svg class="tab-icon" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
                    </svg>
                    <span class="tab-text">Выход</span>
                </div>
            </div>

            <!-- Секция главной страницы -->
            <div class="main-section active-section">
                <div class="main-container">
                    <div class="news-grid">
                        {news_cards_html}
                    </div>
                    <div class="time-card">
                        <div class="time-content">
                            <p class="time-text" id="currentTime">00:00</p>
                            <p class="day-text" id="currentDate">Загрузка...</p>
                        </div>
                    </div>
                </div>
                <div class="music-banner-container">
                    <div class="music-banner">
                        <div class="music-content">
                            <h3 id="musicTitle">Музыка загружается...</h3>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Секция музыки -->
            <div class="music-section">
                <div class="music-header">
                    <h2>Список треков</h2>
                </div>
                <div class="music-list-container">
                    <div class="music-list">
                        {music_list_html}
                    </div>
                </div>
            </div>

            <!-- Секция обратной связи -->
            <div class="feedback-section">
                <h2>Обратная связь</h2>
                <p>Этот раздел находится в разработке</p>
            </div>

            <!-- Секция GitHub -->
            <div class="github-section">
                <div class="github-container">
                    <h2>Последние обновления</h2>
                    <div class="commits-list">
                        {self.github_commits}
                    </div>
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

                // Переключение вкладок
                function showMain() {{
                    document.querySelector('.main-section').style.display = 'block';
                    document.querySelector('.music-section').style.display = 'none';
                    document.querySelector('.feedback-section').style.display = 'none';
                    document.querySelector('.github-section').style.display = 'none';
                    setActiveTab(0);
                }}

                function showMusic() {{
                    document.querySelector('.main-section').style.display = 'none';
                    document.querySelector('.music-section').style.display = 'block';
                    document.querySelector('.feedback-section').style.display = 'none';
                    document.querySelector('.github-section').style.display = 'none';
                    setActiveTab(1);
                }}

                function showFeedback() {{
                    document.querySelector('.main-section').style.display = 'none';
                    document.querySelector('.music-section').style.display = 'none';
                    document.querySelector('.feedback-section').style.display = 'block';
                    document.querySelector('.github-section').style.display = 'none';
                    setActiveTab(2);
                }}

                function showGitHub() {{
                    document.querySelector('.main-section').style.display = 'none';
                    document.querySelector('.music-section').style.display = 'none';
                    document.querySelector('.feedback-section').style.display = 'none';
                    document.querySelector('.github-section').style.display = 'block';
                    setActiveTab(3);
                }}

                function setActiveTab(index) {{
                    document.querySelectorAll('.tab').forEach((tab, i) => {{
                        tab.classList.toggle('active', i === index);
                    }});
                }}

                // Скрытие загрузочного экрана
                setTimeout(() => {{
                    document.querySelector('.loader')?.remove();
                }}, 3000);

                // Обновление времени
                function updateTime() {{
                    const now = new Date();
                    const timeElement = document.getElementById('currentTime');
                    const dateElement = document.getElementById('currentDate');

                    const hours = now.getHours().toString().padStart(2, '0');
                    const minutes = now.getMinutes().toString().padStart(2, '0');
                    const timeString = `${{hours}}:${{minutes}}`;

                    const days = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'];
                    const months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 
                                   'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря'];

                    const day = days[now.getDay()];
                    const date = now.getDate();
                    const month = months[now.getMonth()];
                    const dateString = `${{day}}, ${{date}} ${{month}}`;

                    timeElement.textContent = timeString;
                    dateElement.textContent = dateString;
                }}

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

                // Инициализация времени
                setInterval(updateTime, 1000);
                setTimeout(updateTime, 100); // Первый запуск
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