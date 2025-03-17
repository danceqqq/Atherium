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

            const ctx = canvas.getContext('2d');
            let particles = [];

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
                        ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${p.alpha})`;
                        ctx.beginPath();
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
                particles.forEach(p => p.life = 0);
                card.style.transform = 'rotate(0)';
            });

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left - rect.width / 2) * 0.03;
                const y = (e.clientY - rect.top - rect.height / 2) * 0.01;
                card.style.transform = `rotateX(${y}deg) rotateY(${x}deg)`;
            });
        };
    });
}