document.addEventListener('DOMContentLoaded', () => {
    if (!window.QA_SESSION_DATA) return;

    const {
        startTime,
        duration,
        isLive,
        isUpcoming,
        isCompleted,
        sessionId
    } = window.QA_SESSION_DATA;

    const countdown = document.getElementById('session-countdown');
    const registerBtn = document.getElementById('register-btn');

    const start = new Date(startTime);
    const end = new Date(start.getTime() + duration * 60000);

    function update() {
        const now = new Date();

        // LIVE
        if (now >= start && now <= end) {
            if (countdown) {
                countdown.innerHTML = `<div class="alert alert-success">Session is live!</div>`;
            }

            if (registerBtn) {
                registerBtn.disabled = false;
                registerBtn.textContent = 'Join Session';
                registerBtn.classList.remove('btn-primary');
                registerBtn.classList.add('btn-success');

                registerBtn.onclick = () => {
                    window.location.href = `/experts/sessions/${sessionId}/join`;
                };
            }
            return;
        }

        // COMPLETED
        if (now > end) {
            if (countdown) {
                countdown.innerHTML = `<div class="alert alert-secondary">This session has ended.</div>`;
            }
            if (registerBtn) {
                registerBtn.disabled = true;
                registerBtn.textContent = 'Session Completed';
            }
            return;
        }

        // UPCOMING (COUNTDOWN)
        const diff = start - now;
        if (diff > 0 && countdown) {
            const d = Math.floor(diff / (1000 * 60 * 60 * 24));
            const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
            const m = Math.floor((diff / (1000 * 60)) % 60);
            const s = Math.floor((diff / 1000) % 60);

            countdown.querySelector('#days').textContent = d;
            countdown.querySelector('#hours').textContent = h;
            countdown.querySelector('#minutes').textContent = m;
            countdown.querySelector('#seconds').textContent = s;
        }
    }

    update();
    setInterval(update, 1000);
});
