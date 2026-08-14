"""
RETROLENS — High-Performance Pure Camera Filter App (Streamlit & Desktop)
Clean, Minimalist, Full-screen & 60 FPS Optimized
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
        page_title="RETROLENS",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Hide all Streamlit UI for a pure, clean camera screen
    st.markdown("""
    <style>
    header, footer, #MainMenu, [data-testid="stSidebar"], [data-testid="stToolbar"], .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp {
        background-color: #05050a !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    .block-container {
        padding: 0 !important;
        margin: 0 auto !important;
        max-width: 100vw !important;
        max-height: 100vh !important;
    }
    iframe {
        border: none !important;
        width: 100vw !important;
        height: 100vh !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

    html_code = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
      <title>RetroLens</title>
      <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
      <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        html, body {
          background: #05050a;
          color: #f1f5f9;
          font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
          width: 100vw;
          height: 100vh;
          overflow: hidden;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        #stage {
          position: relative;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #000;
        }

        #output_canvas {
          max-width: 100vw;
          max-height: 100vh;
          aspect-ratio: 16 / 9;
          width: 100%;
          height: auto;
          object-fit: contain;
          box-shadow: 0 0 50px rgba(0, 0, 0, 0.9);
        }

        #webcam {
          display: none;
        }

        /* Overlay jika kamera perlu diaktifkan */
        #tap-overlay {
          position: absolute;
          inset: 0;
          background: rgba(5, 5, 10, 0.88);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          z-index: 100;
          cursor: pointer;
          transition: opacity 0.3s ease;
        }
        #tap-overlay .glow-btn {
          background: linear-gradient(135deg, #00e5a0 0%, #00a5ff 100%);
          color: #05050a;
          padding: 16px 36px;
          border-radius: 50px;
          font-size: 18px;
          font-weight: 800;
          box-shadow: 0 0 30px rgba(0, 229, 160, 0.4);
          letter-spacing: 0.5px;
          border: none;
          cursor: pointer;
          transform: scale(1);
          transition: transform 0.2s ease;
        }
        #tap-overlay .glow-btn:hover {
          transform: scale(1.06);
        }
        #tap-overlay .hint {
          color: #64748b;
          font-size: 13px;
          margin-top: 14px;
        }
      </style>
    </head>
    <body>
      <div id="stage">
        <video id="webcam" playsinline></video>
        <canvas id="output_canvas" width="960" height="540"></canvas>

        <div id="tap-overlay">
          <button class="glow-btn">▶ BUKA KAMERA</button>
          <div class="hint">Klik di mana saja untuk mengaktifkan RETROLENS</div>
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
        const ctx = canvas.getContext('2d', { alpha: false });
        const tapOverlay = document.getElementById('tap-overlay');

        // Offscreen canvas untuk fast filter processing
        const offCanvas = document.createElement('canvas');
        const offCtx = offCanvas.getContext('2d', { willReadFrequently: true });
        const miniCanvas = document.createElement('canvas');
        const miniCtx = miniCanvas.getContext('2d', { willReadFrequently: true });

        let currentFilter = 0;
        let gestureTriggered = false;
        let cameraRunning = false;
        let isProcessing = false;
        let fps = 30;
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

        // Fast Filter Engine (High FPS)
        function applyFilterFast(filterName, rx, ry, rw, rh) {
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

          if (filterName === "BLUR") {
            offCtx.filter = 'blur(10px)';
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.filter = 'none';
            return offCanvas;
          }

          if (filterName === "MONO") {
            offCtx.filter = 'grayscale(100%)';
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.filter = 'none';
            return offCanvas;
          }

          if (filterName === "INVERT") {
            offCtx.filter = 'invert(100%)';
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.filter = 'none';
            return offCanvas;
          }

          if (filterName === "SEPIA") {
            offCtx.filter = 'sepia(100%)';
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.filter = 'none';
            return offCanvas;
          }

          if (filterName === "PIXELATE") {
            let pw = Math.max(1, Math.floor(rw / 12));
            let ph = Math.max(1, Math.floor(rh / 12));
            miniCanvas.width = pw; miniCanvas.height = ph;
            miniCtx.drawImage(video, rx, ry, rw, rh, 0, 0, pw, ph);
            offCtx.imageSmoothingEnabled = false;
            offCtx.drawImage(miniCanvas, 0, 0, pw, ph, 0, 0, rw, rh);
            offCtx.imageSmoothingEnabled = true;
            return offCanvas;
          }

          offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
          let imgData = offCtx.getImageData(0, 0, rw, rh);
          let d = imgData.data;
          let len = d.length;

          if (filterName === "DUAL-TONE") {
            for (let i = 0; i < len; i += 4) {
              let g = (d[i] + d[i+1] + d[i+2]) >> 2;
              if (g > 32) {
                d[i] = 255; d[i+1] = 165; d[i+2] = 0;
              } else {
                d[i] = 255; d[i+1] = 20; d[i+2] = 147;
              }
            }
          } else if (filterName === "THERMAL") {
            for (let i = 0; i < len; i += 4) {
              let v = (d[i] + d[i+1] + d[i+2]) / 765;
              d[i]   = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 3))));
              d[i+1] = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 2))));
              d[i+2] = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 1))));
            }
          } else if (filterName === "SKETCH") {
            for (let y = 0; y < rh - 1; y += 2) {
              for (let x = 0; x < rw - 1; x += 2) {
                let idx = (y * rw + x) << 2;
                let next = ((y + 1) * rw + (x + 1)) << 2;
                let g1 = (d[idx] + d[idx+1] + d[idx+2]) / 3;
                let g2 = (d[next] + d[next+1] + d[next+2]) / 3;
                let diff = 255 - Math.min(255, Math.abs(g1 - g2) * 6);
                d[idx] = d[idx+1] = d[idx+2] = diff;
                d[idx+4] = d[idx+5] = d[idx+6] = diff;
              }
            }
          } else if (filterName === "GLITCH") {
            let shift = Math.max(5, (rw / 18) | 0);
            let copy = new Uint8ClampedArray(d);
            for (let y = 0; y < rh; y++) {
              let row = (y * rw) << 2;
              for (let x = 0; x < rw; x++) {
                let idx = row + (x << 2);
                let rxIdx = row + (Math.min(rw - 1, x + shift) << 2);
                let bxIdx = row + (Math.max(0, x - shift) << 2);
                d[idx] = copy[rxIdx];
                d[idx+2] = copy[bxIdx+2];
              }
            }
          } else if (filterName === "NEON") {
            for (let y = 0; y < rh - 1; y++) {
              let row = (y * rw) << 2;
              let nextRow = ((y + 1) * rw) << 2;
              for (let x = 0; x < rw - 1; x++) {
                let idx = row + (x << 2);
                let right = row + ((x + 1) << 2);
                let down = nextRow + (x << 2);
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
            offCtx.fillStyle = "#140a22";
            offCtx.fillRect(0, 0, rw, rh);
            for (let i = 0; i < 40; i++) {
              let sx = ((Math.sin(i * 45 + Date.now() * 0.001) * 0.5 + 0.5) * rw) | 0;
              let sy = ((Math.cos(i * 25 + Date.now() * 0.001) * 0.5 + 0.5) * rh) | 0;
              offCtx.fillStyle = (i % 2 === 0) ? "#c864ff" : "#00e5a0";
              offCtx.beginPath();
              offCtx.arc(sx, sy, (i % 3) + 1, 0, Math.PI * 2);
              offCtx.fill();
            }
            offCtx.globalAlpha = 0.45;
            offCtx.drawImage(video, rx, ry, rw, rh, 0, 0, rw, rh);
            offCtx.globalAlpha = 1.0;
            return offCanvas;
          } else if (filterName === "VINTAGE") {
            let cx = rw >> 1, cy = rh >> 1;
            let maxD = Math.hypot(cx, cy) + 1e-6;
            for (let y = 0; y < rh; y++) {
              let row = (y * rw) << 2;
              for (let x = 0; x < rw; x++) {
                let idx = row + (x << 2);
                let r = d[idx], g = d[idx+1], b = d[idx+2];
                let dist = Math.hypot(x - cx, y - cy);
                let vig = Math.max(0, 1 - Math.pow(dist / maxD, 1.5));
                d[idx]   = Math.min(255, (0.393*r + 0.769*g + 0.189*b) * vig);
                d[idx+1] = Math.min(255, (0.349*r + 0.686*g + 0.168*b) * vig);
                d[idx+2] = Math.min(255, (0.272*r + 0.534*g + 0.131*b) * vig);
              }
            }
          } else if (filterName === "CARTOON") {
            for (let i = 0; i < len; i += 4) {
              d[i]   = (d[i] >> 6) * 64 + 32;
              d[i+1] = (d[i+1] >> 6) * 64 + 32;
              d[i+2] = (d[i+2] >> 6) * 64 + 32;
            }
          } else if (filterName === "EMBOSS") {
            let copy = new Uint8ClampedArray(d);
            for (let y = 1; y < rh - 1; y++) {
              let row = (y * rw) << 2;
              let pRow = ((y - 1) * rw) << 2;
              let nRow = ((y + 1) * rw) << 2;
              for (let x = 1; x < rw - 1; x++) {
                let idx = row + (x << 2);
                let pTL = pRow + ((x - 1) << 2);
                let pBR = nRow + ((x + 1) << 2);
                let gTL = (copy[pTL] + copy[pTL+1] + copy[pTL+2]) / 3;
                let gBR = (copy[pBR] + copy[pBR+1] + copy[pBR+2]) / 3;
                let val = Math.min(255, Math.max(0, (gBR - gTL) * 1.5 + 128));
                d[idx] = d[idx+1] = d[idx+2] = val;
              }
            }
          } else if (filterName === "NIGHT") {
            for (let i = 0; i < len; i += 4) {
              let g = (d[i] + d[i+1] + d[i+2]) / 3;
              d[i] = 0; d[i+1] = Math.min(255, g * 1.8 + 20); d[i+2] = 0;
            }
          } else if (filterName === "OCEAN") {
            for (let i = 0; i < len; i += 4) {
              d[i]   = (d[i] * 0.35) | 0;
              d[i+1] = (d[i+1] * 0.85) | 0;
              d[i+2] = Math.min(255, (d[i+2] * 1.45) | 0);
            }
          } else if (filterName === "FIRE") {
            for (let i = 0; i < len; i += 4) {
              let g = (d[i] + d[i+1] + d[i+2]) / 3;
              d[i]   = Math.min(255, g * 3);
              d[i+1] = Math.min(255, Math.max(0, (g - 85) * 3));
              d[i+2] = Math.min(255, Math.max(0, (g - 170) * 3));
            }
          } else if (filterName === "RAINBOW") {
            for (let y = 0; y < rh; y++) {
              let row = (y * rw) << 2;
              for (let x = 0; x < rw; x++) {
                let idx = row + (x << 2);
                let g = (d[idx] + d[idx+1] + d[idx+2]) / 3;
                let angle = (x / rw) * 6.28;
                d[idx]   = Math.min(255, g * 0.5 + Math.sin(angle) * 120 + 120);
                d[idx+1] = Math.min(255, g * 0.5 + Math.sin(angle + 2.09) * 120 + 120);
                d[idx+2] = Math.min(255, g * 0.5 + Math.sin(angle + 4.18) * 120 + 120);
              }
            }
          } else if (filterName === "VIGNETTE") {
            let cx = rw >> 1, cy = rh >> 1;
            let maxD = Math.hypot(cx, cy) + 1e-6;
            for (let y = 0; y < rh; y++) {
              let row = (y * rw) << 2;
              for (let x = 0; x < rw; x++) {
                let idx = row + (x << 2);
                let dist = Math.hypot(x - cx, y - cy);
                let vig = Math.max(0, 1 - Math.pow(dist / maxD, 1.8));
                d[idx]   = (d[idx] * vig) | 0;
                d[idx+1] = (d[idx+1] * vig) | 0;
                d[idx+2] = (d[idx+2] * vig) | 0;
              }
            }
          } else if (filterName === "OIL") {
            for (let i = 0; i < len; i += 4) {
              d[i]   = ((d[i] / 40) | 0) * 40;
              d[i+1] = ((d[i+1] / 40) | 0) * 40;
              d[i+2] = ((d[i+2] / 40) | 0) * 40;
            }
          }

          offCtx.putImageData(imgData, 0, 0);
          return offCanvas;
        }

        function drawHUD(w, h, filterName, curIdx, fpsVal) {
          const accentRGB = FILTER_COLORS[filterName] || [0, 229, 160];
          const accentColor = rgbToHex(accentRGB);

          // Top bar
          ctx.fillStyle = 'rgba(5, 5, 12, 0.85)';
          ctx.fillRect(0, 0, w, 44);
          ctx.strokeStyle = accentColor;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(0, 44);
          ctx.lineTo(w, 44);
          ctx.stroke();

          drawTextWithShadow('RETROLENS', 18, 29, 'bold 18px Segoe UI', accentColor);

          let fpsColor = (fpsVal >= 24) ? '#00e5a0' : (fpsVal >= 15 ? '#f59e0b' : '#ef4444');
          drawTextWithShadow(`FPS ${Math.round(fpsVal)}`, w - 85, 29, 'bold 15px Segoe UI', fpsColor);

          // Bottom Filter Strip
          const barH = 46;
          const barTop = h - barH;
          ctx.fillStyle = 'rgba(5, 5, 12, 0.90)';
          ctx.fillRect(0, barTop, w, barH);
          ctx.strokeStyle = accentColor;
          ctx.beginPath();
          ctx.moveTo(0, barTop);
          ctx.lineTo(w, barTop);
          ctx.stroke();

          drawTextWithShadow(`${curIdx + 1}/${FILTERS.length}`, w - 55, barTop - 8, '12px Segoe UI', '#94a3b8');

          const visible = 9;
          const half = (visible / 2) | 0;
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
          isProcessing = false;
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

              let minX = Math.max(0, Math.min(...poly.map(p => p.x))) | 0;
              let maxX = Math.min(w, Math.max(...poly.map(p => p.x))) | 0;
              let minY = Math.max(0, Math.min(...poly.map(p => p.y))) | 0;
              let maxY = Math.min(h, Math.max(...poly.map(p => p.y))) | 0;
              let rw = maxX - minX;
              let rh = maxY - minY;

              if (rw > 20 && rh > 20) {
                let filteredCanvas = applyFilterFast(filterName, minX, minY, rw, rh);

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

                for (let i = 0; i < 4; i++) {
                  let p1 = poly[i], p2 = poly[(i+1)%4];
                  for (let j = 0; j < 3; j++) {
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

        async function startApp() {
          if (cameraRunning) return;
          tapOverlay.style.opacity = '0';
          setTimeout(() => { tapOverlay.style.display = 'none'; }, 300);

          const handsObj = new Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
          });

          // Lite model = 60 FPS in browser!
          handsObj.setOptions({
            maxNumHands: 2,
            modelComplexity: 0,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
          });

          handsObj.onResults(onResults);

          const cameraObj = new Camera(video, {
            onFrame: async () => {
              if (!isProcessing) {
                isProcessing = true;
                await handsObj.send({ image: video });
              }
            },
            width: 640,
            height: 360
          });

          await cameraObj.start();
          cameraRunning = true;
        }

        tapOverlay.addEventListener('click', startApp);
        document.body.addEventListener('click', startApp);
        window.addEventListener('load', () => {
          // Coba autoplay
          startApp().catch(() => {
            tapOverlay.style.display = 'flex';
            tapOverlay.style.opacity = '1';
          });
        });
      </script>
    </body>
    </html>
    """

    components.html(html_code, height=620, scrolling=False)


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
