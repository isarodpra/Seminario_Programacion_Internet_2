/**
 * GPMV CDMX - Gestor de Pagos de Multas Vehiculares
 * Script principal: Efectos de Sonido (Web Audio API), Reproductor de Video Interactivo,
 * Mapas Satelitales (Leaflet) y Transiciones de Interfaz.
 */

/* ============================================================
   UTILIDAD DE CANVAS: Polyfill seguro para roundRect
   ============================================================ */
function drawRoundRect(ctx, x, y, width, height, radius) {
    if (typeof ctx.roundRect === 'function') {
        ctx.beginPath();
        ctx.roundRect(x, y, width, height, radius);
        return;
    }
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
}

/* ============================================================
   1. SISTEMA DE AUDIO DIGITAL (Web Audio API)
   ============================================================ */
class GPMVAudioSystem {
    constructor() {
        this.ctx = null;
        this.enabled = localStorage.getItem('gpmv_sound_enabled') !== 'false';
        this.volume = 0.25;
        this.initDOM();
    }

    getContext() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume().catch(() => {});
        }
        return this.ctx;
    }

    initDOM() {
        document.addEventListener('DOMContentLoaded', () => {
            this.updateButtonUI();
            const btn = document.getElementById('soundToggleBtn');
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggle();
                });
            }

            // Detectar mensajes flash para sonido
            const flash = document.querySelector('.flash');
            if (flash) {
                const text = flash.textContent.toLowerCase();
                if (text.includes('incorrect') || text.includes('error') || text.includes('no se')) {
                    setTimeout(() => this.playError(), 250);
                } else {
                    setTimeout(() => this.playSuccess(), 250);
                }
            }

            // Asignar sonido de clic a botones y enlaces
            document.querySelectorAll('.btn, .nav-item, .chip-btn, .zone-pill, .role-btn').forEach(el => {
                el.addEventListener('click', () => {
                    this.playClick();
                });
            });
        });
    }

    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem('gpmv_sound_enabled', this.enabled);
        this.updateButtonUI();
        if (this.enabled) {
            this.playNotification();
        }
    }

    updateButtonUI() {
        const icon = document.getElementById('soundIcon');
        const text = document.getElementById('soundText');
        const btn = document.getElementById('soundToggleBtn');
        if (icon && text && btn) {
            if (this.enabled) {
                icon.textContent = '🔊';
                text.textContent = 'Sonido: ON';
                btn.classList.remove('muted');
            } else {
                icon.textContent = '🔇';
                text.textContent = 'Sonido: OFF';
                btn.classList.add('muted');
            }
        }
    }

    playClick() {
        if (!this.enabled) return;
        const ctx = this.getContext();
        if (!ctx) return;
        try {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(600, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.04);
            gain.gain.setValueAtTime(this.volume * 0.4, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.04);
        } catch (e) { console.debug(e); }
    }

    playSuccess() {
        if (!this.enabled) return;
        const ctx = this.getContext();
        if (!ctx) return;
        try {
            const notes = [523.25, 659.25, 783.99, 1046.50];
            notes.forEach((freq, idx) => {
                const startTime = ctx.currentTime + (idx * 0.08);
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, startTime);
                gain.gain.setValueAtTime(0.001, startTime);
                gain.gain.linearRampToValueAtTime(this.volume * 0.5, startTime + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.35);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(startTime);
                osc.stop(startTime + 0.35);
            });
        } catch (e) { console.debug(e); }
    }

    playError() {
        if (!this.enabled) return;
        const ctx = this.getContext();
        if (!ctx) return;
        try {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(240, ctx.currentTime);
            osc.frequency.linearRampToValueAtTime(160, ctx.currentTime + 0.25);
            gain.gain.setValueAtTime(this.volume * 0.35, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.25);
        } catch (e) { console.debug(e); }
    }

    playNotification() {
        if (!this.enabled) return;
        const ctx = this.getContext();
        if (!ctx) return;
        try {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.3);
            gain.gain.setValueAtTime(this.volume * 0.5, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.3);
        } catch (e) { console.debug(e); }
    }
}

window.gpmvAudio = new GPMVAudioSystem();


/* ============================================================
   2. REPRODUCTOR DE VIDEO TUTORIAL INTERACTIVO (CANVAS)
   ============================================================ */
class GPMVVideoPlayer {
    constructor() {
        this.canvas = document.getElementById('videoCanvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.isPlaying = false;
        this.currentTime = 0;
        this.totalDuration = 90;
        this.currentRole = 'user';
        this.animationFrame = null;

        this.chaptersUser = [
            { start: 0, end: 25, title: 'Paso 1: Consulta de Placa', tip: 'Ingresa la placa con 7 caracteres sin guiones ni espacios.' },
            { start: 25, end: 50, title: 'Paso 2: Revisión de Multas y Descuentos', tip: 'Aprovecha hasta un 20% de descuento si pagas dentro de los primeros 15 días.' },
            { start: 50, end: 70, title: 'Paso 3: Pago en Línea y Comprobante PDF', tip: 'El comprobante PDF cuenta con validez legal ante cualquier autoridad vial.' },
            { start: 70, end: 90, title: 'Paso 4: Ubicación del Corralón y Retiro', tip: 'Presenta tu INE, tarjeta de circulación y comprobante GPMV para el retiro.' }
        ];

        this.chaptersAdmin = [
            { start: 0, end: 30, title: 'Módulo 1: Acceso Seguro y Roles', tip: 'Contraseñas protegidas mediante algoritmos de hash scrypt resistentes a ataques.' },
            { start: 30, end: 60, title: 'Módulo 2: Gestión y Liberación Vehicular', tip: 'El estatus cambia automáticamente a Liberada cuando se saldan todas las multas.' },
            { start: 60, end: 90, title: 'Módulo 3: Métricas de Recaudación y Auditoría', tip: 'Consulta pagos por mes, montos acumulados y distribución de infracciones.' }
        ];

        this.bindDOMControls();
        this.renderFrame();
    }

    bindDOMControls() {
        window.addEventListener('resize', () => this.renderFrame());

        const overlay = document.getElementById('videoOverlay');
        if (overlay) {
            overlay.addEventListener('click', () => this.togglePlay());
            overlay.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.togglePlay();
                }
            });
        }

        const btnPlay = document.getElementById('btnPlayPause');
        if (btnPlay) btnPlay.addEventListener('click', () => this.togglePlay());

        const progressWrapper = document.querySelector('.video-progress-wrapper');
        if (progressWrapper) {
            progressWrapper.addEventListener('click', (e) => this.seekFromEvent(e));
        }

        const btnRestart = document.getElementById('btnRestartVideo');
        if (btnRestart) btnRestart.addEventListener('click', () => this.restart());

        const btnSound = document.getElementById('btnVideoSound');
        if (btnSound) btnSound.addEventListener('click', () => this.toggleAudio());

        const btnFullscreen = document.getElementById('btnFullscreen');
        if (btnFullscreen) btnFullscreen.addEventListener('click', () => this.toggleFullScreen());

        // Selectores de Rol (Ciudadano vs Admin)
        const btnRoleUser = document.getElementById('btnRoleUser');
        if (btnRoleUser) btnRoleUser.addEventListener('click', () => this.setRole('user'));

        const btnRoleAdmin = document.getElementById('btnRoleAdmin');
        if (btnRoleAdmin) btnRoleAdmin.addEventListener('click', () => this.setRole('admin'));

        // Capítulos clicables en Playlist
        document.querySelectorAll('[data-chapter]').forEach(el => {
            el.addEventListener('click', () => {
                const idx = parseInt(el.getAttribute('data-chapter'), 10);
                this.jumpToChapter(idx);
            });
        });

        document.querySelectorAll('[data-admin-chapter]').forEach(el => {
            el.addEventListener('click', () => {
                const idx = parseInt(el.getAttribute('data-admin-chapter'), 10);
                this.jumpToAdminChapter(idx);
            });
        });
    }

    getChapters() {
        return this.currentRole === 'user' ? this.chaptersUser : this.chaptersAdmin;
    }

    getCurrentChapter() {
        const list = this.getChapters();
        return list.find(c => this.currentTime >= c.start && this.currentTime < c.end) || list[list.length - 1];
    }

    togglePlay() {
        this.isPlaying = !this.isPlaying;
        const overlay = document.getElementById('videoOverlay');
        const ctrlIcon = document.getElementById('ctrlPlayIcon');
        const bigIcon = document.getElementById('bigPlayIcon');

        if (this.isPlaying) {
            if (overlay) overlay.style.display = 'none';
            if (ctrlIcon) ctrlIcon.textContent = '⏸';
            if (bigIcon) bigIcon.textContent = '⏸';
            if (window.gpmvAudio) window.gpmvAudio.playClick();
            this.lastTimestamp = performance.now();
            this.loop();
        } else {
            if (overlay) overlay.style.display = 'flex';
            if (ctrlIcon) ctrlIcon.textContent = '▶';
            if (bigIcon) bigIcon.textContent = '▶';
            if (window.gpmvAudio) window.gpmvAudio.playClick();
            cancelAnimationFrame(this.animationFrame);
        }
    }

    loop() {
        if (!this.isPlaying) return;
        const now = performance.now();
        const delta = (now - this.lastTimestamp) / 1000;
        this.lastTimestamp = now;

        this.currentTime += delta;
        if (this.currentTime >= this.totalDuration) {
            this.currentTime = this.totalDuration;
            this.togglePlay();
        }

        this.updateUI();
        this.renderFrame();

        this.animationFrame = requestAnimationFrame(() => this.loop());
    }

    seek(percent) {
        this.currentTime = percent * this.totalDuration;
        this.updateUI();
        this.renderFrame();
        if (window.gpmvAudio) window.gpmvAudio.playNotification();
    }

    seekFromEvent(e) {
        const bar = e.currentTarget;
        const rect = bar.getBoundingClientRect();
        const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        this.seek(percent);
    }

    restart() {
        this.currentTime = 0;
        this.updateUI();
        this.renderFrame();
        if (!this.isPlaying) {
            this.togglePlay();
        }
    }

    jumpToChapter(idx) {
        const chap = this.chaptersUser[idx];
        if (chap) this.seek(chap.start / this.totalDuration);
    }

    jumpToAdminChapter(idx) {
        const chap = this.chaptersAdmin[idx];
        if (chap) this.seek(chap.start / this.totalDuration);
    }

    toggleAudio() {
        if (window.gpmvAudio) window.gpmvAudio.toggle();
        const icon = document.getElementById('videoSoundIcon');
        if (icon) {
            icon.textContent = window.gpmvAudio.enabled ? '🔊' : '🔇';
        }
    }

    toggleFullScreen() {
        const frame = document.getElementById('videoScreen');
        if (!frame) return;
        if (!document.fullscreenElement) {
            frame.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen().catch(() => {});
        }
    }

    setRole(role) {
        this.currentRole = role;
        this.currentTime = 0;
        const btnUser = document.getElementById('btnRoleUser');
        const btnAdmin = document.getElementById('btnRoleAdmin');
        const listUser = document.getElementById('playlistUser');
        const listAdmin = document.getElementById('playlistAdmin');
        const title = document.getElementById('playlistTitle');

        if (role === 'admin') {
            if (btnUser) btnUser.classList.remove('active');
            if (btnAdmin) btnAdmin.classList.add('active');
            if (listUser) listUser.classList.remove('active');
            if (listAdmin) listAdmin.classList.add('active');
            if (title) title.textContent = 'Capítulos del Tutorial: Administrador';
        } else {
            if (btnAdmin) btnAdmin.classList.remove('active');
            if (btnUser) btnUser.classList.add('active');
            if (listAdmin) listAdmin.classList.remove('active');
            if (listUser) listUser.classList.add('active');
            if (title) title.textContent = 'Capítulos del Tutorial: Ciudadano';
        }

        this.updateUI();
        this.renderFrame();
        if (window.gpmvAudio) window.gpmvAudio.playNotification();
    }

    updateUI() {
        const progress = (this.currentTime / this.totalDuration) * 100;
        const filled = document.getElementById('videoProgressFilled');
        if (filled) filled.style.width = `${progress}%`;

        const curText = document.getElementById('currentTimeText');
        if (curText) curText.textContent = this.formatTime(this.currentTime);

        const totText = document.getElementById('totalTimeText');
        if (totText) totText.textContent = this.formatTime(this.totalDuration);

        const curChap = this.getCurrentChapter();
        const badge = document.getElementById('videoChapterBadge');
        if (badge && curChap) badge.textContent = curChap.title;

        const tip = document.getElementById('videoTipText');
        if (tip && curChap) tip.textContent = curChap.tip;

        const chapters = this.getChapters();
        const activeIdx = chapters.indexOf(curChap);
        const container = this.currentRole === 'user' ? document.getElementById('playlistUser') : document.getElementById('playlistAdmin');
        if (container) {
            const items = container.querySelectorAll('.playlist-item');
            items.forEach((item, idx) => {
                if (idx === activeIdx) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
    }

    formatTime(sec) {
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    renderFrame() {
        const c = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        const bgGrad = c.createLinearGradient(0, 0, w, h);
        bgGrad.addColorStop(0, '#0f172a');
        bgGrad.addColorStop(1, '#1e293b');
        c.fillStyle = bgGrad;
        c.fillRect(0, 0, w, h);

        c.fillStyle = '#1a365d';
        c.fillRect(40, 30, w - 80, 40);

        c.fillStyle = '#ef4444'; c.beginPath(); c.arc(60, 50, 6, 0, Math.PI * 2); c.fill();
        c.fillStyle = '#f59e0b'; c.beginPath(); c.arc(80, 50, 6, 0, Math.PI * 2); c.fill();
        c.fillStyle = '#10b981'; c.beginPath(); c.arc(100, 50, 6, 0, Math.PI * 2); c.fill();

        c.fillStyle = '#0f172a';
        drawRoundRect(c, 130, 38, w - 240, 24, 6);
        c.fill();
        c.fillStyle = '#94a3b8';
        c.font = '12px Segoe UI, sans-serif';
        const urlSim = this.currentRole === 'user' ? 'https://gpmv.cdmx.gob.mx/consulta' : 'https://gpmv.cdmx.gob.mx/admin';
        c.fillText(`🔒 ${urlSim}`, 145, 54);

        c.fillStyle = '#f8fafc';
        c.fillRect(40, 70, w - 80, h - 110);

        if (this.currentRole === 'user') {
            this.renderCitizenDemo(c, w, h);
        } else {
            this.renderAdminDemo(c, w, h);
        }

        c.fillStyle = 'rgba(15, 23, 42, 0.85)';
        drawRoundRect(c, 60, h - 85, w - 120, 35, 8);
        c.fill();

        c.fillStyle = '#ffffff';
        c.font = 'bold 15px Segoe UI, sans-serif';
        c.textAlign = 'center';
        const chap = this.getCurrentChapter();
        c.fillText(`▶ ${chap.title} — ${chap.tip}`, w / 2, h - 62);
        c.textAlign = 'left';
    }

    renderCitizenDemo(c, w, h) {
        const time = this.currentTime;

        c.fillStyle = '#1a3d7c';
        c.fillRect(40, 70, w - 80, 50);
        c.fillStyle = '#ffffff';
        c.font = 'bold 16px Segoe UI, sans-serif';
        c.fillText('🚗 GPMV CDMX — Gestor de Pagos de Multas', 60, 102);

        c.fillStyle = '#7b1e3a';
        c.fillRect(40, 120, w - 80, 4);

        if (time < 25) {
            c.fillStyle = '#1a3d7c';
            c.font = 'bold 22px Segoe UI, sans-serif';
            c.fillText('Consulta de Multas Vehiculares', 80, 170);

            c.fillStyle = '#64748b';
            c.font = '14px Segoe UI, sans-serif';
            c.fillText('Ingresa tu placa vehicular para consultar multas e infracciones registradas:', 80, 200);

            c.fillStyle = '#ffffff';
            c.strokeStyle = '#2563eb';
            c.lineWidth = 2;
            drawRoundRect(c, 80, 220, 360, 45, 6);
            c.fill();
            c.stroke();

            const plateChars = 'ABC1234';
            const charsToShow = Math.min(plateChars.length, Math.floor((time / 15) * plateChars.length));
            c.fillStyle = '#0f172a';
            c.font = 'bold 20px monospace';
            c.fillText(plateChars.substring(0, charsToShow) + (Math.floor(time * 3) % 2 === 0 ? '|' : ''), 100, 250);

            c.fillStyle = '#1a3d7c';
            drawRoundRect(c, 460, 220, 140, 45, 6);
            c.fill();
            c.fillStyle = '#ffffff';
            c.font = 'bold 16px Segoe UI, sans-serif';
            c.fillText('🔍 Buscar', 495, 248);

            const cursorX = 490 + Math.sin(time * 2) * 20;
            const cursorY = 240 + Math.cos(time * 2) * 5;
            this.drawCursor(c, cursorX, cursorY);

        } else if (time < 50) {
            c.fillStyle = '#0f172a';
            c.font = 'bold 20px Segoe UI, sans-serif';
            c.fillText('Resultados para la Placa: ABC1234 (Nissan Versa)', 80, 160);

            c.fillStyle = '#ffffff';
            c.shadowColor = 'rgba(0,0,0,0.08)';
            c.shadowBlur = 10;
            drawRoundRect(c, 80, 185, w - 160, 210, 8);
            c.fill();
            c.shadowBlur = 0;

            c.fillStyle = '#1e293b';
            c.font = 'bold 16px Segoe UI, sans-serif';
            c.fillText('Folio: FOL-2026-0001 — Exceso de velocidad en Insurgentes', 105, 225);

            c.font = '14px Segoe UI, sans-serif';
            c.fillStyle = '#475569';
            c.fillText('Monto original determinado: $1,200.00 MXN', 105, 260);

            c.fillStyle = '#fef08a';
            c.strokeStyle = '#ca8a04';
            drawRoundRect(c, 105, 280, 260, 32, 6);
            c.fill();
            c.stroke();
            c.fillStyle = '#854d0e';
            c.font = 'bold 13px Segoe UI, sans-serif';
            c.fillText('🎉 20% Descuento por Pronto Pago', 120, 301);

            c.fillStyle = '#15803d';
            c.font = 'bold 22px Segoe UI, sans-serif';
            c.fillText('Total a pagar: $960.00 MXN', 105, 350);

            c.fillStyle = '#28a745';
            drawRoundRect(c, w - 300, 315, 180, 45, 6);
            c.fill();
            c.fillStyle = '#ffffff';
            c.font = 'bold 15px Segoe UI, sans-serif';
            c.fillText('💳 Pagar Multa', w - 265, 343);

        } else if (time < 70) {
            c.fillStyle = '#15803d';
            c.font = 'bold 22px Segoe UI, sans-serif';
            c.fillText('✅ ¡Pago Realizado con Éxito!', 80, 160);

            c.fillStyle = '#ffffff';
            c.strokeStyle = '#cbd5e1';
            c.lineWidth = 1;
            drawRoundRect(c, 80, 180, 480, 220, 8);
            c.fill();
            c.stroke();

            c.fillStyle = '#7b1e3a';
            c.fillRect(80, 180, 480, 30);
            c.fillStyle = '#ffffff';
            c.font = 'bold 12px Segoe UI, sans-serif';
            c.fillText('COMPROBANTE OFICIAL DIGITAL — CDMX', 100, 200);

            c.fillStyle = '#334155';
            c.font = '13px Segoe UI, sans-serif';
            c.fillText('Referencia: REF-20261020-A1B2C3', 100, 240);
            c.fillText('Placa: ABC1234 — Vehículo: Nissan Versa', 100, 265);
            c.fillText('Monto Pagado: $960.00 MXN (SPEI / Tarjeta)', 100, 290);
            c.fillText('Nuevo Estatus del Vehículo: LIBERADA 🚗', 100, 315);

            c.fillStyle = '#1a3d7c';
            drawRoundRect(c, 100, 340, 240, 40, 6);
            c.fill();
            c.fillStyle = '#ffffff';
            c.font = 'bold 14px Segoe UI, sans-serif';
            c.fillText('📥 Descargar Comprobante PDF', 115, 365);

        } else {
            c.fillStyle = '#1a3d7c';
            c.font = 'bold 20px Segoe UI, sans-serif';
            c.fillText('🗺️ Ubicación del Depósito Vehicular (Corralón)', 80, 155);

            c.fillStyle = '#e2e8f0';
            drawRoundRect(c, 80, 175, 440, 220, 8);
            c.fill();

            c.strokeStyle = '#ffffff';
            c.lineWidth = 8;
            c.beginPath(); c.moveTo(80, 280); c.lineTo(520, 280); c.stroke();
            c.beginPath(); c.moveTo(250, 175); c.lineTo(250, 395); c.stroke();

            c.fillStyle = '#7b1e3a';
            c.beginPath(); c.arc(320, 250, 16, 0, Math.PI * 2); c.fill();
            c.fillStyle = '#ffffff';
            c.font = 'bold 12px Segoe UI';
            c.fillText('🏛️', 312, 255);

            c.fillStyle = '#ffffff';
            drawRoundRect(c, 540, 175, 340, 220, 8);
            c.fill();
            c.fillStyle = '#1e293b';
            c.font = 'bold 16px Segoe UI';
            c.fillText('Corralón Central CDMX', 560, 210);
            c.font = '13px Segoe UI';
            c.fillStyle = '#475569';
            c.fillText('📍 Av. Insurgentes Sur 1234', 560, 240);
            c.fillText('📦 Área Asignada: A-12', 560, 270);
            c.fillText('⏰ Horario: 24 horas continuas', 560, 300);
            c.fillStyle = '#2563eb';
            c.fillText('📞 Atención: 55 5242 5100', 560, 330);
        }
    }

    renderAdminDemo(c, w, h) {
        const time = this.currentTime;

        c.fillStyle = '#6a3d9a';
        c.fillRect(40, 70, w - 80, 50);
        c.fillStyle = '#ffffff';
        c.font = 'bold 16px Segoe UI, sans-serif';
        c.fillText('🛡️ GPMV — Panel de Control y Auditoría Operativa', 60, 102);

        c.fillStyle = '#7b1e3a';
        c.fillRect(40, 120, w - 80, 4);

        if (time < 30) {
            c.fillStyle = '#6a3d9a';
            c.font = 'bold 22px Segoe UI, sans-serif';
            c.fillText('Autenticación Segura de Administrador', 80, 170);

            c.fillStyle = '#64748b';
            c.font = '14px Segoe UI, sans-serif';
            c.fillText('Acceso protegido contra inyecciones SQL y ataques de fuerza bruta:', 80, 205);

            c.fillStyle = '#ffffff';
            drawRoundRect(c, 80, 230, 340, 40, 6);
            c.fill();
            c.fillStyle = '#1e293b';
            c.font = '15px monospace';
            c.fillText('admin', 100, 255);

            c.fillStyle = '#ffffff';
            drawRoundRect(c, 80, 285, 340, 40, 6);
            c.fill();
            c.fillStyle = '#1e293b';
            c.fillText('••••••••••••', 100, 310);

            c.fillStyle = '#6a3d9a';
            drawRoundRect(c, 80, 340, 160, 40, 6);
            c.fill();
            c.fillStyle = '#ffffff';
            c.font = 'bold 14px Segoe UI';
            c.fillText('Ingresar al Panel', 105, 365);

        } else if (time < 60) {
            c.fillStyle = '#1e293b';
            c.font = 'bold 20px Segoe UI, sans-serif';
            c.fillText('Gestión de Infracciones Registradas', 80, 160);

            c.fillStyle = '#1a3d7c';
            c.fillRect(80, 185, w - 160, 32);
            c.fillStyle = '#ffffff';
            c.font = 'bold 13px Segoe UI';
            c.fillText('Folio', 100, 206);
            c.fillText('Placa', 240, 206);
            c.fillText('Monto', 380, 206);
            c.fillText('Estatus', 520, 206);
            c.fillText('Acción', 680, 206);

            c.fillStyle = '#ffffff';
            c.fillRect(80, 218, w - 160, 40);
            c.fillStyle = '#334155';
            c.fillText('FOL-2026-0001', 100, 243);
            c.fillText('ABC1234', 240, 243);
            c.fillText('$1,200.00', 380, 243);
            c.fillStyle = '#15803d';
            c.fillText('● Liberada', 520, 243);
            c.fillStyle = '#2563eb';
            c.fillText('Ver Detalle', 680, 243);

            c.fillStyle = '#f8fafc';
            c.fillRect(80, 259, w - 160, 40);
            c.fillStyle = '#334155';
            c.fillText('FOL-2026-0002', 100, 284);
            c.fillText('ABC1234', 240, 284);
            c.fillText('$800.00', 380, 284);
            c.fillStyle = '#dc2626';
            c.fillText('● Pendiente', 520, 284);
            c.fillStyle = '#2563eb';
            c.fillText('Ver Detalle', 680, 284);

        } else {
            c.fillStyle = '#1e293b';
            c.font = 'bold 20px Segoe UI, sans-serif';
            c.fillText('Reportes Estadísticos y Resumen Financiero', 80, 160);

            c.fillStyle = '#ffffff';
            drawRoundRect(c, 80, 185, 420, 210, 8);
            c.fill();
            c.fillStyle = '#6a3d9a';
            c.font = 'bold 14px Segoe UI';
            c.fillText('📊 Infracciones por Estatus', 100, 215);

            const bars = [
                { label: 'Pendientes', val: 120, col: '#ef4444' },
                { label: 'Pagadas', val: 240, col: '#10b981' },
                { label: 'Liberadas', val: 190, col: '#3b82f6' }
            ];
            bars.forEach((b, idx) => {
                c.fillStyle = b.col;
                c.fillRect(120 + (idx * 110), 360 - b.val, 70, b.val);
                c.fillStyle = '#64748b';
                c.font = '12px Segoe UI';
                c.fillText(b.label, 125 + (idx * 110), 380);
            });

            c.fillStyle = '#ffffff';
            drawRoundRect(c, 520, 185, 360, 210, 8);
            c.fill();
            c.fillStyle = '#1e293b';
            c.font = 'bold 14px Segoe UI';
            c.fillText('📈 Total Recaudado en el Mes', 540, 215);
            c.fillStyle = '#15803d';
            c.font = 'bold 26px Segoe UI';
            c.fillText('$342,800.00 MXN', 540, 260);
            c.fillStyle = '#64748b';
            c.font = '13px Segoe UI';
            c.fillText('Promedio de pago: 3.2 días hábiles', 540, 295);
            c.fillText('Porcentaje con descuento: 78.4%', 540, 320);
        }
    }

    drawCursor(c, x, y) {
        c.fillStyle = '#0f172a';
        c.beginPath();
        c.moveTo(x, y);
        c.lineTo(x + 15, y + 10);
        c.lineTo(x + 8, y + 12);
        c.lineTo(x + 12, y + 22);
        c.lineTo(x + 6, y + 24);
        c.lineTo(x + 2, y + 14);
        c.lineTo(x, y + 18);
        c.closePath();
        c.fill();
    }
}


/* ============================================================
   3. MAPAS INTERACTIVOS (LEAFLET + OPENSTREETMAP)
   ============================================================ */
let leafletCorralonMap = null;
let corralonMarkers = [];
let userLocationMarker = null;

function initCorralonMap() {
    const mapElement = document.getElementById('corralonMap');
    if (!mapElement || typeof L === 'undefined') return;

    if (leafletCorralonMap) {
        try {
            leafletCorralonMap.remove();
        } catch (e) { console.debug(e); }
        leafletCorralonMap = null;
    }

    const CDMX_CENTER = [19.4326, -99.1332];
    leafletCorralonMap = L.map('corralonMap', {
        center: CDMX_CENTER,
        zoom: 11,
        zoomControl: true,
        scrollWheelZoom: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors &bull; GPMV CDMX'
    }).addTo(leafletCorralonMap);

    // Intentar cargar datos desde API REST o fallback del DOM
    fetch('/api/corralones')
        .then(res => {
            if (!res.ok) throw new Error('API offline');
            return res.json();
        })
        .then(corralones => {
            renderCorralonMarkers(corralones);
        })
        .catch(() => {
            // Fallback: leer atributos data-* de las tarjetas en el DOM
            const cards = document.querySelectorAll('.corralon-item-card');
            const dataFromDOM = Array.from(cards).map(card => ({
                nombre: card.getAttribute('data-name') || '',
                zona: card.getAttribute('data-zone') || 'Centro',
                lat: parseFloat(card.getAttribute('data-lat')) || 19.4326,
                lng: parseFloat(card.getAttribute('data-lng')) || -99.1332,
                direccion: card.querySelector('.corralon-card-address')?.textContent?.replace('📍', '').trim() || '',
                referencia: card.querySelector('.corralon-card-ref')?.textContent?.replace('🚩 Ref:', '').trim() || '',
                telefono: '55 5242 5100',
                capacidad: '400 vehículos'
            }));
            renderCorralonMarkers(dataFromDOM);
        });

    // Vincular controles de la barra de mapa
    const btnLocate = document.getElementById('btnLocateUser');
    if (btnLocate) btnLocate.addEventListener('click', locateUserPosition);

    const btnReset = document.getElementById('btnResetMapView');
    if (btnReset) btnReset.addEventListener('click', resetMapView);

    const searchInput = document.getElementById('corralonSearchInput');
    if (searchInput) searchInput.addEventListener('input', filterCorralones);

    document.querySelectorAll('.zone-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const zone = pill.getAttribute('data-zone') || 'all';
            filterByZone(zone, pill);
        });
    });

    // Vincular clic en tarjetas de corralón
    document.querySelectorAll('.corralon-item-card').forEach(card => {
        card.addEventListener('click', () => {
            const lat = parseFloat(card.getAttribute('data-lat'));
            const lng = parseFloat(card.getAttribute('data-lng'));
            const name = card.getAttribute('data-name');
            focusCorralon(lat, lng, name);
        });

        const btnFocus = card.querySelector('.btn-focus-marker');
        if (btnFocus) {
            btnFocus.addEventListener('click', (e) => {
                e.stopPropagation();
                const lat = parseFloat(card.getAttribute('data-lat'));
                const lng = parseFloat(card.getAttribute('data-lng'));
                const name = card.getAttribute('data-name');
                focusCorralon(lat, lng, name);
            });
        }
    });
}

function renderCorralonMarkers(corralones) {
    if (!leafletCorralonMap || !Array.isArray(corralones)) return;

    corralonMarkers.forEach(m => {
        try { leafletCorralonMap.removeLayer(m); } catch (e) {}
    });
    corralonMarkers = [];

    corralones.forEach(c => {
        const iconHtml = `<div class="marker-pin marker-corralon" title="${c.nombre}">🏛️</div>`;
        const customIcon = L.divIcon({
            className: 'custom-map-marker',
            html: iconHtml,
            iconSize: [40, 40],
            iconAnchor: [20, 40],
            popupAnchor: [0, -35]
        });

        const marker = L.marker([c.lat, c.lng], { icon: customIcon }).addTo(leafletCorralonMap);

        const popupHtml = `
            <div class="map-popup-card">
                <div class="popup-header">
                    <span class="popup-badge badge-${(c.zona || 'centro').toLowerCase()}">${c.zona || 'Centro'}</span>
                    <span class="popup-live">🟢 Abierto 24h</span>
                </div>
                <h4 class="popup-title">🏛️ ${c.nombre}</h4>
                <p class="popup-address">📍 ${c.direccion}</p>
                <p class="popup-ref">🚩 Ref: ${c.referencia || 'Depósito oficial'}</p>
                <div class="popup-meta">
                    <span>📞 ${c.telefono || '55 5242 5100'}</span><br>
                    <span>📦 Capacidad: ${c.capacidad || '400 vehículos'}</span>
                </div>
                <div class="popup-actions">
                    <a href="https://www.google.com/maps/search/?api=1&query=${c.lat},${c.lng}" 
                       target="_blank" 
                       rel="noopener" 
                       class="btn btn-sm btn-primary">
                        🗺️ Ver ruta en Google Maps
                    </a>
                </div>
            </div>
        `;

        marker.bindPopup(popupHtml);
        marker.on('click', () => {
            if (window.gpmvAudio) window.gpmvAudio.playNotification();
        });

        marker.corralonData = c;
        corralonMarkers.push(marker);
    });
}

function focusCorralon(lat, lng, nombre) {
    if (!leafletCorralonMap) return;
    if (window.gpmvAudio) window.gpmvAudio.playClick();
    leafletCorralonMap.flyTo([lat, lng], 15, { duration: 1.2 });

    const marker = corralonMarkers.find(m => m.corralonData && m.corralonData.nombre === nombre);
    if (marker) {
        setTimeout(() => marker.openPopup(), 600);
    }
}

function filterByZone(zone, button) {
    if (window.gpmvAudio) window.gpmvAudio.playClick();
    document.querySelectorAll('.zone-pill').forEach(b => b.classList.remove('active'));
    if (button) button.classList.add('active');

    const cards = document.querySelectorAll('.corralon-item-card');
    let visibleCount = 0;

    cards.forEach(card => {
        const cZone = card.getAttribute('data-zone') || '';
        if (zone === 'all' || cZone.toLowerCase() === zone.toLowerCase()) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    const countElem = document.getElementById('corralonCount');
    if (countElem) countElem.textContent = visibleCount;

    corralonMarkers.forEach(marker => {
        const data = marker.corralonData || {};
        const mZone = (data.zona || '').toLowerCase();
        if (zone === 'all' || mZone === zone.toLowerCase()) {
            if (!leafletCorralonMap.hasLayer(marker)) leafletCorralonMap.addLayer(marker);
        } else {
            if (leafletCorralonMap.hasLayer(marker)) leafletCorralonMap.removeLayer(marker);
        }
    });
}

function filterCorralones() {
    const input = document.getElementById('corralonSearchInput');
    const query = (input ? input.value : '').toLowerCase().trim();
    const cards = document.querySelectorAll('.corralon-item-card');
    let visibleCount = 0;

    cards.forEach(card => {
        const name = (card.getAttribute('data-name') || '').toLowerCase();
        const address = card.innerText.toLowerCase();
        if (name.includes(query) || address.includes(query)) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    const countElem = document.getElementById('corralonCount');
    if (countElem) countElem.textContent = visibleCount;

    corralonMarkers.forEach(marker => {
        const data = marker.corralonData || {};
        const match = (data.nombre || '').toLowerCase().includes(query) || (data.direccion || '').toLowerCase().includes(query);
        if (match) {
            if (!leafletCorralonMap.hasLayer(marker)) leafletCorralonMap.addLayer(marker);
        } else {
            if (leafletCorralonMap.hasLayer(marker)) leafletCorralonMap.removeLayer(marker);
        }
    });
}

function locateUserPosition() {
    if (!leafletCorralonMap) return;
    if (window.gpmvAudio) window.gpmvAudio.playNotification();

    const userLat = 19.4326;
    const userLng = -99.1332;

    if (userLocationMarker) {
        try { leafletCorralonMap.removeLayer(userLocationMarker); } catch (e) {}
    }

    const userIcon = L.divIcon({
        className: 'custom-map-marker',
        html: '<div class="marker-pin marker-user" title="Tu ubicación">📍</div>',
        iconSize: [40, 40],
        iconAnchor: [20, 40]
    });

    userLocationMarker = L.marker([userLat, userLng], { icon: userIcon }).addTo(leafletCorralonMap);
    userLocationMarker.bindPopup(`
        <div style="font-family:'Segoe UI',sans-serif;">
            <h4 style="color:#1a3d7c; margin-bottom:4px;">📍 Tu Ubicación Actual</h4>
            <p style="font-size:12px; margin:0;">Zócalo / Centro Histórico, CDMX</p>
            <small style="color:#666;">Calculando distancias a depósitos vehiculares...</small>
        </div>
    `).openPopup();

    leafletCorralonMap.flyTo([userLat, userLng], 13, { duration: 1 });
}

function resetMapView() {
    if (!leafletCorralonMap) return;
    if (window.gpmvAudio) window.gpmvAudio.playClick();
    leafletCorralonMap.flyTo([19.4326, -99.1332], 11, { duration: 1 });
}

/* ============================================================
   4. MAPA INDIVIDUAL EN DETALLE DE MULTA
   ============================================================ */
let singleLeafletMap = null;

function initSingleCorralonMap() {
    const el = document.getElementById('singleCorralonMap');
    if (!el || typeof L === 'undefined') return;

    if (singleLeafletMap) {
        try { singleLeafletMap.remove(); } catch (e) {}
        singleLeafletMap = null;
    }

    const lat = parseFloat(el.getAttribute('data-lat')) || 19.3734;
    const lng = parseFloat(el.getAttribute('data-lng')) || -99.1795;
    const corralon = el.getAttribute('data-corralon') || 'Depósito Vehicular CDMX';
    const direccion = el.getAttribute('data-direccion') || 'Ciudad de México';
    const area = el.getAttribute('data-area') || 'A-01';

    singleLeafletMap = L.map('singleCorralonMap', {
        center: [lat, lng],
        zoom: 15,
        scrollWheelZoom: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors &bull; GPMV CDMX'
    }).addTo(singleLeafletMap);

    const customIcon = L.divIcon({
        className: 'custom-map-marker',
        html: '<div class="marker-pin marker-corralon">🏛️</div>',
        iconSize: [40, 40],
        iconAnchor: [20, 40]
    });

    const marker = L.marker([lat, lng], { icon: customIcon }).addTo(singleLeafletMap);
    marker.bindPopup(`
        <div style="font-family:'Segoe UI',sans-serif; min-width: 200px;">
            <h4 style="color: #7b1e3a; margin-bottom: 4px;">🏛️ ${corralon}</h4>
            <p style="font-size: 13px; margin: 4px 0;">📍 ${direccion}</p>
            <p style="font-size: 12px; color: #1a3d7c; font-weight: bold; margin: 4px 0;">Área asignada: ${area}</p>
            <small style="color: #666;">Horario: 24 horas continuas</small>
        </div>
    `).openPopup();
}

/* ============================================================
   AUTO-INICIALIZACIÓN GLOBAL
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar video player si existe el canvas
    if (document.getElementById('videoCanvas')) {
        window.gpmvPlayerInstance = new GPMVVideoPlayer();
    }

    // Inicializar mapa general si existe el contenedor
    if (document.getElementById('corralonMap')) {
        initCorralonMap();
    }

    // Inicializar mapa de detalle si existe
    if (document.getElementById('singleCorralonMap')) {
        initSingleCorralonMap();
    }
});
