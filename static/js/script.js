function initialize() {
    const cards = document.querySelectorAll('.news-card');
    const colorThief = new ColorThief();

    cards.forEach(card => {
        const img = new Image();
        const bgUrl = getComputedStyle(card).backgroundImage.slice(5, -2);
        img.src = bgUrl;

        img.onload = () => {
            const color = colorThief.getDominantColor(img, 10);
            card.style.setProperty('--dominant-color', `rgb(${color.r}, ${color.g}, ${color.b})`);

            const canvas = document.createElement('canvas');
            canvas.className = 'particle-canvas';
            card.appendChild(canvas);

            let ctx = canvas.getContext('2d');
            let particles = [];
            let animationFrameId;

            function initParticles() {
                canvas.width = card.offsetWidth;
                canvas.height = card.offsetHeight;
                particles = [];

                for (let i = 0; i < 30; i++) {
                    particles.push({
                        x: Math.random() * canvas.width,
                        y: Math.random() * canvas.height,
                        size: Math.random() * 2 + 1,
                        speedX: (Math.random() - 0.5) * 2,
                        speedY: (Math.random() - 0.5) * 2,
                        alpha: 0,
                        life: Math.random() * 100 + 50
                    });
                }
            }

            function updateParticles() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.globalCompositeOperation = 'lighter';

                particles.forEach(p => {
                    p.x += p.speedX;
                    p.y += p.speedY;
                    p.alpha = Math.min(p.alpha + 0.03, 1);
                    p.life--;

                    if (p.life > 0 && p.alpha > 0) {
                        ctx.beginPath();
                        ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${p.alpha})`;
                        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                        ctx.fill();
                    }
                });

                particles = particles.filter(p => p.life > 0);
                if (particles.length > 0) requestAnimationFrame(updateParticles);
            }

            card.addEventListener('mouseenter', () => {
                initParticles();
                updateParticles();
            });

            card.addEventListener('mouseleave', () => {
                cancelAnimationFrame(animationFrameId);
                particles.forEach(p => p.life = 0);
                card.style.transform = 'rotate(0)';
            });

            // Анимация наклона
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left - rect.width / 2) * 0.03;
                const y = (e.clientY - rect.top - rect.height / 2) * 0.01;
                card.style.transform = `rotateX(${y}deg) rotateY(${x}deg)`;
            });
        };
    });
}

function launchGame() {
    const nickname = document.getElementById('nickname').value || 'Гость';
    const closeAfterLaunch = document.getElementById('closeAfterLaunch').checked;
    window.pyobject.launchGame(nickname, closeAfterLaunch);
    saveConfig();
}

function toggleSettings() {
    const settingsMenu = document.querySelector('.settings-menu');
    const currentRight = window.getComputedStyle(settingsMenu).right;

    if (currentRight === '-300px' || currentRight === '-100%') {
        settingsMenu.style.right = '0';
        settingsMenu.style.opacity = '1';
    } else {
        settingsMenu.style.right = '-300px';
        settingsMenu.style.opacity = '0';
        saveConfig();
    }
}

function saveConfig() {
    const nickname = document.getElementById('nickname').value || '';
    const remember = document.getElementById('rememberNickname').checked;
    const closeAfterLaunch = document.getElementById('closeAfterLaunch').checked;
    const launcherColor = document.getElementById('colorPreview').style.background;
    window.pyobject.save_to_config(nickname, remember, closeAfterLaunch, launcherColor);
}

function closeLauncher() {
    window.pyobject.close_launcher();
}

function openColorPicker() {
    window.pyobject.open_color_picker((newColor) => {
        document.getElementById('colorPreview').style.background = newColor;
        document.body.style.background = newColor;
        saveConfig();
    });
}