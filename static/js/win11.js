/* ============================================================
   VacancyMonitor — Fluent interactions
   ============================================================ */
(function () {
    'use strict';

    document.documentElement.classList.add('js');

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ---------- Fluent reveal: highlight follows the cursor ---------- */
    if (!reduced) {
        document.querySelectorAll('.vacancy-card').forEach(function (card) {
            card.addEventListener('pointermove', function (e) {
                var r = card.getBoundingClientRect();
                card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
                card.style.setProperty('--my', (e.clientY - r.top) + 'px');
            });
        });
    }

    /* ---------- Scroll reveal ---------- */
    var targets = document.querySelectorAll('.reveal-on-scroll');
    if ('IntersectionObserver' in window && targets.length) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (en) {
                if (en.isIntersecting) {
                    en.target.classList.add('in');
                    io.unobserve(en.target);
                }
            });
        }, { threshold: 0.12 });
        targets.forEach(function (el) { io.observe(el); });
    } else {
        targets.forEach(function (el) { el.classList.add('in'); });
    }

    /* ---------- Animated counter ---------- */
    document.querySelectorAll('[data-count]').forEach(function (el) {
        var target = parseInt(el.getAttribute('data-count'), 10) || 0;
        if (reduced) { el.textContent = String(target); return; }
        var start = performance.now(), dur = 1100;
        (function tick(t) {
            var p = Math.min(1, (t - start) / dur);
            var eased = 1 - Math.pow(1 - p, 3);
            el.textContent = String(Math.round(target * eased));
            if (p < 1) requestAnimationFrame(tick);
        })(start);
    });

    /* ---------- Taskbar-style clock ---------- */
    var clock = document.getElementById('clock');
    if (clock) {
        var tickClock = function () {
            clock.textContent = new Date().toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
        };
        tickClock();
        setInterval(tickClock, 10000);
    }

    /* ---------- "/" focuses search ---------- */
    var search = document.getElementById('search');
    if (search) {
        document.addEventListener('keydown', function (e) {
            var tag = (document.activeElement && document.activeElement.tagName) || '';
            if (e.key === '/' && !/INPUT|SELECT|TEXTAREA/.test(tag)) {
                e.preventDefault();
                search.focus();
            }
            if (e.key === 'Escape' && document.activeElement === search) {
                search.blur();
            }
        });
    }
})();
