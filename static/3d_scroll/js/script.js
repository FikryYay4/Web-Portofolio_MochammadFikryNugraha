/* ============================================
   ARCHITECT — 3D Cylinder Scroll Engine
   ============================================ */

(function () {
    'use strict';

    const isMobile = () => window.innerWidth <= 768;

    /* ── DOM Elements ────────────────────── */
    const proxy = document.querySelector('.scroll-proxy');
    const cylinder = document.getElementById('cylinder');
    const panels = Array.from(document.querySelectorAll('.panel'));
    
    // Custom Cursor
    const cursorOuter = document.getElementById('cursor');
    const cursorDot = document.getElementById('cursor-dot');

    /* ── Configuration ───────────────────── */
    const N = panels.length; // Ensure this is 6 based on HTML
    const THETA = 360 / N;   // 60 degrees between panels

    /* ── State ───────────────────────────── */
    let currentRotation = 0;
    let targetRotation = 0;
    let radius = 0;

    /* ── Initialization & Math ───────────── */
    function resize() {
        const H = window.innerHeight;
        // Calculate radius to make each panel exactly full screen height at the tangent
        // Since panel rotates around center, the apothem is the radius
        // R = (H / 2) / Math.tan(Math.PI / N)
        radius = (H / 2) / Math.tan(Math.PI / N);
        
        // Add minimal padding so panels don't clip into each other tightly
        radius += isMobile() ? 40 : 100;

        // Propagate to CSS variables
        document.documentElement.style.setProperty('--cylinder-radius', `${radius}px`);
        
        // Adjust proxy height to make the scrolling smooth.
        // We want (N-1) sections of scroll depth. Each translates to 1.5 viewport heights to give reading time.
        proxy.style.height = `${(N) * 1.5 * H}px`;
        
        // Force update immediately
        updateScrollProgress();
    }

    /* ── Scroll Logic ────────────────────── */
    function updateScrollProgress() {
        if (!proxy) return;
        const scrollTop = window.scrollY;
        const maxScroll = proxy.scrollHeight - window.innerHeight;
        const progress = maxScroll > 0 ? scrollTop / maxScroll : 0;
        
        // We want the total rotation to span from Panel 0 to Panel N-1
        // meaning total degrees = (N - 1) * THETA
        targetRotation = progress * ((N - 1) * THETA);
    }

    /* ── Animation Loop ──────────────────── */
    function render() {
        // Lerp for buttery smooth scrolling
        currentRotation += (targetRotation - currentRotation) * 0.08;
        
        if (cylinder) {
            // translateZ(-R) pushes the entire cylinder back so the front panel sits at Z=0 (viewport plane)
            // rotateX spins the cylinder. A positive rotation makes it spin downwards (so panels below come UP).
            cylinder.style.transform = `translateZ(-${radius}px) rotateX(${currentRotation}deg)`;
        }

        // Panel Depth Management (Opacity & Blur)
        panels.forEach((panel, i) => {
             const panelRot = i * THETA;
             // Find how far the panel is from the front (currently viewed angle)
             const diff = Math.abs(panelRot - currentRotation);
             
             // distance ratio: 0 is front, 1 is 1-panel away (60deg), >1 is behind
             const distRatio = Math.min(diff / THETA, 1.5);
             
             // Dim panels that are rolling away/behind
             const opacity = Math.max(1 - distRatio * 0.9, 0.05);
             
             // Add blur to fading panels to enhance depth of field
             const blur = distRatio * 8; 

             panel.style.opacity = opacity;
             panel.style.filter = `blur(${blur}px)`;
             
             // Optimize out completely hidden panels from paint interactions
             panel.style.pointerEvents = distRatio > 0.5 ? 'none' : 'all';
        });

        // Request next frame
        requestAnimationFrame(render);
    }

    /* ── Custom Cursor ───────────────────── */
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    function initCursor() {
        if (isMobile() || !cursorOuter || !cursorDot) return;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            cursorDot.style.left = mouseX + 'px';
            cursorDot.style.top = mouseY + 'px';
        });

        const hoverTargets = document.querySelectorAll('button, a, .bento-item, .image-wrapper');
        hoverTargets.forEach((el) => {
            el.addEventListener('mouseenter', () => cursorOuter.style.borderColor = 'var(--color-tertiary)');
            el.addEventListener('mouseleave', () => cursorOuter.style.borderColor = 'rgba(132, 173, 255, 0.5)');
            el.addEventListener('mouseenter', () => cursorOuter.style.transform = 'translate(-50%, -50%) scale(1.5)');
            el.addEventListener('mouseleave', () => cursorOuter.style.transform = 'translate(-50%, -50%) scale(1)');
        });
    }

    function renderCursor() {
        if (!isMobile() && cursorOuter) {
            cursorX += (mouseX - cursorX) * 0.15;
            cursorY += (mouseY - cursorY) * 0.15;
            cursorOuter.style.left = cursorX + 'px';
            cursorOuter.style.top = cursorY + 'px';
        }
        requestAnimationFrame(renderCursor);
    }

    /* ── Boot ────────────────────────────── */
    function init() {
        window.addEventListener('resize', resize);
        window.addEventListener('scroll', updateScrollProgress, { passive: true });
        
        resize();
        updateScrollProgress();
        
        // Ensure starting properties apply
        currentRotation = targetRotation; 

        initCursor();
        
        // Start loops
        requestAnimationFrame(render);
        requestAnimationFrame(renderCursor);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
