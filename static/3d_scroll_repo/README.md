# 3D Scroll Web Template

**🔗 Live Demo: [https://sina-cb.github.io/3d_scroll_web/](https://sina-cb.github.io/3d_scroll_web/)**

A visually stunning, immersive 3D scroll experience built with vanilla HTML, CSS, and JavaScript. Designed as a template with placeholder content that's easy to customize.

## ✨ Features

- **3D Scroll Effects** — Perspective transforms, parallax depth layers, and cinematic section reveals
- **Horizontal Scroll Gallery** — Cards scroll horizontally as you scroll vertically (desktop)
- **Interactive 3D Card Tilt** — Gallery cards respond to mouse position with 3D rotation
- **Word-by-Word Text Reveals** — Headlines animate in from Z-depth
- **Floating Parallax Geometry** — Decorative elements at different scroll speeds
- **Glassmorphism Navigation** — Frosted glass effect with backdrop blur
- **Custom Cursor** — Follows mouse with smooth easing (desktop)
- **Scroll Progress Bar** — Glowing indicator showing page progress
- **Fully Responsive** — Optimized for mobile, tablet, and desktop
- **Accessibility** — Respects `prefers-reduced-motion` settings

## 🚀 Deployment

This is a **static site** — no build step required.

### GitHub Pages

1. Push to your repository
2. Go to **Settings → Pages**
3. Set source to **main** branch, root `/`
4. Your site will be live at `https://<username>.github.io/3d_scroll_web/`

### Local Preview

Simply open `index.html` in your browser, or use a local server:

```bash
# Python
python -m http.server 8000

# Node.js
npx serve .
```

## 📁 Structure

```
├── index.html          # Main HTML structure
├── css/
│   └── style.css       # Design system + 3D animations
├── js/
│   └── script.js       # Scroll engine + interactive effects
├── .gitignore
└── README.md
```

## 🎨 Customization

### Colors
Edit CSS custom properties in `css/style.css` under `:root` to change the entire color scheme.

### Content
Replace placeholder text and image URLs directly in `index.html`. Images use Unsplash URLs by default — swap with your own.

### Effects
Tune 3D effect intensity by adjusting variables in `js/script.js`:
- Parallax speeds
- Tilt angles
- Animation thresholds

## 📐 Design System

Based on the "Digital Architect" design language:
- **Typography**: Epilogue (headlines), Manrope (body), Space Grotesk (labels)
- **Palette**: Deep navy surfaces, electric blue primary, soft gold accents
- **Depth**: Tonal surface layering, glassmorphism, ambient shadows

## License

MIT
