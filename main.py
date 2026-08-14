"""
RETROLENS — Hand Tracking Camera Filter App
Support dual-mode:
1. Streamlit Web App (Streamlit Community Cloud / Browser)
2. Desktop OpenCV App (Local Python Execution)
"""

import sys
import os

def is_running_in_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return (
            "streamlit" in sys.modules or
            any("streamlit" in arg for arg in sys.argv) or
            os.environ.get("STREAMLIT_SERVER_PORT") is not None
        )

def run_streamlit_app():
    import streamlit as st
    import streamlit.components.v1 as components

    st.set_page_config(
        page_title="RETROLENS — Hand Tracking Filter Portal",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS Styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #0a0a14;
        color: #f8fafc;
    }
    header, footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    .custom-title {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00e5a0 0%, #00a5ff 50%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .custom-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<h2 style='color:#00e5a0;'>✨ RETROLENS</h2>", unsafe_allow_html=True)
        st.caption("AI Hand Tracking & Camera Portal (21 Filter)")
        st.markdown("---")

        st.markdown("### 🎮 Panduan Gestur Tangan")
        st.markdown("""
        - 🖐️ **Buka Portal**: Angkat **kedua tangan** (jempol & telunjuk) untuk membuat area portal filter persegi!
        - 🤙 **Ganti Filter (1 Tangan)**: Dekatkan **Jempol + Kelingking [P]** hingga menyentuh.
        - 👆 **Ganti Filter (2 Tangan)**: Sentuhkan **kedua jari telunjuk**.
        """)
        st.markdown("---")

        st.markdown("### 🎨 21 Filter Visual")
        st.markdown("""
        `MONO` `DUAL-TONE` `PIXELATE` `INVERT` `SEPIA`
        `BLUR` `THERMAL` `SKETCH` `GLITCH` `NEON`
        `GALAXY` `VINTAGE` `CARTOON` `EMBOSS` `NIGHT`
        `OCEAN` `FIRE` `RAINBOW` `MIRROR` `VIGNETTE` `OIL`
        """)
        st.markdown("---")
        st.info("💡 **Privasi Terjamin**: Kamera & AI MediaPipe diproses 100% di browser Anda (Client-Side) tanpa latency server!")

    st.markdown("<div class='custom-title'>✨ RETROLENS</div>", unsafe_allow_html=True)
    st.markdown("<div class='custom-sub'>Aplikasi Hand Tracking & 21 Filter Kamera Interaktif Real-Time</div>", unsafe_allow_html=True)

    html_code = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>RetroLens</title>
      <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
      <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          background: #0a0a14;
          color: #f1f5f9;
          font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: flex-start;
          overflow: hidden;
          padding: 8px;
        }

        #container {
          position: relative;
          width: 960px;
          max-width: 100%;
          border-radius: 14px;
          overflow: hidden;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 229, 160, 0.15);
          border: 1px solid rgba(255, 255, 255, 0.1);
          background: #111122;
        }

        #output_canvas {
          display: block;
          width: 100%;
          height: auto;
          aspect-ratio: 16 / 9;
          background: #05050c;
        }

        #webcam {
          display: none;
        }

        #overlay-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 960px;
          max-width: 100%;
          margin-top: 10px;
          gap: 10px;
          flex-wrap: wrap;
        }

        .btn {
          background: #1e1e38;
          color: #f8fafc;
          border: 1px solid rgba(255, 255, 255, 0.15);
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }
        .btn:hover {
          background: #2a2a4e;
          border-color: #00e5a0;
          color: #00e5a0;
        }
        .btn-primary {
          background: #00e5a0;
          color: #0a0a14;
          border-color: #00e5a0;
        }
        .btn-primary:hover {
          background: #00c98c;
          color: #0a0a14;
        }
        .btn-danger {
          background: #ef4444;
          color: #fff;
          border-color: #ef4444;
        }
        .btn-danger:hover {
          background: #dc2626;
        }

        #status-card {
          font-size: 13px;
          color: #94a3b8;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #00e5a0;
          box-shadow: 0 0 8px #00e5a0;
        }

        #start-overlay {
          position: absolute;
          inset: 0;
          background: rgba(10, 10, 20, 0.92);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          z-index: 50;
          gap: 14px;
        }
        #start-overlay h3 {
          font-size: 20px;
          font-weight: 700;
          color: #00e5a0;
        }
        #start-overlay p {
          color: #94a3b8;
          font-size: 13px;
          max-width: 400px;
          text-align: center;
        }
      </style>
    </head>
    <body>
      <div id="container">
        <video id="webcam" playsinline></video>
        <canvas id="output_canvas" width="960" height="540"></canvas>

        <div id="start-overlay">
          <h3>✨ Siap Menggunakan RETROLENS?</h3>
          <p>Izinkan akses webcam pada browser Anda untuk memulai deteksi gestur tangan dan 21 filter.</p>
          <button id="btn-start" class="btn btn-primary" style="padding: 12px 24px; font-size: 15px;">
            ▶ Aktifkan Kamera & Mulai
          </button>
        </div>
      </div>

      <div id="overlay-bar">
        <div id="status-card">
          <span id="stat-dot" class="status-dot"></span>
          <span id="stat-text">Menunggu izin kamera...</span>
        </div>

        <div style="display: flex; gap: 8px;">
          <button id="btn-prev" class="btn">◀ Filter Sebelumnya</button>
          <button id="btn-next" class="btn">Filter Berikutnya ▶</button>
          <button id="btn-toggle" class="btn btn-danger">Hentikan Kamera</button>
        </div>
      </div>

      <script>
        const FILTERS = [
          "MONO",    "DUAL-TONE", "PIXELATE", "INVERT",  "SEPIA",
          "BLUR",    "THERMAL",   "SKETCH",   "GLITCH",  "NEON",
          "GALAXY",  "VINTAGE",   "CARTOON",  "EMBOSS",  "NIGHT",
          "OCEAN",   "FIRE",      "RAINBOW",  "MIRROR",  "VIGNETTE",
          "OIL"
        ];

        const FILTER_COLORS = {
          "MONO":      [180, 180, 180], "DUAL-TONE": [255,  20, 200],
          "PIXELATE":  [  0, 165, 255], "INVERT":    [255,   0, 220],
          "SEPIA":     [210, 120,  40], "BLUR":      [200, 200, 255],
          "THERMAL":   [255,  80,   0], "SKETCH":    [220, 220, 220],
          "GLITCH":    [255,  60,  60], "NEON":      [  0, 255, 255],
          "GALAXY":    [200, 100, 255], "VINTAGE":   [200, 140,  60],
          "CARTOON":   [  0, 230, 255], "EMBOSS":    [200, 200, 200],
          "NIGHT":     [  0, 220,  60], "OCEAN":     [ 20, 130, 220],
          "FIRE":      [255, 100,   0], "RAINBOW":   [  0, 255, 160],
          "MIRROR":    [200, 220, 255], "VIGNETTE":  [150, 120, 120],
          "OIL":       [ 70, 200, 110],
        };

        const video = document.getElementById('webcam');
        const canvas = document.getElementById('output_canvas');
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        const startOverlay = document.getElementById('start-overlay');
        const btnStart = document.getElementById('btn-start');
        const btnToggle = document.getElementById('btn-toggle');
        const btnNext = document.getElementById('btn-next');
        const btnPrev = document.getElementById('btn-prev');
        const statDot = document.getElementById('stat-dot');
        const statText = document.getElementById('stat-text');

        const offCanvas = document.createElement('canvas');
        const offCtx = offCanvas.getContext('2d', { willReadFrequently: true });

        let currentFilter = 0;
        let gestureTriggered = false;
        let cameraRunning = false;
        let cameraObj = null;
        let handsObj = null;
        let fps = 0;
        let lastTime = performance.now();

        function rgbToHex(rgb) {
          return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
        }

        function drawTextWithShadow(text, x, y, font, color, align = 'left') {
          ctx.font = font;
          ctx.textAlign = align;
          ctx.fillStyle = '#000000';
          ctx.fillText(text, x + 2, y + 2);
          ctx.fillStyle = color;
          ctx.fillText(text, x, y);
        }

        function applyFilter(filterName, rx, ry, rw, rh) {
          offCanvas.width = rw;
          offCanvas.height = rh;

          if (filterName === "MIRROR") {
            offCtx.save();
            offCtx.translate(rw, 0);
            offCtx.scale(-1, 1);
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.restore();
            return offCanvas;
          }

          offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
          let imgData = offCtx.getImageData(0, 0, rw, rh);
          let d = imgData.data;

          if (filterName === "MONO") {
            for (let i = 0; i < d.length; i += 4) {
              let g = 0.299 * d[i] + 0.587 * d[i+1] + 0.114 * d[i+2];
              d[i] = d[i+1] = d[i+2] = g;
            }
          } else if (filterName === "INVERT") {
            for (let i = 0; i < d.length; i += 4) {
              d[i] = 255 - d[i]; d[i+1] = 255 - d[i+1]; d[i+2] = 255 - d[i+2];
            }
          } else if (filterName === "SEPIA") {
            for (let i = 0; i < d.length; i += 4) {
              let r = d[i], g = d[i+1], b = d[i+2];
              d[i]   = Math.min(255, 0.393*r + 0.769*g + 0.189*b);
              d[i+1] = Math.min(255, 0.349*r + 0.686*g + 0.168*b);
              d[i+2] = Math.min(255, 0.272*r + 0.534*g + 0.131*b);
            }
          } else if (filterName === "DUAL-TONE") {
            for (let i = 0; i < d.length; i += 4) {
              let g = (d[i] + d[i+1] + d[i+2]) / 3;
              if (g > 127) {
                d[i] = 255; d[i+1] = 165; d[i+2] = 0;
              } else {
                d[i] = 255; d[i+1] = 20; d[i+2] = 147;
              }
            }
          } else if (filterName === "PIXELATE") {
            let pw = Math.max(1, Math.floor(rw / 12));
            let ph = Math.max(1, Math.floor(rh / 12));
            let tempC = document.createElement('canvas');
            tempC.width = pw; tempC.height = ph;
            let tempCtx = tempC.getContext('2d');
            tempCtx.drawImage(video, rx, ry, rw, rh, 0, 0, pw, ph);
            offCtx.imageSmoothingEnabled = false;
            offCtx.drawImage(tempC, 0, 0, pw, ph, 0, 0, rw, rh);
            offCtx.imageSmoothingEnabled = true;
            return offCanvas;
          } else if (filterName === "BLUR") {
            offCtx.filter = 'blur(10px)';
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.filter = 'none';
            return offCanvas;
          } else if (filterName === "THERMAL") {
            for (let i = 0; i < d.length; i += 4) {
              let v = (d[i] + d[i+1] + d[i+2]) / (3 * 255);
              d[i]   = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 3))));
              d[i+1] = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 2))));
              d[i+2] = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 1))));
            }
          } else if (filterName === "SKETCH") {
            for (let y = 0; y < rh - 1; y++) {
              for (let x = 0; x < rw - 1; x++) {
                let idx = (y * rw + x) * 4;
                let next = ((y + 1) * rw + (x + 1)) * 4;
                let g1 = (d[idx] + d[idx+1] + d[idx+2]) / 3;
                let g2 = (d[next] + d[next+1] + d[next+2]) / 3;
                let diff = 255 - Math.min(255, Math.abs(g1 - g2) * 6);
                d[idx] = d[idx+1] = d[idx+2] = diff;
              }
            }
          } else if (filterName === "GLITCH") {
            let shift = Math.max(5, Math.floor(rw / 20));
            let copy = new Uint8ClampedArray(d);
            for (let y = 0; y < rh; y++) {
              for (let x = 0; x < rw; x++) {
                let idx = (y * rw + x) * 4;
                let rxIdx = (y * rw + Math.min(rw - 1, x + shift)) * 4;
                let bxIdx = (y * rw + Math.max(0, x - shift)) * 4;
                d[idx] = copy[rxIdx];
                d[idx+2] = copy[bxIdx+2];
              }
            }
          } else if (filterName === "NEON") {
            for (let y = 0; y < rh - 1; y++) {
              for (let x = 0; x < rw - 1; x++) {
                let idx = (y * rw + x) * 4;
                let right = (y * rw + x + 1) * 4;
                let down = ((y + 1) * rw + x) * 4;
                let g = (d[idx] + d[idx+1] + d[idx+2]) / 3;
                let gr = (d[right] + d[right+1] + d[right+2]) / 3;
                let gd = (d[down] + d[down+1] + d[down+2]) / 3;
                let edge = Math.hypot(gr - g, gd - g) * 3;
                if (edge > 40) {
                  d[idx] = 0; d[idx+1] = 255; d[idx+2] = 255;
                } else {
                  d[idx] = 10; d[idx+1] = 10; d[idx+2] = 25;
                }
              }
            }
          } else if (filterName === "GALAXY") {
            offCtx.fillStyle = "#160a28";
            offCtx.fillRect(0, 0, rw, rh);
            for (let i = 0; i < 50; i++) {
              let sx = (Math.sin(i * 45 + Date.now() * 0.001) * 0.5 + 0.5) * rw;
              let sy = (Math.cos(i * 25 + Date.now() * 0.001) * 0.5 + 0.5) * rh;
              offCtx.fillStyle = (i % 2 === 0) ? "#c864ff" : "#ffffff";
              offCtx.beginPath();
              offCtx.arc(sx, sy, (i % 3) + 1, 0, Math.PI * 2);
              offCtx.fill();
            }
            offCtx.globalAlpha = 0.45;
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.globalAlpha = 1.0;
            return offCanvas;
          } else if (filterName === "VINTAGE") {
            let cx = rw / 2, cy = rh / 2;
            let maxD = Math.hypot(cx, cy) + 1e-6;
            for (let y = 0; y < rh; y++) {
              for (let x = 0; x < rw; x++) {
                let idx = (y * rw + x) * 4;
                let r = d[idx], g = d[idx+1], b = d[idx+2];
                let sr = 0.393*r + 0.769*g + 0.189*b;
                let sg = 0.349*r + 0.686*g + 0.168*b;
                let sb = 0.272*r + 0.534*g + 0.131*b;
                let dist = Math.hypot(x - cx, y - cy);
                let vig = Math.max(0, 1 - Math.pow(dist / maxD, 1.5));
                let grain = (Math.random() - 0.5) * 20;
                d[idx]   = Math.min(255, Math.max(0, sr * vig + grain));
                d[idx+1] = Math.min(255, Math.max(0, sg * vig + grain));
                d[idx+2] = Math.min(255, Math.max(0, sb * vig + grain));
              }
            }
          } else if (filterName === "CARTOON") {
            for (let y = 0; y < rh - 1; y++) {
              for (let x = 0; x < rw - 1; x++) {
                let idx = (y * rw + x) * 4;
                let right = (y * rw + x + 1) * 4;
                let down = ((y + 1) * rw + x) * 4;
                let g = (d[idx] + d[idx+1] + d[idx+2]) / 3;
                let gr = (d[right] + d[right+1] + d[right+2]) / 3;
                let gd = (d[down] + d[down+1] + d[down+2]) / 3;
                let edge = Math.hypot(gr - g, gd - g);
                if (edge > 25) {
                  d[idx] = d[idx+1] = d[idx+2] = 0;
                } else {
                  d[idx]   = Math.floor(d[idx] / 64) * 64 + 32;
                  d[idx+1] = Math.floor(d[idx+1] / 64) * 64 + 32;
                  d[idx+2] = Math.floor(d[idx+2] / 64) * 64 + 32;
                }
              }
            }
          } else if (filterName === "EMBOSS") {
            let copy = new Uint8ClampedArray(d);
            for (let y = 1; y < rh - 1; y++) {
              for (let x = 1; x < rw - 1; x++) {
                let idx = (y * rw + x) * 4;
                let pTL = ((y - 1) * rw + (x - 1)) * 4;
                let pBR = ((y + 1) * rw + (x + 1)) * 4;
                let gTL = (copy[pTL] + copy[pTL+1] + copy[pTL+2]) / 3;
                let gBR = (copy[pBR] + copy[pBR+1] + copy[pBR+2]) / 3;
                let val = Math.min(255, Math.max(0, (gBR - gTL) * 1.5 + 128));
                d[idx] = d[idx+1] = d[idx+2] = val;
              }
            }
          } else if (filterName === "NIGHT") {
            for (let i = 0; i < d.length; i += 4) {
              let g = (d[i] + d[i+1] + d[i+2]) / 3;
              d[i] = 0; d[i+1] = Math.min(255, g * 1.8 + 20); d[i+2] = 0;
            }
          } else if (filterName === "OCEAN") {
            for (let i = 0; i < d.length; i += 4) {
              d[i]   = Math.floor(d[i] * 0.35);
              d[i+1] = Math.floor(d[i+1] * 0.85);
              d[i+2] = Math.min(255, Math.floor(d[i+2] * 1.45));
            }
          } else if (filterName === "FIRE") {
            for (let i = 0; i < d.length; i += 4) {
              let g = (d[i] + d[i+1] + d[i+2]) / 3;
              d[i]   = Math.min(255, g * 3);
              d[i+1] = Math.min(255, Math.max(0, (g - 85) * 3));
              d[i+2] = Math.min(255, Math.max(0, (g - 170) * 3));
            }
          } else if (filterName === "RAINBOW") {
            for (let y = 0; y < rh; y++) {
              for (let x = 0; x < rw; x++) {
                let idx = (y * rw + x) * 4;
                let g = (d[idx] + d[idx+1] + d[idx+2]) / 3;
                let angle = (x / rw) * 6.28;
                d[idx]   = Math.min(255, g * 0.5 + Math.sin(angle) * 120 + 120);
                d[idx+1] = Math.min(255, g * 0.5 + Math.sin(angle + 2.09) * 120 + 120);
                d[idx+2] = Math.min(255, g * 0.5 + Math.sin(angle + 4.18) * 120 + 120);
              }
            }
          } else if (filterName === "VIGNETTE") {
            let cx = rw / 2, cy = rh / 2;
            let maxD = Math.hypot(cx, cy) + 1e-6;
            for (let y = 0; y < rh; y++) {
              for (let x = 0; x < rw; x++) {
                let idx = (y * rw + x) * 4;
                let dist = Math.hypot(x - cx, y - cy);
                let vig = Math.max(0, 1 - Math.pow(dist / maxD, 1.8));
                d[idx]   = Math.floor(d[idx] * vig);
                d[idx+1] = Math.floor(d[idx+1] * vig);
                d[idx+2] = Math.floor(d[idx+2] * vig);
              }
            }
          } else if (filterName === "OIL") {
            for (let i = 0; i < d.length; i += 4) {
              d[i]   = Math.floor(d[i] / 40) * 40;
              d[i+1] = Math.floor(d[i+1] / 40) * 40;
              d[i+2] = Math.floor(d[i+2] / 40) * 40;
            }
          }

          offCtx.putImageData(imgData, 0, 0);
          return offCanvas;
        }

        function drawHUD(w, h, filterName, curIdx, fpsVal) {
          const accentRGB = FILTER_COLORS[filterName] || [0, 229, 160];
          const accentColor = rgbToHex(accentRGB);

          // Top bar
          ctx.fillStyle = 'rgba(10, 10, 20, 0.85)';
          ctx.fillRect(0, 0, w, 46);
          ctx.strokeStyle = accentColor;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(0, 46);
          ctx.lineTo(w, 46);
          ctx.stroke();

          drawTextWithShadow('RETROLENS', 18, 30, 'bold 18px Segoe UI', accentColor);

          let fpsColor = (fpsVal >= 20) ? '#00e5a0' : (fpsVal >= 10 ? '#f59e0b' : '#ef4444');
          drawTextWithShadow(`FPS ${Math.round(fpsVal)}`, w - 90, 30, 'bold 15px Segoe UI', fpsColor);

          // Bottom Filter Strip
          const barH = 46;
          const barTop = h - barH;
          ctx.fillStyle = 'rgba(10, 10, 20, 0.88)';
          ctx.fillRect(0, barTop, w, barH);
          ctx.strokeStyle = accentColor;
          ctx.beginPath();
          ctx.moveTo(0, barTop);
          ctx.lineTo(w, barTop);
          ctx.stroke();

          drawTextWithShadow(`${curIdx + 1}/${FILTERS.length}`, w - 55, barTop - 8, '12px Segoe UI', '#94a3b8');

          const visible = 9;
          const half = Math.floor(visible / 2);
          const slotW = w / visible;

          for (let i = 0; i < visible; i++) {
            let idx = (curIdx - half + i + FILTERS.length * 10) % FILTERS.length;
            let fname = FILTERS[idx];
            let isCur = (idx === curIdx);
            let sx = i * slotW;
            let scx = sx + slotW / 2;
            let scy = barTop + barH / 2;

            if (isCur) {
              ctx.fillStyle = 'rgba(0, 229, 160, 0.18)';
              ctx.fillRect(sx + 4, barTop + 4, slotW - 8, barH - 8);
              ctx.strokeStyle = accentColor;
              ctx.lineWidth = 1.5;
              ctx.strokeRect(sx + 4, barTop + 4, slotW - 8, barH - 8);
              drawTextWithShadow(fname, scx, scy + 4, 'bold 13px Segoe UI', accentColor, 'center');
            } else {
              drawTextWithShadow(fname, scx, scy + 4, '11px Segoe UI', '#64748b', 'center');
            }
          }
        }

        function onResults(results) {
          const now = performance.now();
          const rawFps = 1000 / Math.max(1, now - lastTime);
          lastTime = now;
          fps = fps * 0.85 + rawFps * 0.15;

          const w = canvas.width;
          const h = canvas.height;

          // Flip video horizontal (Mirror)
          ctx.save();
          ctx.translate(w, 0);
          ctx.scale(-1, 1);
          ctx.drawImage(video, 0, 0, w, h);
          ctx.restore();

          const filterName = FILTERS[currentFilter];
          const accentRGB = FILTER_COLORS[filterName] || [0, 229, 160];
          const accentColor = rgbToHex(accentRGB);

          let changeFilter = false;
          const ptsPortal = [];

          if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            const handsLms = results.multiHandLandmarks;

            // 2-Hand Gesture: Index touching index
            if (handsLms.length >= 2) {
              let p0 = handsLms[0][8];
              let p1 = handsLms[1][8];
              let pt0 = { x: (1 - p0.x) * w, y: p0.y * h };
              let pt1 = { x: (1 - p1.x) * w, y: p1.y * h };
              if (Math.hypot(pt0.x - pt1.x, pt0.y - pt1.y) < 45) {
                changeFilter = true;
              }
            }

            for (let hand of handsLms) {
              let thumbPt = { x: (1 - hand[4].x) * w, y: hand[4].y * h };
              let indexPt = { x: (1 - hand[8].x) * w, y: hand[8].y * h };
              let pinkyPt = { x: (1 - hand[20].x) * w, y: hand[20].y * h };

              ptsPortal.push(thumbPt);
              ptsPortal.push(indexPt);

              // Gesture: Thumb + Pinky touch
              let distTP = Math.hypot(thumbPt.x - pinkyPt.x, thumbPt.y - pinkyPt.y);
              let nearTrigger = distTP < 85;
              let onTrigger = distTP < 45;

              if (onTrigger) {
                changeFilter = true;
              }

              // Connecting gesture line
              if (nearTrigger) {
                ctx.strokeStyle = onTrigger ? '#ef4444' : '#f59e0b';
                ctx.lineWidth = onTrigger ? 3 : 1.5;
                ctx.beginPath();
                ctx.moveTo(thumbPt.x, thumbPt.y);
                ctx.lineTo(pinkyPt.x, pinkyPt.y);
                ctx.stroke();
              }

              // Pinky Landmark [20]
              let pkColor = onTrigger ? '#ef4444' : '#c832ff';
              ctx.fillStyle = pkColor;
              ctx.beginPath(); ctx.arc(pinkyPt.x, pinkyPt.y, 13, 0, Math.PI * 2); ctx.fill();
              ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5;
              ctx.beginPath(); ctx.arc(pinkyPt.x, pinkyPt.y, 16, 0, Math.PI * 2); ctx.stroke();
              drawTextWithShadow('P', pinkyPt.x, pinkyPt.y + 4, 'bold 11px Segoe UI', '#ffffff', 'center');

              // Thumb [4] & Index [8] Landmarks
              for (let pt of [thumbPt, indexPt]) {
                ctx.fillStyle = accentColor;
                ctx.beginPath(); ctx.arc(pt.x, pt.y, 11, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.arc(pt.x, pt.y, 14, 0, Math.PI * 2); ctx.stroke();
              }
            }

            // Trigger debounce
            if (changeFilter) {
              if (!gestureTriggered) {
                currentFilter = (currentFilter + 1) % FILTERS.length;
                gestureTriggered = true;
              }
            } else {
              gestureTriggered = false;
            }

            // Gambar Portal Polygon
            if (ptsPortal.length >= 4) {
              ptsPortal.sort((a, b) => a.y - b.y);
              let topPts = ptsPortal.slice(0, 2).sort((a, b) => a.x - b.x);
              let botPts = ptsPortal.slice(2, 4).sort((a, b) => a.x - b.x);
              let poly = [topPts[0], topPts[1], botPts[1], botPts[0]];

              let minX = Math.max(0, Math.min(...poly.map(p => p.x)));
              let maxX = Math.min(w, Math.max(...poly.map(p => p.x)));
              let minY = Math.max(0, Math.min(...poly.map(p => p.y)));
              let maxY = Math.min(h, Math.max(...poly.map(p => p.y)));
              let rw = maxX - minX;
              let rh = maxY - minY;

              if (rw > 20 && rh > 20) {
                let filteredCanvas = applyFilter(filterName, minX, minY, rw, rh);

                ctx.save();
                ctx.beginPath();
                ctx.moveTo(poly[0].x, poly[0].y);
                for (let i = 1; i < poly.length; i++) ctx.lineTo(poly[i].x, poly[i].y);
                ctx.closePath();
                ctx.clip();

                ctx.drawImage(filteredCanvas, minX, minY);
                ctx.restore();

                // Polygon outline & Sparks
                ctx.strokeStyle = accentColor;
                ctx.lineWidth = 2.5;
                ctx.beginPath();
                ctx.moveTo(poly[0].x, poly[0].y);
                for (let i = 1; i < poly.length; i++) ctx.lineTo(poly[i].x, poly[i].y);
                ctx.closePath();
                ctx.stroke();

                // Particles
                for (let i = 0; i < 4; i++) {
                  let p1 = poly[i], p2 = poly[(i+1)%4];
                  for (let j = 0; j < 4; j++) {
                    let a = Math.random();
                    let gx = p1.x * a + p2.x * (1 - a) + (Math.random() - 0.5) * 16;
                    let gy = p1.y * a + p2.y * (1 - a) + (Math.random() - 0.5) * 16;
                    ctx.fillStyle = accentColor;
                    ctx.beginPath(); ctx.arc(gx, gy, Math.random() * 2 + 1, 0, Math.PI * 2); ctx.fill();
                  }
                }

                drawTextWithShadow(filterName, topPts[0].x + 8, Math.max(60, topPts[0].y - 12), 'bold 15px Segoe UI', accentColor);
              }
            }
          }

          drawHUD(w, h, filterName, currentFilter, fps);
        }

        async function initCamera() {
          try {
            statDot.style.background = '#f59e0b';
            statDot.style.boxShadow = '0 0 8px #f59e0b';
            statText.textContent = 'Memuat model AI MediaPipe...';

            handsObj = new Hands({
              locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
            });

            handsObj.setOptions({
              maxNumHands: 2,
              modelComplexity: 1,
              minDetectionConfidence: 0.4,
              minTrackingConfidence: 0.4
            });

            handsObj.onResults(onResults);

            cameraObj = new Camera(video, {
              onFrame: async () => {
                if (cameraRunning) {
                  await handsObj.send({ image: video });
                }
              },
              width: 960,
              height: 540
            });

            await cameraObj.start();
            cameraRunning = true;
            startOverlay.style.display = 'none';
            btnToggle.textContent = 'Hentikan Kamera';
            btnToggle.className = 'btn btn-danger';
            statDot.style.background = '#00e5a0';
            statDot.style.boxShadow = '0 0 8px #00e5a0';
            statText.textContent = '🟢 Kamera Aktif — Deteksi Gestur Berjalan';
          } catch (err) {
            console.error(err);
            statDot.style.background = '#ef4444';
            statDot.style.boxShadow = '0 0 8px #ef4444';
            statText.textContent = '❌ Izin webcam ditolak atau kamera tidak ditemukan.';
            startOverlay.style.display = 'flex';
          }
        }

        function stopCamera() {
          cameraRunning = false;
          if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
          }
          startOverlay.style.display = 'flex';
          btnToggle.textContent = 'Mulai Kamera';
          btnToggle.className = 'btn btn-primary';
          statDot.style.background = '#64748b';
          statDot.style.boxShadow = 'none';
          statText.textContent = 'Kamera dijeda.';
        }

        btnStart.addEventListener('click', () => {
          initCamera();
        });

        btnToggle.addEventListener('click', () => {
          if (cameraRunning) {
            stopCamera();
          } else {
            initCamera();
          }
        });

        btnNext.addEventListener('click', () => {
          currentFilter = (currentFilter + 1) % FILTERS.length;
        });

        btnPrev.addEventListener('click', () => {
          currentFilter = (currentFilter - 1 + FILTERS.length) % FILTERS.length;
        });

        window.addEventListener('load', () => {
          initCamera();
        });
      </script>
    </body>
    </html>
    """

    components.html(html_code, height=660, scrolling=False)


def run_desktop_opencv():
    """Jalankan versi desktop OpenCV lokal."""
    import cv2
    import mediapipe as mp
    import time
    import math
    import numpy as np

    BaseOptions           = mp.tasks.BaseOptions
    HandLandmarker        = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    VisionRunningMode     = mp.tasks.vision.RunningMode

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.4,
        min_hand_presence_confidence=0.4,
        min_tracking_confidence=0.4
    )
    landmarker = HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    cap.set(cv2.CAP_PROP_FPS,          30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS,    1)
    cap.set(cv2.CAP_PROP_ZOOM,         100)
    cv2.namedWindow("RETROLENS", cv2.WINDOW_NORMAL)

    FILTERS = [
        "MONO",    "DUAL-TONE", "PIXELATE", "INVERT",  "SEPIA",
        "BLUR",    "THERMAL",   "SKETCH",   "GLITCH",  "NEON",
        "GALAXY",  "VINTAGE",   "CARTOON",  "EMBOSS",  "NIGHT",
        "OCEAN",   "FIRE",      "RAINBOW",  "MIRROR",  "VIGNETTE",
        "OIL"
    ]

    FILTER_COLORS = {
        "MONO":      (180, 180, 180), "DUAL-TONE": (255,  20, 200),
        "PIXELATE":  (  0, 165, 255), "INVERT":    (255,   0, 220),
        "SEPIA":     ( 40, 120, 210), "BLUR":      (200, 200, 255),
        "THERMAL":   (  0,  80, 255), "SKETCH":    (220, 220, 220),
        "GLITCH":    ( 60,  60, 255), "NEON":      (  0, 255, 255),
        "GALAXY":    (200, 100, 255), "VINTAGE":   ( 60, 140, 200),
        "CARTOON":   (  0, 230, 255), "EMBOSS":    (200, 200, 200),
        "NIGHT":     (  0, 220,  60), "OCEAN":     (220, 130,  20),
        "FIRE":      (  0, 100, 255), "RAINBOW":   (  0, 255, 160),
        "MIRROR":    (200, 220, 255), "VIGNETTE":  (120, 120, 150),
        "OIL":       ( 70, 200, 110),
    }

    current_filter    = 0
    gesture_triggered = False
    fps_time = time.time()
    fps      = 0.0

    PINKY_COLOR  = (200,  50, 255)
    PINKY_ACTIVE = (0,    80, 255)

    _vig_cache = {}
    def get_vig_mask(h, w, power):
        key = (h, w, power)
        if key not in _vig_cache:
            cx, cy = w//2, h//2
            Y, X   = np.ogrid[:h, :w]
            d      = np.sqrt((X-cx)**2 + (Y-cy)**2)
            md     = np.sqrt(cx**2 + cy**2) + 1e-6
            mask   = np.clip(1-(d/md)**power, 0, 1)
            _vig_cache[key] = np.stack([mask]*3, axis=2).astype(np.float32)
        return _vig_cache[key]

    def put_text_shadow(img, text, pos, scale, color, thickness=1):
        x, y = pos
        cv2.putText(img, text, (x+1, y+1), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, (0,0,0), thickness+2, cv2.LINE_AA)
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, color, thickness, cv2.LINE_AA)

    def rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
        if x2 <= x1 or y2 <= y1:
            return
        region = img[y1:y2, x1:x2]
        bg = np.full_like(region, color)
        img[y1:y2, x1:x2] = cv2.addWeighted(bg, alpha, region, 1-alpha, 0)

    def draw_hud(img, filter_name, cur_idx, fps_val):
        h, w   = img.shape[:2]
        accent = FILTER_COLORS.get(filter_name, (0, 255, 255))
        total  = len(FILTERS)

        rect_alpha(img, 0, 0, w, 46, (10, 10, 20), alpha=0.78)
        cv2.line(img, (0, 46), (w, 46), accent, 1)
        put_text_shadow(img, "RETROLENS", (18, 32), 0.90, accent, 2)
        fps_color = (0,230,90) if fps_val>=20 else (0,180,255) if fps_val>=10 else (0,80,255)
        put_text_shadow(img, f"FPS {int(fps_val):>3}", (w-100, 32), 0.58, fps_color, 1)

        bar_h   = 46
        bar_top = h - bar_h
        rect_alpha(img, 0, bar_top, w, h, (10, 10, 20), alpha=0.80)
        cv2.line(img, (0, bar_top), (w, bar_top), accent, 1)
        put_text_shadow(img, f"{cur_idx+1}/{total}", (w-60, bar_top-6), 0.42, (140,140,160), 1)

        visible = 9
        half    = visible // 2
        slot_w  = w // visible
        for i in range(visible):
            idx    = (cur_idx - half + i) % total
            fname  = FILTERS[idx]
            is_cur = (idx == cur_idx)
            sx     = i * slot_w
            scx    = sx + slot_w // 2
            scy    = bar_top + bar_h // 2
            if is_cur:
                rect_alpha(img, sx+3, bar_top+3, sx+slot_w-3, h-3, accent, alpha=0.30)
                cv2.rectangle(img, (sx+3, bar_top+3), (sx+slot_w-3, h-3), accent, 1)
                color, scale = accent, 0.50
            else:
                color, scale = (130, 130, 140), 0.38
            (tw, th), _ = cv2.getTextSize(fname, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
            put_text_shadow(img, fname, (scx - tw//2, scy + th//2), scale, color, 1)

    def apply_filter(roi, filter_name):
        if roi is None or roi.size == 0:
            return roi
        if filter_name == "MONO":
            return cv2.cvtColor(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        elif filter_name == "INVERT":
            return cv2.bitwise_not(roi)
        elif filter_name == "BLUR":
            return cv2.GaussianBlur(roi, (15, 15), 0)
        elif filter_name == "SEPIA":
            k = np.array([[0.272,0.534,0.131],[0.349,0.686,0.168],[0.393,0.769,0.189]])
            return np.clip(cv2.transform(roi, k), 0, 255).astype(np.uint8)
        elif filter_name == "DUAL-TONE":
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, m = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            out = np.zeros_like(roi)
            out[m==255] = [  0,165,255]
            out[m==  0] = [147, 20,255]
            return out
        elif filter_name == "PIXELATE":
            h_r, w_r = roi.shape[:2]
            pw = max(1, w_r//10); ph = max(1, h_r//10)
            return cv2.resize(cv2.resize(roi, (pw, ph), interpolation=cv2.INTER_LINEAR),
                              (w_r, h_r), interpolation=cv2.INTER_NEAREST)
        elif filter_name == "THERMAL":
            return cv2.applyColorMap(roi, cv2.COLORMAP_JET)
        elif filter_name == "SKETCH":
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(cv2.bitwise_not(gray), (21,21), 0)
            return cv2.cvtColor(cv2.divide(gray, 255-blur, scale=256), cv2.COLOR_GRAY2BGR)
        elif filter_name == "GLITCH":
            h_r, w_r = roi.shape[:2]
            shift = max(5, w_r//20)
            out = roi.copy()
            if w_r > shift:
                out[:,:-shift,2] = roi[:,shift:, 2]
                out[:,shift:, 0] = roi[:,:-shift,0]
            return out
        elif filter_name == "NEON":
            gray  = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(cv2.GaussianBlur(gray,(5,5),0), 50, 150)
            e3    = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            e3[np.where((e3==[255,255,255]).all(axis=2))] = [255,255,0]
            return cv2.dilate(e3, np.ones((3,3),np.uint8), iterations=1)
        elif filter_name == "VINTAGE":
            k = np.array([[0.272,0.534,0.131],[0.349,0.686,0.168],[0.393,0.769,0.189]])
            sepia = np.clip(cv2.transform(roi, k), 0, 255).astype(np.uint8)
            h_r, w_r = roi.shape[:2]
            vig = get_vig_mask(h_r, w_r, 1.5)
            grain = np.random.randint(0, 25, sepia.shape, dtype=np.uint8)
            return np.clip(sepia.astype(np.float32)*vig - grain, 0, 255).astype(np.uint8)
        elif filter_name == "CARTOON":
            color = cv2.bilateralFilter(roi, 7, 150, 150)
            gray  = cv2.medianBlur(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            return cv2.bitwise_and(color, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
        elif filter_name == "EMBOSS":
            k = np.array([[-2,-1,0],[-1,1,1],[0,1,2]], dtype=np.float32)
            gf  = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
            emb = np.clip(cv2.filter2D(gf, cv2.CV_32F, k)+128.0, 0, 255).astype(np.uint8)
            return cv2.cvtColor(emb, cv2.COLOR_GRAY2BGR)
        elif filter_name == "NIGHT":
            night = np.zeros_like(roi)
            night[:,:,1] = cv2.equalizeHist(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
            return night
        elif filter_name == "OCEAN":
            f = roi.astype(np.float32)
            f[:,:,0] = np.clip(f[:,:,0]*1.4,  0,255)
            f[:,:,1] = np.clip(f[:,:,1]*0.9,  0,255)
            f[:,:,2] = np.clip(f[:,:,2]*0.45, 0,255)
            return f.astype(np.uint8)
        elif filter_name == "FIRE":
            return cv2.applyColorMap(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_HOT)
        elif filter_name == "RAINBOW":
            return cv2.applyColorMap(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_RAINBOW)
        elif filter_name == "MIRROR":
            return cv2.flip(roi, 1)
        elif filter_name == "VIGNETTE":
            h_v, w_v = roi.shape[:2]
            vig = get_vig_mask(h_v, w_v, 1.8)
            return (roi.astype(np.float32) * vig).astype(np.uint8)
        elif filter_name == "OIL":
            return cv2.medianBlur(cv2.medianBlur(roi, 7), 5)
        return roi

    try:
        while True:
            success, img = cap.read()
            if not success:
                break

            img  = cv2.flip(img, 1)
            h, w = img.shape[:2]

            img_rgb      = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image     = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            timestamp_ms = time.time_ns() // 1_000_000

            results     = landmarker.detect_for_video(mp_image, timestamp_ms)
            filter_name = FILTERS[current_filter]
            accent      = FILTER_COLORS.get(filter_name, (0, 255, 255))

            now      = time.time()
            raw_fps  = 1.0 / max(now - fps_time, 1e-6)
            fps_time = now
            fps      = fps * 0.85 + raw_fps * 0.15

            pts_portal    = []
            change_filter = False

            if results.hand_landmarks:
                if len(results.hand_landmarks) >= 2:
                    p0  = results.hand_landmarks[0][8]
                    p1  = results.hand_landmarks[1][8]
                    pt0 = (int(p0.x*w), int(p0.y*h))
                    pt1 = (int(p1.x*w), int(p1.y*h))
                    if math.hypot(pt0[0]-pt1[0], pt0[1]-pt1[1]) < 40:
                        change_filter = True

                for hand_lms in results.hand_landmarks:
                    thumb_pt = (int(hand_lms[4].x*w),  int(hand_lms[4].y*h))
                    index_pt = (int(hand_lms[8].x*w),  int(hand_lms[8].y*h))
                    pinky_pt = (int(hand_lms[20].x*w), int(hand_lms[20].y*h))

                    pts_portal.append(list(thumb_pt))
                    pts_portal.append(list(index_pt))

                    dist_tp      = math.hypot(thumb_pt[0]-pinky_pt[0], thumb_pt[1]-pinky_pt[1])
                    near_trigger = dist_tp < 80
                    on_trigger   = dist_tp < 40
                    if on_trigger:
                        change_filter = True

                    if near_trigger:
                        lc = PINKY_ACTIVE if on_trigger else (0, 200, 255)
                        lt = 3 if on_trigger else 1
                        cv2.line(img, thumb_pt, pinky_pt, lc, lt, cv2.LINE_AA)

                    pk_c = PINKY_ACTIVE if on_trigger else PINKY_COLOR
                    cv2.circle(img, pinky_pt, 13, pk_c, -1)
                    cv2.circle(img, pinky_pt, 17, (255,255,255), 1)
                    cv2.circle(img, pinky_pt, 20, pk_c, 1)
                    put_text_shadow(img, "P", (pinky_pt[0]-5, pinky_pt[1]+5), 0.38, (255,255,255), 1)

                    for pt in [thumb_pt, index_pt]:
                        cv2.circle(img, pt, 11, accent, -1)
                        cv2.circle(img, pt, 15, (255,255,255), 1)
                        cv2.circle(img, pt, 18, accent, 1)

                if change_filter:
                    if not gesture_triggered:
                        current_filter    = (current_filter+1) % len(FILTERS)
                        gesture_triggered = True
                else:
                    gesture_triggered = False

                if len(pts_portal) == 4:
                    pts_portal.sort(key=lambda p: p[1])
                    top_pts    = sorted(pts_portal[:2], key=lambda p: p[0])
                    bottom_pts = sorted(pts_portal[2:], key=lambda p: p[0])
                    poly = np.array([top_pts[0], top_pts[1],
                                     bottom_pts[1], bottom_pts[0]], dtype=np.int32)

                    rx, ry, rw, rh = cv2.boundingRect(poly)
                    rx = max(0, rx); ry = max(0, ry)
                    rw = min(w-rx, rw); rh = min(h-ry, rh)

                    if rw > 5 and rh > 5:
                        roi          = img[ry:ry+rh, rx:rx+rw].copy()
                        filtered_roi = apply_filter(roi, filter_name)
                        if filtered_roi is None:
                            filtered_roi = roi

                        mask_poly = np.zeros((rh, rw), dtype=np.uint8)
                        cv2.fillPoly(mask_poly, [poly - [rx, ry]], 255)
                        mask3ch = cv2.cvtColor(mask_poly, cv2.COLOR_GRAY2BGR)
                        img[ry:ry+rh, rx:rx+rw] = np.where(mask3ch==255, filtered_roi, roi)

                        cv2.polylines(img, [poly], True, (255,255,255), 1)
                        cv2.polylines(img, [poly], True, accent, 2)

                        lx = top_pts[0][0]
                        ly = max(top_pts[0][1]-14, 60)
                        put_text_shadow(img, f"  {filter_name}", (lx, ly), 0.65, accent, 2)

            draw_hud(img, filter_name, current_filter, fps)
            cv2.imshow("RETROLENS", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    if is_running_in_streamlit():
        run_streamlit_app()
    else:
        try:
            run_desktop_opencv()
        except Exception as e:
            print("Mode desktop OpenCV tidak dapat dibuka, mencoba Streamlit...", e)
            run_streamlit_app()
else:
    run_streamlit_app()
