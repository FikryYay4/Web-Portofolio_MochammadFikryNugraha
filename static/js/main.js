// ---- SAFE LOADER HIDE (runs before anything else) ----
(function() {
    var loader = document.getElementById('loader');
    function hide() { if (loader) { loader.style.opacity = '0'; loader.style.visibility = 'hidden'; } }
    setTimeout(hide, 3000);
    if (document.readyState === 'complete') { setTimeout(hide, 100); }
    window.addEventListener('load', function() { setTimeout(hide, 500); });
})();

// Initialize Lenis Smooth Scroll (safe)
var lenis = null;
try {
    if (typeof Lenis !== 'undefined') {
        lenis = new Lenis({
            duration: 1.2,
            easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
            smoothWheel: true
        });
        function raf(time) {
            if (lenis) lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
    }
} catch(e) {}

function stopLenis() { try { if (lenis) lenis.stop(); } catch(e) {} }
function startLenis() { try { if (lenis) lenis.start(); } catch(e) {} }

document.addEventListener('DOMContentLoaded', function() {

    // ---- GSAP-dependent features ----
    if (typeof gsap !== 'undefined') {
        try { gsap.registerPlugin(ScrollTrigger); } catch(e) {}
        try { lenis.on('scroll', ScrollTrigger.update); } catch(e) {}
    }

    // Hero entrance if GSAP available and hero elements exist
    if (typeof gsap !== 'undefined' && document.querySelector('.hero__greeting')) {
        try {
            const tl = gsap.timeline();
            tl.from('.hero__greeting', { opacity: 0, y: 20, duration: 0.6, ease: 'power2.out' })
              .from('.hero__name', { opacity: 0, y: 30, duration: 0.8, ease: 'power3.out' }, '-=0.4')
              .from('.hero__headline', { opacity: 0, y: 20, duration: 0.6, ease: 'power2.out' }, '-=0.5')
              .from('.hero__description', { opacity: 0, y: 20, duration: 0.6, ease: 'power2.out' }, '-=0.5')
              .from('.hero__cta .btn', { opacity: 0, y: 15, stagger: 0.15, duration: 0.5, ease: 'power2.out' }, '-=0.4')
              .from('.hero__avatar-wrapper', { opacity: 0, scale: 0.9, duration: 1, ease: 'power2.out' }, '-=0.6')
              .from('.hero__scroll', { opacity: 0, y: -10, duration: 0.5, ease: 'power2.out' }, '-=0.3');
        } catch(e) {}
    }

    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar--scrolled');
        } else {
            navbar.classList.remove('navbar--scrolled');
        }
    });

    // Mobile Navigation Hamburger
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            const expanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !expanded);
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }

    // Interactive 3D Orbit Particles on Hero Visual Canvas
    initHeroParticles();

    // GSAP Scroll + Reveal Animations
    if (typeof gsap !== 'undefined') {
        try {
            gsap.utils.toArray('.reveal').forEach(elem => {
                gsap.from(elem, {
                    scrollTrigger: {
                        trigger: elem,
                        start: 'top 85%',
                        toggleActions: 'play none none none'
                    },
                    opacity: 0,
                    y: 40,
                    duration: 0.8,
                    ease: 'power2.out'
                });
            });
        } catch(e) {}
    }

    if (typeof gsap !== 'undefined') {
        try {
            const layerCards = gsap.utils.toArray('.layer-card');
            if (layerCards.length > 0) {
                layerCards.forEach((card, i) => {
                    if (i === layerCards.length - 1) return;
                    gsap.to(card, {
                        scrollTrigger: {
                            trigger: card,
                            start: 'top 15%',
                            endTrigger: layerCards[layerCards.length - 1],
                            end: 'top 15%',
                            scrub: true
                        },
                        scale: 1 - ((layerCards.length - i) * 0.05),
                        y: -30,
                        opacity: 0.5,
                        transformOrigin: "top center",
                        ease: "none"
                    });
                });
            }
        } catch(e) {}

        try {
            const sections = gsap.utils.toArray('.section');
            sections.forEach((section, i) => {
                const wrapper = section.querySelector('.container');
                if (!wrapper) return;
                gsap.fromTo(wrapper,
                    { autoAlpha: 0, y: 80, scale: 0.92, rotationX: 12, transformOrigin: '50% 0%', filter: 'blur(4px)' },
                    {
                        autoAlpha: 1, y: 0, scale: 1, rotationX: 0, filter: 'blur(0px)',
                        duration: 1.2,
                        ease: 'power4.out',
                        scrollTrigger: {
                            trigger: section,
                            start: 'top 90%',
                            end: 'top 40%',
                            toggleActions: 'play none none reverse',
                        }
                    }
                );
                const bg = section.querySelector('.hero__bg');
                if (bg) {
                    gsap.to(bg, {
                        scrollTrigger: {
                            trigger: section,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: true
                        },
                        y: -40,
                        scale: 1.05,
                        ease: 'none'
                    });
                }
            });
        } catch(e) {}
    }

    // Counter Animation
    animateCounters();

    // Skill Modal Interaction
    initSkillModal();

    // Back to top behavior
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            try { lenis.scrollTo('#hero', { duration: 1.5 }); } catch(e) { window.location.hash = '#hero'; }
        });
    }

    // Smooth scroll for nav link anchors
    document.querySelectorAll('.navbar__link, .hero__cta a, .navbar__logo').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const targetId = anchor.getAttribute('href');
            if (targetId.startsWith('#')) {
                e.preventDefault();
                try { lenis.scrollTo(targetId, { duration: 1.2 }); } catch(e) { window.location.hash = targetId; }

                // Active link tracking
                document.querySelectorAll('.navbar__link').forEach(l => l.classList.remove('active'));
                if (anchor.classList.contains('navbar__link')) {
                    anchor.classList.add('active');
                }

                // Close mobile menu if open
                if (navLinks && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    hamburger.classList.remove('active');
                    hamburger.setAttribute('aria-expanded', false);
                }
            }
        });
    });

    // Active Section Link Observer
    const sections = document.querySelectorAll('section');
    const navItems = document.querySelectorAll('.navbar__link');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    });
});

// Counter Animation for About section
function animateCounters() {
    const counters = document.querySelectorAll('.about__counter-num');
    if (!counters.length) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count')) || 0;
                let current = 0;
                const step = Math.max(1, Math.ceil(target / 60));
                const interval = setInterval(() => {
                    current += step;
                    if (current >= target) {
                        el.textContent = target;
                        clearInterval(interval);
                    } else {
                        el.textContent = current;
                    }
                }, 25);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    counters.forEach(el => observer.observe(el));
}

// Canvas Particle System - sparks/embers rising from bottom
function initHeroParticles() {
    const canvas = document.getElementById('heroCanvas');
    const backCanvas = document.getElementById('heroCanvasBack');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.offsetWidth;
    let height = canvas.offsetHeight;

    canvas.width = width;
    canvas.height = height;
    if (backCanvas) { backCanvas.width = width; backCanvas.height = height; }

    const cx = width / 2;
    const cy = height / 2;
    const colors = ['#22D3EE', '#06B6D4', '#67E8F9'];
    const maxParticles = 60;

    let mouseX = cx, mouseY = cy;
    let targetMX = cx, targetMY = cy;

    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        targetMX = e.clientX - rect.left;
        targetMY = e.clientY - rect.top;
    });
    canvas.addEventListener('mouseleave', () => { targetMX = cx; targetMY = cy; });

    class Spark {
        constructor() {
            this.reset(true);
        }
        reset(initial) {
            this.x = cx + (Math.random() - 0.5) * 160;
            this.y = height + 10 + Math.random() * 20;
            this.size = Math.random() * 2.5 + 1;
            this.speedY = -(Math.random() * 1.2 + 0.6);
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.color = colors[Math.floor(Math.random() * colors.length)];
            this.alpha = Math.random() * 0.25 + 0.1;
            this.life = 1;
            this.decay = Math.random() * 0.006 + 0.004;
            this.wobble = Math.random() * 0.02;
            this.wobbleAmp = Math.random() * 10 + 5;
            this.wobblePhase = Math.random() * Math.PI * 2;
        }
        update(time) {
            this.y += this.speedY;
            this.x += this.speedX + Math.sin(time * this.wobble + this.wobblePhase) * 0.3;
            this.life -= this.decay;
            this.alpha = this.life * 0.3;
            if (this.life <= 0 || this.y < -20) this.reset(false);
        }
        draw() {
            ctx.save();
            ctx.globalAlpha = Math.max(0, this.alpha);
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 15;
            ctx.shadowColor = this.color;
            ctx.fill();
            ctx.restore();
        }
    }

    const sparks = [];
    for (let i = 0; i < maxParticles; i++) {
        const s = new Spark();
        s.y = Math.random() * height;
        s.life = Math.random();
        sparks.push(s);
    }

    let time = 0;

    function animate() {
        time += 0.02;
        ctx.clearRect(0, 0, width, height);
        mouseX += (targetMX - mouseX) * 0.05;
        mouseY += (targetMY - mouseY) * 0.05;

        sparks.forEach(s => {
            s.update(time);
            s.draw();
        });
        requestAnimationFrame(animate);
    }
    animate();

    window.addEventListener('resize', () => {
        width = canvas.offsetWidth;
        height = canvas.offsetHeight;
        canvas.width = width;
        canvas.height = height;
        if (backCanvas) { backCanvas.width = width; backCanvas.height = height; }
    });
}

// Certificate Modal Lightbox
function openCertModal(img) {
    const modal = document.getElementById('certModal');
    const modalImg = document.getElementById('certModalImg');
    if (!modal || !modalImg) return;
    modalImg.src = img.src;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
}
function closeCertModal(e) {
    const modal = document.getElementById('certModal');
    if (!modal) return;
    if (e && e.target !== modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
}
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        var projModal = document.getElementById('projectModal');
        if (projModal && projModal.classList.contains('active')) return;
        var certModal = document.getElementById('certModal');
        if (certModal && certModal.classList.contains('active')) closeCertModal();
        var skillModal = document.getElementById('skillModal');
        if (skillModal && skillModal.classList.contains('active')) { skillModal.classList.remove('active'); skillModal.setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; }
    }
});

var scrollPos = 0;
function lockScroll() {
    scrollPos = window.pageYOffset || document.documentElement.scrollTop;
    document.body.style.position = 'fixed';
    document.body.style.top = '-' + scrollPos + 'px';
    document.body.style.left = '0';
    document.body.style.width = '100%';
}
function unlockScroll() {
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.width = '';
    window.scrollTo(0, scrollPos);
}

// ---- Carousel State ----
var C = { files: [], current: 0, total: 0, isDragging: false, startX: 0, startY: 0, dragOffset: 0, zoomed: false };

function initCarouselDrag() {
    var track = document.getElementById('carouselTrack');
    if (!track) return;

    var viewport = track.parentElement;
    function sw() { return viewport ? viewport.offsetWidth : window.innerWidth; }

    function down(e) {
        var modal = document.getElementById('projectModal');
        if (!modal || !modal.classList.contains('active')) return;
        if (C.zoomed) return;
        C.isDragging = true;
        C.startX = e.clientX || (e.touches && e.touches[0].clientX);
        C.startY = e.clientY || (e.touches && e.touches[0].clientY);
        C.dragOffset = 0;
        track.classList.add('dragging');
        track.style.cursor = 'grabbing';
    }

    function move(e) {
        if (!C.isDragging) return;
        var cx = e.clientX || (e.touches && e.touches[0].clientX);
        var cy = e.clientY || (e.touches && e.touches[0].clientY);
        var dx = cx - C.startX;
        var dy = cy - C.startY;
        if (Math.abs(dx) < Math.abs(dy) * 0.5) {
            C.isDragging = false;
            track.classList.remove('dragging');
            return;
        }
        e.preventDefault();
        C.dragOffset = dx;
        var vw = sw();
        track.style.transform = 'translateX(' + (-C.current * vw + dx) + 'px)';
    }

    function up() {
        if (!C.isDragging) return;
        C.isDragging = false;
        track.classList.remove('dragging');
        track.style.cursor = '';
        var vw = sw();
        var s = C.dragOffset;
        if (s < -vw * 0.18 && C.current < C.total - 1) { C.current++; }
        else if (s > vw * 0.18 && C.current > 0) { C.current--; }
        C.dragOffset = 0;
        updateCarouselUI();
    }

    track.addEventListener('mousedown', down);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    track.addEventListener('touchstart', down, { passive: true });
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', up);
    window.addEventListener('resize', function() {
        if (document.getElementById('projectModal').classList.contains('active')) updateCarouselUI();
    });
}

function openProjectModal(el) {
    var parent = el.classList.contains('project-card__image') ? el : el.closest('.project-card__image');
    if (!parent) return;
    var raw = parent.getAttribute('data-files');
    var files = [];
    try { files = JSON.parse(raw); } catch(e) { files = []; }
    if (!files || !files.length) return;
    var title = parent.getAttribute('data-title') || '';

    C.files = files;
    C.current = 0;
    C.total = files.length;
    C.zoomed = false;

    var modal = document.getElementById('projectModal');
    var track = document.getElementById('carouselTrack');
    var dots = document.getElementById('carouselDots');
    var counter = document.getElementById('carouselCounter');
    if (!modal || !track) return;

    track.innerHTML = '';
    if (dots) dots.innerHTML = '';

    files.forEach(function(fname, i) {
        var slide = document.createElement('div');
        slide.className = 'project-carousel__slide';
        var video = fname.toLowerCase().endsWith('.mp4');
        if (video) {
            var v = document.createElement('video');
            v.src = '/static/uploads/' + fname;
            v.autoplay = true; v.loop = true; v.muted = true; v.playsInline = true;
            v.style.maxWidth = '100%'; v.style.maxHeight = '70vh'; v.style.borderRadius = '12px';
            slide.appendChild(v);
        } else {
            var img = document.createElement('img');
            img.loading = 'eager';
            img.alt = title;
            img.style.display = 'block';
            img.style.maxWidth = '100%'; img.style.maxHeight = '70vh'; img.style.objectFit = 'contain';
            img.style.borderRadius = '12px'; img.style.boxShadow = '0 20px 60px rgba(0,0,0,0.5)';
            img.style.pointerEvents = 'none';
            var isFirst = i === 0 || fname.indexOf('/') !== -1;
            img.src = isFirst ? '/static/uploads/' + fname : '/static/uploads/project_images/' + fname;
            img.onerror = function() {
                this.onerror = null;
                this.src = isFirst ? '/static/uploads/project_images/' + fname : '/static/uploads/' + fname;
            };
            slide.appendChild(img);
        }
        slide.addEventListener('click', function(e) {
            if (C.isDragging) return;
            if (video) return;
            var img = this.querySelector('img');
            if (!img) return;
            C.zoomed = !C.zoomed;
            modal.classList.toggle('zoom', C.zoomed);
        });
        track.appendChild(slide);

        if (dots) {
            var dot = document.createElement('button');
            dot.className = 'project-carousel__dot' + (i === 0 ? ' project-carousel__dot--active' : '');
            dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
            (function(idx) { dot.addEventListener('click', function() { carouselGoTo(idx); }); })(i);
            dots.appendChild(dot);
        }
    });

    if (counter) counter.textContent = '1 / ' + files.length;
    modal.removeAttribute('data-title');
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    updateCarouselUI();
}

function closeProjectModal(e) {
    var modal = document.getElementById('projectModal');
    if (!modal) return;
    if (e && e.target !== modal) return;
    modal.classList.remove('active', 'zoom');
    modal.setAttribute('aria-hidden', 'true');
    C.zoomed = false;
    if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
    var track = document.getElementById('carouselTrack');
    if (track) track.style.transform = '';
}

function updateCarouselUI() {
    var track = document.getElementById('carouselTrack');
    var dots = document.getElementById('carouselDots');
    var counter = document.getElementById('carouselCounter');
    if (!track) return;
    var vp = track.parentElement;
    var vw = vp ? vp.offsetWidth : window.innerWidth;
    track.style.transform = 'translateX(' + (-C.current * vw + (C.dragOffset || 0)) + 'px)';
    if (dots) {
        Array.from(dots.children).forEach(function(d, i) {
            d.className = 'project-carousel__dot' + (i === C.current ? ' project-carousel__dot--active' : '');
        });
    }
    if (counter) counter.textContent = (C.current + 1) + ' / ' + C.total;
}

function carouselGoTo(idx) {
    if (C.zoomed) { C.zoomed = false; document.getElementById('projectModal').classList.remove('zoom'); }
    if (idx < 0) idx = 0;
    if (idx >= C.total) idx = C.total - 1;
    C.current = idx;
    C.dragOffset = 0;
    updateCarouselUI();
}

window.prevSlide = function() { carouselGoTo(C.current - 1); };
window.nextSlide = function() { carouselGoTo(C.current + 1); };

initCarouselDrag();

document.addEventListener('keydown', function(e) {
    var modal = document.getElementById('projectModal');
    if (!modal.classList.contains('active')) return;
    if (e.key === 'Escape') {
        if (C.zoomed) { C.zoomed = false; modal.classList.remove('zoom'); e.preventDefault(); return; }
        closeProjectModal();
        return;
    }
    if (C.zoomed) return;
    if (e.key === 'ArrowLeft') { window.prevSlide(); e.preventDefault(); }
    if (e.key === 'ArrowRight') { window.nextSlide(); e.preventDefault(); }
});

// Skill Modal Interaction
function initSkillModal() {
    const modal = document.getElementById('skillModal');
    if (!modal) return;

    const cards = document.querySelectorAll('.skill-card');
    const closeBtn = modal.querySelector('.modal-close');
    const mIcon = modal.querySelector('.modal-icon');
    const mTitle = modal.querySelector('.modal-title');
    const mBody = modal.querySelector('.modal-body');

    function openModal(data) {
        mTitle.textContent = data.name;

        let iconHtml = '';
        if (data.icon && data.icon.includes('.svg')) {
            const svgPath = `/static/assets/svg/${data.icon}`;
            iconHtml = `<img src="${svgPath}" alt="${data.name}">`;
        } else {
            iconHtml = `<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/></svg>`;
        }
        mIcon.innerHTML = iconHtml;

        let softwareList = '';
        if (data.software && data.software.length > 0) {
            softwareList = `
                <h4>Tools & Technologies</h4>
                <ul>
                    ${data.software.map(sw => `<li>${sw}</li>`).join('')}
                </ul>
            `;
        }

        let certList = '';
        if (data.certificates && data.certificates.length > 0) {
            const toeflToeicCerts = [];
            const otherCerts = [];
            data.certificates.forEach(cert => {
                if (cert.includes('TOEFL') || cert.includes('TOEIC')) {
                    toeflToeicCerts.push(cert);
                } else {
                    otherCerts.push(cert);
                }
            });

            let certHtml = '';
            if (toeflToeicCerts.length > 0) {
                certHtml += `<h4>Language Proficiency</h4><ul>${toeflToeicCerts.map(cert => {
                    if (cert.includes('TOEFL')) {
                        return `<li><a href="/static/uploads/certificates/toefl.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline;">${cert}</a></li>`;
                    }
                    return `<li><a href="/static/uploads/certificates/toeic.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline;">${cert}</a></li>`;
                }).join('')}</ul>`;
            }
            if (otherCerts.length > 0) {
                certHtml += `<h4>Certificates & Credentials</h4><ul>${otherCerts.map(cert => {
                    if (cert.includes('BNSP Graphic Design')) {
                        return `<li>${cert}<br><a href="/static/uploads/certificates/sertifikat_DesignGraphic_BNSP(Depan)_20260710_0001.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline; font-size: 0.85rem; margin-right: 10px;">Lihat Depan</a><a href="/static/uploads/certificates/sertifikat_DesignGraphic_BNSP(Belakang)_20260710_0001.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline; font-size: 0.85rem;">Lihat Belakang</a></li>`;
                    }
                    if (cert.includes('Sertifikat Graphic Design Telkom')) {
                        return `<li><a href="/static/uploads/certificates/telkom_graphic.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline;">${cert}</a></li>`;
                    }
                    if (cert.includes('BNSP Network Engineering')) {
                        return `<li>${cert}<br><a href="/static/uploads/certificates/sertifikat_NetworkEnginer_BNSP(Depan)_20260710_0001.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline; font-size: 0.85rem; margin-right: 10px;">Lihat Depan</a><a href="/static/uploads/certificates/sertifikat_NetworkEnginer_BNSP(Belakang)_20260710_0001.jpg" target="_blank" style="color: var(--secondary); text-decoration: underline; font-size: 0.85rem;">Lihat Belakang</a></li>`;
                    }
                    if (cert.includes('KarirNext') || cert.includes('Data Analyst')) {
                        return `<li><a href="/static/uploads/certificates/WhatsApp Image 2026-07-10 at 16.42.20.jpeg" target="_blank" style="color: var(--secondary); text-decoration: underline;">${cert}</a></li>`;
                    }
                    return `<li>${cert}</li>`;
                }).join('')}</ul>`;
            }
            certList = certHtml;
        }

        let projList = '';
        if (data.projects && data.projects.length > 0) {
            projList = `
                <h4>Projects</h4>
                <ul>
                    ${data.projects.map(proj => `<li>${proj}</li>`).join('')}
                </ul>
            `;
        }

        mBody.innerHTML = `
            <p>${data.description}</p>
            ${softwareList}
            ${certList}
            ${projList}
        `;

        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
    }

    function closeModal() {
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
    }

    cards.forEach(card => {
        card.addEventListener('click', () => {
            // Read dataset or static fallback data
            const modalData = card.getAttribute('data-modal');
            if (modalData) {
                try {
                    const data = JSON.parse(modalData);
                    openModal(data);
                } catch (e) {
                    console.error("Error parsing skill modal data", e);
                }
            } else {
                // Read from card DOM
                const name = card.querySelector('.skill-card__title').textContent;
                const desc = card.querySelector('.skill-card__desc').textContent;
                const software = Array.from(card.querySelectorAll('.skill-card__software li')).map(li => li.textContent);
                const iconImg = card.querySelector('.skill-card__icon img');
                const iconSrc = iconImg ? iconImg.getAttribute('src').replace('/static/assets/svg/', '') : '';

                openModal({
                    name,
                    description: desc,
                    software,
                    icon: iconSrc
                });
            }
        });
    });

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
}
