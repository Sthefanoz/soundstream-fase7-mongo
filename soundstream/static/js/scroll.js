/* =========================================================
   SoundStream - Animaciones de scroll
   - Reveal con IntersectionObserver
   - Counter animado
   - Parallax suave
   - Nav que se condensa al hacer scroll
   - Scroll-video (efecto Apple) opcional si hay #heroVideo
   ========================================================= */

(function () {
    'use strict';

    // ------------ Reveal ------------
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale')
        .forEach((el) => observer.observe(el));

    // stagger index
    document.querySelectorAll('[data-stagger]').forEach((group) => {
        Array.from(group.children).forEach((child, i) => {
            child.style.setProperty('--i', i);
        });
    });

    // ------------ Counter ------------
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const el = entry.target;
            const target = parseFloat(el.dataset.count || '0');
            const suffix = el.dataset.suffix || '';
            const duration = 1800;
            const start = performance.now();
            function tick(now) {
                const p = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - p, 3);
                const value = Math.floor(target * eased);
                el.textContent = formatNumber(value) + suffix;
                if (p < 1) requestAnimationFrame(tick);
                else el.textContent = formatNumber(target) + suffix;
            }
            requestAnimationFrame(tick);
            counterObserver.unobserve(el);
        });
    }, { threshold: 0.5 });
    document.querySelectorAll('[data-count]').forEach((el) => counterObserver.observe(el));

    function formatNumber(n) {
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1) + 'M';
        if (n >= 1_000) return (n / 1_000).toFixed(n % 1_000 === 0 ? 0 : 1) + 'k';
        return n.toString();
    }

    // ------------ Nav scrolled ------------
    const nav = document.querySelector('.nav');
    if (nav) {
        const onScroll = () => {
            if (window.scrollY > 30) nav.classList.add('scrolled');
            else nav.classList.remove('scrolled');
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // ------------ Burger ------------
    const burger = document.querySelector('.burger');
    const links = document.querySelector('.nav-links');
    if (burger && links) {
        burger.addEventListener('click', () => links.classList.toggle('open'));
    }

    // ------------ Parallax ------------
    const parallaxEls = document.querySelectorAll('[data-parallax]');
    if (parallaxEls.length) {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(() => {
                const sy = window.scrollY;
                parallaxEls.forEach((el) => {
                    const speed = parseFloat(el.dataset.parallax) || 0.3;
                    const rect = el.getBoundingClientRect();
                    const offset = (sy - (sy + rect.top - window.innerHeight)) * speed;
                    el.style.transform = `translate3d(0, ${offset * 0.05}px, 0)`;
                });
                ticking = false;
            });
        }, { passive: true });
    }

    // ------------ Orbes que respiran con el scroll ------------
    const orbs = document.querySelectorAll('.orb');
    if (orbs.length) {
        window.addEventListener('scroll', () => {
            const sy = window.scrollY;
            orbs.forEach((o, i) => {
                o.style.transform = `translate3d(${Math.sin(sy * 0.002 + i) * 30}px, ${sy * (0.06 + i * 0.02)}px, 0)`;
            });
        }, { passive: true });
    }

    // ------------ Bg text parallax horizontal ------------
    const bgTexts = document.querySelectorAll('.parallax-band .bg-text');
    bgTexts.forEach((t) => {
        const band = t.closest('.parallax-band');
        window.addEventListener('scroll', () => {
            const rect = band.getBoundingClientRect();
            const center = window.innerHeight / 2 - (rect.top + rect.height / 2);
            t.style.transform = `translate(calc(-50% + ${center * 0.4}px), -50%)`;
        }, { passive: true });
    });

    // ------------ Scroll Video (efecto Apple) ------------
    const video = document.getElementById('heroVideo');
    const hero = document.getElementById('scroll-hero');
    const progressFill = document.getElementById('progressFill');
    if (video && hero) {
        const isMobile = window.matchMedia('(max-width: 768px)').matches;
        const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (isMobile || prefersReduced) {
            video.autoplay = true;
            video.loop = true;
            video.muted = true;
            video.play().catch(() => {});
        } else {
            video.pause();
            video.currentTime = 0;
            let isReady = false;
            video.addEventListener('loadedmetadata', () => { isReady = true; });
            video.load();

            function updateVideo() {
                if (!isReady || !video.duration) return;
                const rect = hero.getBoundingClientRect();
                const scrolled = -rect.top;
                const scrollable = hero.offsetHeight - window.innerHeight;
                if (scrolled <= 0) {
                    video.currentTime = 0;
                    if (progressFill) progressFill.style.width = '0%';
                    return;
                }
                if (scrolled >= scrollable) {
                    video.currentTime = video.duration;
                    if (progressFill) progressFill.style.width = '100%';
                    return;
                }
                const progress = scrolled / scrollable;
                video.currentTime = progress * video.duration;
                if (progressFill) progressFill.style.width = (progress * 100) + '%';
            }
            let t = false;
            window.addEventListener('scroll', () => {
                if (!t) {
                    requestAnimationFrame(() => { updateVideo(); t = false; });
                    t = true;
                }
            }, { passive: true });
            window.addEventListener('resize', updateVideo);
        }
    }

    // ------------ Reproductor persistente (mini-player) ------------
    const audio = document.getElementById('reproductor-audio');
    const bar = document.getElementById('player-bar');
    const elTitulo = document.getElementById('player-title');
    const elArtista = document.getElementById('player-artist');
    const elToggle = document.getElementById('player-toggle');
    const elClose = document.getElementById('player-close');
    const elCur = document.getElementById('player-cur');
    const elDur = document.getElementById('player-dur');
    const elTrack = document.getElementById('player-track');
    const elFill = document.getElementById('player-fill');
    let botonActual = null;

    function fmt(seg) {
        if (!isFinite(seg) || seg < 0) seg = 0;
        const m = Math.floor(seg / 60), s = Math.floor(seg % 60);
        return m + ':' + (s < 10 ? '0' + s : s);
    }

    function pintarToggle() {
        const sonando = audio && !audio.paused && audio.src;
        if (elToggle) {
            elToggle.innerHTML = sonando ? '&#9208;' : '&#9654;';  // pausa / play
            elToggle.classList.toggle('play', !sonando);
        }
        if (bar) bar.classList.toggle('playing', !!sonando);
        if (botonActual) botonActual.classList.toggle('playing', !!sonando);
    }

    function detener() {
        if (audio) audio.pause();
        if (botonActual) botonActual.classList.remove('playing', 'loading');
        if (bar) bar.classList.remove('playing');
        pintarToggle();
    }

    if (audio) {
        audio.addEventListener('ended', function () {
            if (botonActual) botonActual.classList.remove('playing');
            if (elFill) elFill.style.width = '0%';
            pintarToggle();
        });
        audio.addEventListener('timeupdate', function () {
            if (audio.duration && elFill) {
                elFill.style.width = (audio.currentTime / audio.duration * 100) + '%';
            }
            if (elCur) elCur.textContent = fmt(audio.currentTime);
        });
        audio.addEventListener('loadedmetadata', function () {
            if (elDur) elDur.textContent = fmt(audio.duration);
        });
        audio.addEventListener('play', pintarToggle);
        audio.addEventListener('pause', pintarToggle);
    }

    if (elToggle) elToggle.addEventListener('click', function () {
        if (!audio || !audio.src) return;
        if (audio.paused) audio.play(); else audio.pause();
    });
    if (elClose) elClose.addEventListener('click', function () {
        detener();
        botonActual = null;
        if (bar) bar.classList.remove('visible');
    });
    if (elTrack) elTrack.addEventListener('click', function (e) {
        if (!audio || !audio.duration) return;
        const rect = elTrack.getBoundingClientRect();
        audio.currentTime = ((e.clientX - rect.left) / rect.width) * audio.duration;
    });

    // Pide a Deezer una preview fresca (las URLs guardadas caducan). Si falla
    // -por falta de internet- cae a la preview que venia en el boton.
    async function previewFresca(btn) {
        const playUrl = btn.dataset.playSong;
        if (playUrl) {
            try {
                const r = await fetch(playUrl.replace('/play/', '/preview/'));
                const data = await r.json();
                if (data.preview) return data.preview;
            } catch (_) { /* sin red: usar la guardada */ }
        }
        return btn.dataset.preview || '';
    }

    document.querySelectorAll('[data-play-song]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            // Si es la cancion actual -> alternar play/pausa
            if (botonActual === btn && audio && audio.src) {
                if (audio.paused) audio.play(); else audio.pause();
                return;
            }

            detener();
            botonActual = btn;

            // Muestra la barra con la info de la cancion y el estado de carga.
            if (elTitulo) elTitulo.textContent = btn.dataset.titulo || 'Reproduciendo';
            if (elArtista) elArtista.textContent = btn.dataset.artista || '';
            if (elFill) elFill.style.width = '0%';
            if (elCur) elCur.textContent = '0:00';
            if (bar) bar.classList.add('visible');
            btn.classList.add('loading');

            const preview = await previewFresca(btn);
            btn.classList.remove('loading');

            // Reproducir la preview (si hay y el navegador soporta audio)
            if (audio && preview) {
                audio.src = preview;
                audio.load();
                audio.play().then(() => {
                    btn.classList.add('playing');
                    pintarToggle();
                }).catch((err) => {
                    flashToast('Error de audio: ' + (err.message || err.name));
                });
            } else if (!preview) {
                flashToast('Sin audio de muestra disponible.');
            }

            // Registrar la reproduccion en la BD (CRUD via stored procedure)
            const url = btn.dataset.playSong;
            if (!url) return;
            try {
                const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                const r = await fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrf || '' },
                });
                const data = await r.json();
                if (!data.ok) {
                    flashToast('Inicia sesion para guardar tu reproduccion.');
                }
            } catch (_) {
                flashToast('Inicia sesion para guardar tu reproduccion.');
            }
        });
    });

    function flashToast(msg) {
        const t = document.createElement('div');
        t.textContent = msg;
        Object.assign(t.style, {
            position: 'fixed', bottom: '24px', left: '50%',
            transform: 'translateX(-50%)',
            background: '#101019', color: '#fff',
            padding: '12px 20px', borderRadius: '999px',
            border: '1px solid rgba(255,255,255,0.1)',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
            zIndex: 9999, fontSize: '0.9rem',
        });
        document.body.appendChild(t);
        setTimeout(() => { t.style.transition = 'opacity 0.4s'; t.style.opacity = 0; }, 1800);
        setTimeout(() => t.remove(), 2400);
    }
})();
