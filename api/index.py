"""
RETROLENS — FastAPI Backend for Vercel
Clean minimal design, browser-side MediaPipe hand tracking
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="RETROLENS")

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"/>
  <meta name="description" content="RETROLENS — Real-time hand tracking camera filter app with 26 cinematic filters."/>
  <title>RETROLENS — Hand Tracking Camera Filter</title>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {
      box-sizing: border-box; margin: 0; padding: 0;
      user-select: none; -webkit-user-select: none;
      scrollbar-width: none; -ms-overflow-style: none;
    }
    ::-webkit-scrollbar { display: none; }

    html, body {
      width: 100vw; height: 100vh;
      overflow: hidden;
      background: #03030a;
      font-family: 'Inter', system-ui, sans-serif;
    }

    /* ── Canvas Stage ─────────────────────────── */
    #stage {
      position: relative;
      width: 100vw; height: 100vh;
      overflow: hidden;
    }

    #webcam { display: none; }

    #output_canvas {
      position: absolute; inset: 0;
      width: 100%; height: 100%;
      object-fit: cover;
      display: block;
    }

    /* ── Filter Badge — bottom-left ───────────── */
    #filter-badge {
      position: absolute;
      bottom: 28px; left: 24px;
      z-index: 40;
      display: none;
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;
      pointer-events: none;
    }
    #filter-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 2px;
      color: rgba(255,255,255,0.35);
      text-transform: uppercase;
    }
    #filter-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 22px;
      font-weight: 600;
      letter-spacing: 1px;
      color: #fff;
      text-shadow: 0 0 20px currentColor;
      transition: color 0.3s ease, text-shadow 0.3s ease;
    }
    #filter-counter {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: rgba(255,255,255,0.3);
      letter-spacing: 1px;
    }

    /* ── Gesture Guide — bottom-right ────────── */
    #gesture-guide {
      position: absolute;
      bottom: 28px; right: 24px;
      z-index: 40;
      display: none;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
      pointer-events: none;
    }
    .g-row {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      color: rgba(255,255,255,0.35);
      letter-spacing: 0.5px;
    }
    .g-row .g-icon {
      font-size: 14px;
      opacity: 0.6;
    }

    /* ── App Name — top-left ─────────────────── */
    #app-brand {
      position: absolute;
      top: 22px; left: 24px;
      z-index: 40;
      display: none;
      align-items: center;
      gap: 10px;
      pointer-events: none;
    }
    #app-brand .brand-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: #00e5a0;
      box-shadow: 0 0 8px #00e5a0;
      animation: blink 2s ease-in-out infinite;
    }
    @keyframes blink {
      0%,100% { opacity: 1; }
      50%      { opacity: 0.3; }
    }
    #app-brand .brand-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 3px;
      color: rgba(255,255,255,0.5);
    }

    /* ── Loading overlay ─────────────────────── */
    #loading {
      position: absolute; inset: 0;
      z-index: 100;
      background: #03030a;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      transition: opacity 0.4s ease;
    }
    #loading .ld-ring {
      width: 40px; height: 40px;
      border: 2px solid rgba(255,255,255,0.06);
      border-top-color: #00e5a0;
      border-radius: 50%;
      animation: spin 0.9s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    #loading .ld-text {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 2px;
      color: rgba(255,255,255,0.25);
    }

    /* ── Permission prompt (fallback) ────────── */
    #perm-prompt {
      position: absolute; inset: 0;
      z-index: 100;
      background: #03030a;
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 20px;
      cursor: pointer;
    }
    #perm-prompt .pp-icon {
      font-size: 40px;
      opacity: 0.5;
    }
    #perm-prompt .pp-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 2px;
      color: rgba(255,255,255,0.5);
    }
    #perm-prompt .pp-sub {
      font-size: 12px;
      color: rgba(255,255,255,0.2);
      letter-spacing: 0.5px;
      text-align: center;
      line-height: 1.8;
      max-width: 280px;
    }
    #perm-prompt .pp-btn {
      margin-top: 8px;
      padding: 12px 32px;
      border-radius: 100px;
      border: 1px solid rgba(0,229,160,0.4);
      background: transparent;
      color: #00e5a0;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      letter-spacing: 2px;
      cursor: pointer;
      transition: background 0.2s, border-color 0.2s;
    }
    #perm-prompt .pp-btn:hover {
      background: rgba(0,229,160,0.08);
      border-color: rgba(0,229,160,0.7);
    }

    /* ── Error toast ─────────────────────────── */
    #err-toast {
      position: absolute;
      top: 24px; left: 50%; transform: translateX(-50%);
      z-index: 200;
      background: rgba(239,68,68,0.12);
      border: 1px solid rgba(239,68,68,0.3);
      border-radius: 12px;
      padding: 12px 20px;
      font-size: 13px;
      color: #fca5a5;
      display: none;
      white-space: nowrap;
      backdrop-filter: blur(12px);
    }
  </style>
</head>
<body>
<div id="stage">
  <video id="webcam" playsinline></video>
  <canvas id="output_canvas"></canvas>

  <!-- Live UI overlays (shown after camera starts) -->
  <div id="app-brand">
    <div class="brand-dot"></div>
    <div class="brand-name">RETROLENS</div>
  </div>

  <div id="filter-badge">
    <div id="filter-label">FILTER AKTIF</div>
    <div id="filter-name">NORMAL</div>
    <div id="filter-counter">01 / 26</div>
  </div>

  <div id="gesture-guide">
    <div class="g-row"><span>Ibu jari + kelingking</span><span class="g-icon">🤙</span></div>
    <div class="g-row"><span>2 tangan bersentuhan</span><span class="g-icon">🤝</span></div>
    <div class="g-row" style="color:rgba(255,255,255,0.18)"><span>ganti filter</span></div>
  </div>

  <div id="err-toast"></div>

  <!-- Loading spinner (shown while initialising) -->
  <div id="loading">
    <div class="ld-ring"></div>
    <div class="ld-text">MEMUAT KAMERA</div>
  </div>

  <!-- Permission fallback (shown only if camera blocked) -->
  <div id="perm-prompt">
    <div class="pp-icon">&#128247;</div>
    <div class="pp-title">IZIN KAMERA</div>
    <div class="pp-sub">Izinkan akses kamera di browser Anda,<br>lalu klik tombol di bawah untuk melanjutkan.</div>
    <button class="pp-btn" id="retry-btn">COBA LAGI</button>
  </div>
</div>

<script>
// ─────────────────────────────────────────────
// FILTER REGISTRY
// ─────────────────────────────────────────────
const FILTERS = [
  { name: "NORMAL",     color: [200,200,200] },
  { name: "MONO",       color: [180,180,180] },
  { name: "SEPIA",      color: [210,130, 50] },
  { name: "VINTAGE",    color: [200,150, 80] },
  { name: "INVERT",     color: [255, 80,220] },
  { name: "THERMAL",    color: [255,100,  0] },
  { name: "NEON",       color: [  0,255,255] },
  { name: "NIGHT",      color: [  0,230, 80] },
  { name: "OCEAN",      color: [ 20,140,230] },
  { name: "FIRE",       color: [255,100,  0] },
  { name: "RAINBOW",    color: [160,255,  0] },
  { name: "GALAXY",     color: [180, 80,255] },
  { name: "SKETCH",     color: [220,220,220] },
  { name: "EMBOSS",     color: [200,200,200] },
  { name: "CARTOON",    color: [  0,220,255] },
  { name: "GLITCH",     color: [255, 50, 50] },
  { name: "PIXELATE",   color: [  0,180,255] },
  { name: "BLUR",       color: [180,180,255] },
  { name: "DUAL-TONE",  color: [255, 20,180] },
  { name: "OIL",        color: [ 60,210,120] },
  { name: "VIGNETTE",   color: [160,120,120] },
  { name: "MIRROR",     color: [200,230,255] },
  { name: "CYBERPUNK",  color: [255, 20,120] },
  { name: "MATRIX",     color: [  0,255, 80] },
  { name: "LOMO",       color: [255,150, 50] },
  { name: "ICE",        color: [120,220,255] },
];

// ─────────────────────────────────────────────
// DOM REFS
// ─────────────────────────────────────────────
const video       = document.getElementById('webcam');
const canvas      = document.getElementById('output_canvas');
const ctx         = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
const loadingEl   = document.getElementById('loading');
const permPrompt  = document.getElementById('perm-prompt');
const retryBtn    = document.getElementById('retry-btn');
const filterBadge = document.getElementById('filter-badge');
const filterName  = document.getElementById('filter-name');
const filterCount = document.getElementById('filter-counter');
const gestureUI   = document.getElementById('gesture-guide');
const brandUI     = document.getElementById('app-brand');
const errToast    = document.getElementById('err-toast');

// Offscreen canvases
const offC  = document.createElement('canvas');
const offX  = offC.getContext('2d', { willReadFrequently: true });
const miniC = document.createElement('canvas');
const miniX = miniC.getContext('2d', { willReadFrequently: true });

// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
let curFilter        = 0;
let gestureTriggered = false;
let camRunning       = false;
let processing       = false;
let lastAccent       = '#00e5a0';
let animFrame        = 0; // for time-based filters

// ─────────────────────────────────────────────
// RESIZE CANVAS TO MATCH WINDOW
// ─────────────────────────────────────────────
function resizeCanvas() {
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// ─────────────────────────────────────────────
// UTILITY
// ─────────────────────────────────────────────
function rgb(c) { return `rgb(${c[0]},${c[1]},${c[2]})`; }

function showError(msg) {
  errToast.textContent = msg;
  errToast.style.display = 'block';
  setTimeout(() => { errToast.style.display = 'none'; }, 4000);
}

// ─────────────────────────────────────────────
// APPLY FILTER TO REGION
// Returns an ImageData or OffscreenCanvas to blit
// ─────────────────────────────────────────────
function applyFilter(name, sx, sy, sw, sh) {
  if (sw < 2 || sh < 2) return null;

  offC.width  = sw;
  offC.height = sh;

  // ── CSS filter shortcuts (no pixel read needed) ──
  const cssMap = {
    'MONO':    'grayscale(100%)',
    'SEPIA':   'sepia(100%) saturate(130%) brightness(1.05)',
    'INVERT':  'invert(100%)',
    'BLUR':    'blur(14px)',
    'MIRROR':  null, // handled below
  };
  if (name === 'MIRROR') {
    offX.save();
    offX.translate(sw, 0); offX.scale(-1, 1);
    offX.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);
    offX.restore();
    return offC;
  }
  if (name === 'PIXELATE') {
    const pw = Math.max(2, (sw/12)|0), ph = Math.max(2, (sh/12)|0);
    miniC.width = pw; miniC.height = ph;
    miniX.drawImage(canvas, sx, sy, sw, sh, 0, 0, pw, ph);
    offX.imageSmoothingEnabled = false;
    offX.drawImage(miniC, 0, 0, pw, ph, 0, 0, sw, sh);
    offX.imageSmoothingEnabled = true;
    return offC;
  }
  if (cssMap[name]) {
    offX.filter = cssMap[name];
    offX.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);
    offX.filter = 'none';
    return offC;
  }

  // ── Pixel-manipulation filters ──
  offX.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);
  const imgData = offX.getImageData(0, 0, sw, sh);
  const d = imgData.data;
  const len = d.length;
  const t = Date.now() * 0.001;

  if (name === 'NORMAL') {
    // No-op, already drawn
  }

  else if (name === 'VINTAGE') {
    const cx = sw >> 1, cy = sh >> 1;
    const maxD = Math.hypot(cx, cy) + 1e-6;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw)|0;
      const r = d[i], g = d[i+1], b = d[i+2];
      // sepia
      const sr = Math.min(255, 0.393*r + 0.769*g + 0.189*b);
      const sg = Math.min(255, 0.349*r + 0.686*g + 0.168*b);
      const sb = Math.min(255, 0.272*r + 0.534*g + 0.131*b);
      // vignette
      const vig = Math.max(0, 1 - Math.pow(Math.hypot(x-cx, y-cy)/maxD, 1.6));
      d[i]   = sr * vig;
      d[i+1] = sg * vig;
      d[i+2] = sb * vig;
    }
  }

  else if (name === 'THERMAL') {
    for (let i = 0; i < len; i += 4) {
      const v = (d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114) / 255;
      d[i]   = Math.min(255, Math.max(0, 255*(1.5 - Math.abs(4*v - 3))));
      d[i+1] = Math.min(255, Math.max(0, 255*(1.5 - Math.abs(4*v - 2))));
      d[i+2] = Math.min(255, Math.max(0, 255*(1.5 - Math.abs(4*v - 1))));
    }
  }

  else if (name === 'NEON') {
    for (let y = 0; y < sh-1; y++) {
      const row = y*sw*4, nr = (y+1)*sw*4;
      for (let x = 0; x < sw-1; x++) {
        const i = row + x*4, r = row+(x+1)*4, dn = nr+x*4;
        const lum  = (d[i]  +d[i+1]  +d[i+2]  )/3;
        const lumR = (d[r]  +d[r+1]  +d[r+2]  )/3;
        const lumD = (d[dn] +d[dn+1] +d[dn+2] )/3;
        const edge = Math.min(255, Math.hypot(lumR-lum, lumD-lum) * 4);
        d[i]   = 0;
        d[i+1] = edge;
        d[i+2] = edge;
      }
    }
  }

  else if (name === 'NIGHT') {
    for (let i = 0; i < len; i += 4) {
      const lum = d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114;
      d[i]   = 0;
      d[i+1] = Math.min(255, lum * 1.9 + 15);
      d[i+2] = 0;
    }
  }

  else if (name === 'OCEAN') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = (d[i]   * 0.3) | 0;
      d[i+1] = (d[i+1] * 0.8) | 0;
      d[i+2] = Math.min(255, (d[i+2] * 1.5) | 0);
    }
  }

  else if (name === 'FIRE') {
    for (let i = 0; i < len; i += 4) {
      const lum = d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114;
      d[i]   = Math.min(255, lum * 3.0);
      d[i+1] = Math.min(255, Math.max(0, (lum - 85) * 3));
      d[i+2] = Math.min(255, Math.max(0, (lum - 170)* 3));
    }
  }

  else if (name === 'RAINBOW') {
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw;
      const lum = (d[i]+d[i+1]+d[i+2])/3;
      const angle = (x/sw + t*0.2) * Math.PI * 2;
      d[i]   = Math.min(255, lum*0.4 + Math.sin(angle)*110 + 120);
      d[i+1] = Math.min(255, lum*0.4 + Math.sin(angle+2.094)*110 + 120);
      d[i+2] = Math.min(255, lum*0.4 + Math.sin(angle+4.189)*110 + 120);
    }
  }

  else if (name === 'GALAXY') {
    // Dark base + starfield overlay + original image blend
    for (let i = 0; i < len; i += 4) {
      d[i]   = (d[i]   * 0.15 + 10) | 0;
      d[i+1] = (d[i+1] * 0.05 + 5 ) | 0;
      d[i+2] = (d[i+2] * 0.5  + 20) | 0;
    }
    offX.putImageData(imgData, 0, 0);
    // Draw animated stars on top
    for (let s = 0; s < 80; s++) {
      const sx2 = ((Math.sin(s * 137.5 + t) * 0.5 + 0.5) * sw) | 0;
      const sy2 = ((Math.cos(s * 97.3  + t * 0.7) * 0.5 + 0.5) * sh) | 0;
      const alpha = (Math.sin(s + t * 2) * 0.5 + 0.5);
      offX.fillStyle = s % 3 === 0 ? `rgba(200,80,255,${alpha})` :
                       s % 3 === 1 ? `rgba(0,229,160,${alpha})` :
                                     `rgba(255,255,255,${alpha*0.5})`;
      offX.beginPath();
      offX.arc(sx2, sy2, (s % 2) + 0.8, 0, Math.PI*2);
      offX.fill();
    }
    return offC;
  }

  else if (name === 'SKETCH') {
    for (let y = 0; y < sh-1; y++) {
      const row = y*sw*4, nr = (y+1)*sw*4;
      for (let x = 0; x < sw-1; x++) {
        const i = row+x*4, next = nr+(x+1)*4;
        const g1 = (d[i]+d[i+1]+d[i+2])/3;
        const g2 = (d[next]+d[next+1]+d[next+2])/3;
        const val = 255 - Math.min(255, Math.abs(g1-g2)*7);
        d[i] = d[i+1] = d[i+2] = val;
      }
    }
  }

  else if (name === 'EMBOSS') {
    const copy = new Uint8ClampedArray(d);
    for (let y = 1; y < sh-1; y++) {
      for (let x = 1; x < sw-1; x++) {
        const i   = (y*sw+x)*4;
        const tl  = ((y-1)*sw+(x-1))*4;
        const br  = ((y+1)*sw+(x+1))*4;
        const gTL = (copy[tl]+copy[tl+1]+copy[tl+2])/3;
        const gBR = (copy[br]+copy[br+1]+copy[br+2])/3;
        const val = Math.min(255, Math.max(0, (gBR-gTL)*1.4+128));
        d[i] = d[i+1] = d[i+2] = val;
      }
    }
  }

  else if (name === 'CARTOON') {
    // Posterize
    for (let i = 0; i < len; i += 4) {
      d[i]   = ((d[i]   >> 5) * 36 + 18);
      d[i+1] = ((d[i+1] >> 5) * 36 + 18);
      d[i+2] = ((d[i+2] >> 5) * 36 + 18);
    }
  }

  else if (name === 'GLITCH') {
    const shift = Math.max(4, (sw/16)|0);
    const copy  = new Uint8ClampedArray(d);
    for (let y = 0; y < sh; y++) {
      const row = y*sw*4;
      // Apply glitch only to random rows
      if (Math.sin(y * 0.3 + t * 10) > 0.4) {
        for (let x = 0; x < sw; x++) {
          const i  = row + x*4;
          const rx = Math.min(sw-1, x+shift);
          const bx = Math.max(0, x-shift);
          d[i]   = copy[row + rx*4];
          d[i+2] = copy[row + bx*4 + 2];
        }
      }
    }
  }

  else if (name === 'DUAL-TONE') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114);
      if (lum > 128) { d[i]=255; d[i+1]=160; d[i+2]=0;   }
      else           { d[i]=255; d[i+1]=10;  d[i+2]=180; }
    }
  }

  else if (name === 'OIL') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = ((d[i]   / 36) | 0) * 36;
      d[i+1] = ((d[i+1] / 36) | 0) * 36;
      d[i+2] = ((d[i+2] / 36) | 0) * 36;
    }
  }

  else if (name === 'VIGNETTE') {
    const cx = sw>>1, cy = sh>>1;
    const maxD = Math.hypot(cx, cy) + 1e-6;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const vig = Math.max(0, 1 - Math.pow(Math.hypot(x-cx,y-cy)/maxD, 1.9));
      d[i]   = (d[i]   * vig) | 0;
      d[i+1] = (d[i+1] * vig) | 0;
      d[i+2] = (d[i+2] * vig) | 0;
    }
  }

  else if (name === 'CYBERPUNK') {
    for (let i = 0; i < len; i += 4) {
      const lum = d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114;
      // Teal-shadows, magenta-highlights
      const t2  = lum / 255;
      d[i]   = Math.min(255, lum * 0.6 + 255 * t2 * 0.8);
      d[i+1] = Math.min(255, lum * 0.1 + 20);
      d[i+2] = Math.min(255, lum * 0.6 + 255 * (1-t2) * 0.6);
    }
  }

  else if (name === 'MATRIX') {
    for (let i = 0; i < len; i += 4) {
      const lum = d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114;
      d[i]   = 0;
      d[i+1] = Math.min(255, lum * 2.0);
      d[i+2] = 0;
    }
  }

  else if (name === 'LOMO') {
    const cx = sw>>1, cy = sh>>1;
    const maxD = Math.hypot(cx, cy) + 1e-6;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw)|0;
      const vig = Math.max(0.05, 1 - Math.pow(Math.hypot(x-cx,y-cy)/maxD, 1.3));
      d[i]   = Math.min(255, (d[i]   * 1.15 * vig) | 0);
      d[i+1] = Math.min(255, (d[i+1] * 0.85 * vig) | 0);
      d[i+2] = Math.min(255, (d[i+2] * 0.7  * vig) | 0);
    }
  }

  else if (name === 'ICE') {
    for (let i = 0; i < len; i += 4) {
      const lum = d[i]*0.299 + d[i+1]*0.587 + d[i+2]*0.114;
      d[i]   = Math.min(255, lum * 0.7 + 30);
      d[i+1] = Math.min(255, lum * 0.9 + 50);
      d[i+2] = Math.min(255, lum * 1.3 + 80);
    }
  }

  offX.putImageData(imgData, 0, 0);
  return offC;
}

// ─────────────────────────────────────────────
// UPDATE FILTER BADGE UI
// ─────────────────────────────────────────────
function updateBadge(idx) {
  const f = FILTERS[idx];
  const ac = rgb(f.color);
  filterName.textContent  = f.name;
  filterCount.textContent = `${String(idx+1).padStart(2,'0')} / ${FILTERS.length}`;
  filterName.style.color  = ac;
  filterName.style.textShadow = `0 0 16px ${ac}`;
  lastAccent = ac;
}
updateBadge(0);

// ─────────────────────────────────────────────
// MEDIAPIPE RESULT HANDLER
// ─────────────────────────────────────────────
function onResults(results) {
  processing = false;
  animFrame++;

  const W = canvas.width, H = canvas.height;

  // Draw mirrored camera frame
  ctx.save();
  ctx.translate(W, 0); ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, W, H);
  ctx.restore();

  const fdata      = FILTERS[curFilter];
  const accentColor = rgb(fdata.color);
  const hands       = results.multiHandLandmarks;

  let triggerChange = false;
  const portalPts   = [];

  if (hands && hands.length > 0) {
    // ── Two-hand gesture (index tips meet) ──
    if (hands.length >= 2) {
      const p0 = { x:(1-hands[0][8].x)*W, y:hands[0][8].y*H };
      const p1 = { x:(1-hands[1][8].x)*W, y:hands[1][8].y*H };
      if (Math.hypot(p0.x-p1.x, p0.y-p1.y) < 50) triggerChange = true;
    }

    for (const hand of hands) {
      const thumb = { x:(1-hand[4].x)*W,  y:hand[4].y*H  };
      const index = { x:(1-hand[8].x)*W,  y:hand[8].y*H  };
      const pinky = { x:(1-hand[20].x)*W, y:hand[20].y*H };

      portalPts.push(thumb, index);

      const dist     = Math.hypot(thumb.x-pinky.x, thumb.y-pinky.y);
      const nearTrig = dist < 90;
      const onTrig   = dist < 48;
      if (onTrig) triggerChange = true;

      // Draw connector line
      if (nearTrig) {
        ctx.save();
        ctx.strokeStyle = onTrig ? '#ef4444' : '#f59e0b';
        ctx.lineWidth   = onTrig ? 2.5 : 1.5;
        ctx.setLineDash(onTrig ? [] : [4,4]);
        ctx.globalAlpha = 0.8;
        ctx.beginPath();
        ctx.moveTo(thumb.x, thumb.y);
        ctx.lineTo(pinky.x, pinky.y);
        ctx.stroke();
        ctx.restore();
      }

      // Pinky dot
      const pinkyColor = onTrig ? '#ef4444' : '#a855f7';
      ctx.save();
      ctx.globalAlpha = 0.9;
      ctx.fillStyle = pinkyColor;
      ctx.beginPath(); ctx.arc(pinky.x, pinky.y, 10, 0, Math.PI*2); ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(pinky.x, pinky.y, 13, 0, Math.PI*2); ctx.stroke();
      ctx.restore();

      // Thumb & index dots
      for (const pt of [thumb, index]) {
        ctx.save();
        ctx.globalAlpha = 0.9;
        ctx.fillStyle = accentColor;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 9, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 12, 0, Math.PI*2); ctx.stroke();
        ctx.restore();
      }
    }

    // ── Debounce filter change ──
    if (triggerChange) {
      if (!gestureTriggered) {
        curFilter = (curFilter + 1) % FILTERS.length;
        updateBadge(curFilter);
        gestureTriggered = true;
      }
    } else {
      gestureTriggered = false;
    }

    // ── Portal filter region (from 2 hands = 4 pts) ──
    if (portalPts.length >= 4) {
      const sorted = [...portalPts].sort((a,b) => a.y - b.y);
      const topPts = sorted.slice(0, 2).sort((a,b) => a.x - b.x);
      const botPts = sorted.slice(2, 4).sort((a,b) => a.x - b.x);
      const poly   = [topPts[0], topPts[1], botPts[1], botPts[0]];

      const pxs = poly.map(p => p.x), pys = poly.map(p => p.y);
      const rsx = Math.max(0, Math.min(...pxs) | 0);
      const rex = Math.min(W, Math.max(...pxs) | 0);
      const rsy = Math.max(0, Math.min(...pys) | 0);
      const rey = Math.min(H, Math.max(...pys) | 0);
      const rw  = rex - rsx, rh = rey - rsy;

      if (rw > 24 && rh > 24) {
        const filtered = applyFilter(fdata.name, rsx, rsy, rw, rh);
        if (filtered) {
          ctx.save();
          ctx.beginPath();
          ctx.moveTo(poly[0].x, poly[0].y);
          for (let k=1; k<4; k++) ctx.lineTo(poly[k].x, poly[k].y);
          ctx.closePath();
          ctx.clip();
          ctx.drawImage(filtered, rsx, rsy);
          ctx.restore();
        }

        // Portal outline with animated dash
        ctx.save();
        ctx.strokeStyle = accentColor;
        ctx.lineWidth   = 2;
        ctx.globalAlpha = 0.9;
        ctx.setLineDash([8, 4]);
        ctx.lineDashOffset = -animFrame * 0.5;
        ctx.beginPath();
        ctx.moveTo(poly[0].x, poly[0].y);
        for (let k=1; k<4; k++) ctx.lineTo(poly[k].x, poly[k].y);
        ctx.closePath();
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();

        // Spark particles at corners
        for (const pt of poly) {
          const px = pt.x + (Math.random()-0.5)*12;
          const py = pt.y + (Math.random()-0.5)*12;
          ctx.save();
          ctx.fillStyle = accentColor;
          ctx.globalAlpha = Math.random() * 0.8 + 0.2;
          ctx.beginPath(); ctx.arc(px, py, Math.random()*2+0.5, 0, Math.PI*2); ctx.fill();
          ctx.restore();
        }
      }
    }
  }
}

// ─────────────────────────────────────────────
// START CAMERA + MEDIAPIPE
// ─────────────────────────────────────────────
async function startApp() {
  if (camRunning) return;

  // Hide permission prompt, show loading spinner
  permPrompt.style.display = 'none';
  loadingEl.style.display  = 'flex';
  loadingEl.style.opacity  = '1';

  try {
    const hands = new Hands({
      locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${f}`
    });
    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.55,
      minTrackingConfidence: 0.5,
    });
    hands.onResults(onResults);

    const cam = new Camera(video, {
      onFrame: async () => {
        // Fade out loader on first frame
        if (loadingEl.style.display !== 'none') {
          loadingEl.style.opacity = '0';
          setTimeout(() => { loadingEl.style.display = 'none'; }, 400);
        }
        if (!processing) {
          processing = true;
          if (video.videoWidth && (canvas.width !== window.innerWidth || canvas.height !== window.innerHeight)) {
            resizeCanvas();
          }
          try { await hands.send({ image: video }); }
          catch(e) { processing = false; }
        }
      },
      width: 1280, height: 720,
    });

    await cam.start();
    camRunning = true;

    // Show live UI elements
    filterBadge.style.display = 'flex';
    gestureUI.style.display   = 'flex';
    brandUI.style.display     = 'flex';

  } catch (err) {
    // Hide loader, show permission prompt
    loadingEl.style.display  = 'none';
    permPrompt.style.display = 'flex';
    if (err.name === 'NotFoundError') {
      showError('⚠ Kamera tidak ditemukan di perangkat ini.');
    } else if (err.name !== 'NotAllowedError') {
      showError('⚠ Gagal memulai kamera: ' + err.message);
    }
  }
}

// ─────────────────────────────────────────────
// AUTO-START & RETRY
// ─────────────────────────────────────────────
window.addEventListener('load', startApp);
retryBtn.addEventListener('click', startApp);
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=HTML_PAGE)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "RETROLENS", "filters": 26}
