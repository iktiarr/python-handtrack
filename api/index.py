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
  <meta name="description" content="RETROLENS — Real-time hand tracking camera filter app with 36 cinematic filters."/>
  <title>RETROLENS — Hand Tracking Camera Filter</title>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.4.1675466862/camera_utils.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/hands.js"></script>
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
      display: block;
      cursor: pointer;
    }

    /* ── Floating Trigger Buttons ────────────── */
    .floating-btn {
      position: absolute;
      z-index: 60;
      background: rgba(10, 10, 26, 0.85);
      backdrop-filter: blur(24px) saturate(190%);
      -webkit-backdrop-filter: blur(24px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.12);
      color: #fff;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
      -webkit-user-select: none;
    }
    .floating-btn:hover {
      border-color: rgba(255, 255, 255, 0.32);
      background: rgba(18, 18, 40, 0.94);
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.65);
      transform: scale(1.05);
    }
    .floating-btn:active {
      transform: scale(0.96);
    }

    /* Guide ? button — bottom-left */
    #guide-toggle-btn {
      bottom: 24px; left: 24px;
      width: 44px; height: 44px;
      border-radius: 50%;
      display: none;
      align-items: center; justify-content: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 19px;
      font-weight: 700;
    }
    #guide-toggle-btn.active {
      background: rgba(0, 229, 160, 0.2);
      border-color: #00e5a0;
      color: #00e5a0;
      box-shadow: 0 0 16px rgba(0, 229, 160, 0.35);
    }

    /* Filter pill button — right side */
    #filter-toggle-btn {
      top: 50%; right: 24px;
      transform: translateY(-50%);
      height: 42px;
      padding: 0 15px;
      border-radius: 100px;
      display: none;
      align-items: center;
      gap: 9px;
    }
    #filter-toggle-btn:hover {
      transform: translateY(-50%) scale(1.05);
    }
    #filter-toggle-btn.active {
      background: rgba(0, 229, 160, 0.18);
      border-color: #00e5a0;
      box-shadow: 0 0 16px rgba(0, 229, 160, 0.35);
    }
    .ftb-dot {
      width: 9px; height: 9px;
      border-radius: 50%;
      background: #00e5a0;
      box-shadow: 0 0 8px currentColor;
      flex-shrink: 0;
      transition: background 0.3s, box-shadow 0.3s;
    }
    .ftb-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.5px;
      color: #fff;
      max-width: 105px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .ftb-icon {
      font-size: 14px;
      opacity: 0.85;
    }

    /* ── Close button for dock and modal ──────── */
    .panel-close-btn {
      width: 24px; height: 24px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: rgba(255, 255, 255, 0.65);
      display: flex;
      align-items: center; justify-content: center;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .panel-close-btn:hover {
      background: rgba(255, 255, 255, 0.2);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.3);
    }

    /* ── Filter Dock — RIGHT SIDE (COLLAPSIBLE, DEFAULT HIDDEN) ───── */
    #filter-dock {
      position: absolute;
      top: 50%; right: 24px;
      z-index: 70;
      display: none;
      flex-direction: column;
      width: 252px;
      background: rgba(8, 8, 24, 0.92);
      backdrop-filter: blur(24px) saturate(190%);
      -webkit-backdrop-filter: blur(24px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 20px;
      padding: 16px;
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.12);
      pointer-events: auto;
      user-select: none;
      opacity: 0;
      transform: translateY(-50%) scale(0.95);
      transition: opacity 0.22s ease, transform 0.22s ease;
    }
    #filter-dock.open {
      display: flex;
      opacity: 1;
      transform: translateY(-50%) scale(1);
    }

    .fd-card {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .fd-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .fd-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 2px;
      color: rgba(255,255,255,0.4);
      text-transform: uppercase;
    }

    .fd-counter {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: rgba(255,255,255,0.45);
      letter-spacing: 1px;
    }

    .fd-main-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 2px 0;
    }

    .fd-dot {
      width: 10px; height: 10px;
      border-radius: 50%;
      background: #00e5a0;
      box-shadow: 0 0 10px currentColor;
      flex-shrink: 0;
      transition: background 0.3s, box-shadow 0.3s;
    }

    .fd-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 1px;
      color: #fff;
      text-shadow: 0 0 18px currentColor;
      transition: color 0.3s ease, text-shadow 0.3s ease;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }

    .fd-arrows {
      display: flex;
      gap: 4px;
      flex-shrink: 0;
    }

    .fd-arrow-btn {
      width: 26px; height: 26px;
      border-radius: 7px;
      border: 1px solid rgba(255,255,255,0.12);
      background: rgba(255,255,255,0.06);
      color: rgba(255,255,255,0.75);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .fd-arrow-btn:hover {
      background: rgba(255,255,255,0.18);
      color: #fff;
      border-color: rgba(255,255,255,0.3);
    }

    .fd-divider {
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
      margin: 4px 0 2px;
    }

    .fd-fullscreen-toggle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 9px 11px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .fd-fullscreen-toggle:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.16);
    }
    .fd-fullscreen-toggle.active {
      background: rgba(0, 229, 160, 0.12);
      border-color: rgba(0, 229, 160, 0.4);
    }

    .toggle-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .toggle-title {
      font-size: 11.5px;
      font-weight: 600;
      color: #fff;
      letter-spacing: 0.3px;
    }

    .toggle-sub {
      font-family: 'JetBrains Mono', monospace;
      font-size: 9.5px;
      color: rgba(255, 255, 255, 0.45);
      letter-spacing: 0.5px;
      transition: color 0.2s;
    }
    .fd-fullscreen-toggle.active .toggle-sub {
      color: #00e5a0;
      font-weight: 600;
    }

    .toggle-switch {
      position: relative;
      width: 38px;
      height: 20px;
      background: rgba(255, 255, 255, 0.18);
      border-radius: 20px;
      transition: background 0.25s ease, box-shadow 0.25s ease;
      flex-shrink: 0;
    }
    .fd-fullscreen-toggle.active .toggle-switch {
      background: #00e5a0;
      box-shadow: 0 0 10px rgba(0, 229, 160, 0.5);
    }

    .switch-handle {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 16px;
      height: 16px;
      background: #fff;
      border-radius: 50%;
      transition: transform 0.25s ease;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .fd-fullscreen-toggle.active .switch-handle {
      transform: translateX(18px);
    }

    /* ── Gesture Guide Modal (POPUP, DEFAULT HIDDEN) ──────────── */
    #gesture-modal {
      position: absolute;
      bottom: 80px; left: 24px;
      z-index: 70;
      display: none;
      flex-direction: column;
      gap: 10px;
      width: 325px;
      background: rgba(8, 8, 24, 0.94);
      backdrop-filter: blur(24px) saturate(190%);
      -webkit-backdrop-filter: blur(24px) saturate(190%);
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 20px;
      padding: 14px 16px;
      box-shadow: 0 20px 48px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.12);
      pointer-events: auto;
      user-select: none;
      opacity: 0;
      transform: translateY(12px) scale(0.96);
      transition: opacity 0.22s ease, transform 0.22s ease;
    }
    #gesture-modal.open {
      display: flex;
      opacity: 1;
      transform: translateY(0) scale(1);
    }

    .gg-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 2px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .gg-header-left {
      display: flex;
      align-items: center;
      gap: 7px;
    }
    .gg-header-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .gg-icon-title {
      font-size: 15px;
    }
    .gg-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1.5px;
      color: rgba(255,255,255,0.75);
      text-transform: uppercase;
    }
    .gg-status-pill {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 2px 8px;
      border-radius: 20px;
      background: rgba(0, 229, 160, 0.12);
      border: 1px solid rgba(0, 229, 160, 0.3);
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      font-weight: 600;
      color: #00e5a0;
      letter-spacing: 0.5px;
    }
    .gg-pulse-dot {
      width: 5px; height: 5px;
      border-radius: 50%;
      background: #00e5a0;
      box-shadow: 0 0 6px #00e5a0;
      animation: blink 1.6s ease-in-out infinite;
    }

    .gg-body {
      display: flex;
      flex-direction: column;
      gap: 7px;
    }

    .gg-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 7px 9px;
      border-radius: 11px;
      background: rgba(255, 255, 255, 0.035);
      border: 1px solid rgba(255, 255, 255, 0.06);
      transition: all 0.22s ease;
    }
    .gg-item.highlight {
      background: rgba(0, 229, 160, 0.18) !important;
      border-color: rgba(0, 229, 160, 0.5) !important;
      box-shadow: 0 0 16px rgba(0, 229, 160, 0.25);
      transform: scale(1.02);
    }

    .gg-badge {
      width: 28px;
      height: 28px;
      border-radius: 9px;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.12);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .gg-text {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .gg-action {
      font-size: 11.5px;
      font-weight: 700;
      color: #fff;
      line-height: 1.3;
      letter-spacing: 0.2px;
    }

    .gg-desc {
      font-size: 10px;
      color: rgba(255,255,255,0.58);
      line-height: 1.45;
    }
    .gg-desc b {
      color: #fff;
      font-weight: 600;
    }

    .gg-tag-warn {
      color: #fbbf24;
      font-weight: 600;
    }
    .gg-tag-alert {
      color: #f87171;
      font-weight: 600;
    }
    .gg-tag-green {
      color: #34d399;
      font-weight: 600;
    }
    .gg-tag-blue {
      color: #60a5fa;
      font-weight: 600;
    }

    /* ── Mobile Responsive Layout ─────────────── */
    @media (max-width: 680px) {
      #guide-toggle-btn {
        bottom: 18px; left: 16px;
        width: 44px; height: 44px;
      }

      #filter-toggle-btn {
        top: auto; bottom: 18px; right: 16px;
        transform: none;
        height: 44px;
        padding: 0 14px;
      }
      #filter-toggle-btn:hover {
        transform: scale(1.04);
      }

      #gesture-modal {
        bottom: 74px; left: 16px;
        width: calc(100vw - 32px);
        max-width: 360px;
        max-height: 72vh;
        overflow-y: auto;
        padding: 14px;
      }

      #filter-dock {
        top: auto; bottom: 74px; right: 16px;
        transform: scale(0.96);
        width: calc(100vw - 32px);
        max-width: 320px;
        padding: 14px;
      }
      #filter-dock.open {
        transform: scale(1);
      }
      .fd-name { font-size: 16px; }
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

  <!-- Floating Trigger Buttons -->
  <button id="guide-toggle-btn" class="floating-btn" title="Panduan Kontrol Gestur (?)">?</button>

  <button id="filter-toggle-btn" class="floating-btn" title="Buka Pengaturan Filter (🎨)">
    <span class="ftb-dot" id="filter-btn-dot"></span>
    <span class="ftb-name" id="filter-btn-name">NORMAL</span>
    <span class="ftb-icon">🎨</span>
  </button>

  <!-- Gesture Guide Modal (Default: Hidden, opened via ?) -->
  <aside id="gesture-modal">
    <div class="gg-header">
      <div class="gg-header-left">
        <span class="gg-icon-title">💡</span>
        <span class="gg-title">PANDUAN GESTUR</span>
      </div>
      <div class="gg-header-right">
        <div class="gg-status-pill">
          <span class="gg-pulse-dot"></span>
          <span>AI TRACKER</span>
        </div>
        <button id="close-guide-btn" class="panel-close-btn" title="Tutup Panduan (✕)">✕</button>
      </div>
    </div>
    
    <div class="gg-body">
      <!-- Gestur 1: Ganti Filter -->
      <div class="gg-item" id="gi-thumb-pinky">
        <div class="gg-badge">🤙</div>
        <div class="gg-text">
          <div class="gg-action">Ganti Filter: Jempol & Kelingking</div>
          <div class="gg-desc">
            Dekatkan ujung jempol ke kelingking di satu tangan.<br>
            <span class="gg-tag-warn">🟡 Kuning:</span> Mendekat (Siap)<br>
            <span class="gg-tag-alert">🔴 Merah:</span> Menyentuh = <b>Filter Berganti!</b>
          </div>
        </div>
      </div>

      <!-- Mode Display -->
      <div class="gg-item" id="gi-mode-info">
        <div class="gg-badge" id="gg-mode-icon">🖐️</div>
        <div class="gg-text">
          <div class="gg-action" id="gg-mode-title">Mode: Portal Tangan (Bawaan)</div>
          <div class="gg-desc" id="gg-mode-desc">
            Filter hanya aktif di area jari/tangan.<br>
            Aktifkan <b>"Terapkan Satu Layar"</b> di panel filter agar efek filter mengisi seluruh layar!
          </div>
        </div>
      </div>

      <!-- Gestur 2 -->
      <div class="gg-item" id="gi-two-hands">
        <div class="gg-badge">🤝</div>
        <div class="gg-text">
          <div class="gg-action">2 Ujung Telunjuk Bertemu</div>
          <div class="gg-desc">Dekatkan telunjuk kiri & kanan sebagai alternatif ganti filter</div>
        </div>
      </div>

      <!-- Manual -->
      <div class="gg-item">
        <div class="gg-badge">⚡</div>
        <div class="gg-text">
          <div class="gg-action">Kontrol Cepat (Klik / Spasi / ▲ ▼)</div>
          <div class="gg-desc">Klik layar, tombol ▲ ▼ di panel filter, atau tombol Spasi</div>
        </div>
      </div>
    </div>
  </aside>

  <!-- Filter Dock (Default: Hidden, opened via 🎨) -->
  <aside id="filter-dock">
    <div class="fd-card">
      <div class="fd-top">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="fd-label">FILTER AKTIF</span>
          <span class="fd-counter" id="filter-counter">01 / 36</span>
        </div>
        <button id="close-filter-btn" class="panel-close-btn" title="Tutup Panel Filter (✕)">✕</button>
      </div>

      <div class="fd-main-row">
        <span class="fd-dot" id="filter-dot"></span>
        <div class="fd-name" id="filter-name">NORMAL</div>
        <div class="fd-arrows">
          <button id="prev-filter-btn" class="fd-arrow-btn" title="Filter Sebelumnya (▲ / ←)">▲</button>
          <button id="next-filter-btn" class="fd-arrow-btn" title="Filter Berikutnya (▼ / →)">▼</button>
        </div>
      </div>

      <!-- Opsi Terapkan Satu Layar -->
      <div class="fd-divider"></div>

      <div class="fd-fullscreen-toggle" id="fullscreen-toggle" role="button" tabindex="0" title="Klik untuk mengaktifkan / menonaktifkan filter satu layar penuh">
        <div class="toggle-info">
          <span class="toggle-title">Terapkan Satu Layar</span>
          <span class="toggle-sub" id="toggle-sub">Mode: Portal Tangan</span>
        </div>
        <div class="toggle-switch" id="toggle-switch">
          <div class="switch-handle"></div>
        </div>
      </div>
    </div>
  </aside>

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
  { name: "NORMAL",      color: [200, 200, 200] },
  { name: "MONO",        color: [180, 180, 180] },
  { name: "SEPIA",       color: [225, 145,  60] },
  { name: "VINTAGE",     color: [215, 160,  85] },
  { name: "INVERT",      color: [255,  80, 220] },
  { name: "THERMAL",     color: [255,  85,   0] },
  { name: "NEON",        color: [  0, 255, 255] },
  { name: "NIGHT",       color: [  0, 240,  90] },
  { name: "OCEAN",       color: [ 10, 160, 245] },
  { name: "FIRE",        color: [255,  95,   0] },
  { name: "RAINBOW",     color: [170, 255,   0] },
  { name: "GALAXY",      color: [195,  85, 255] },
  { name: "SKETCH",      color: [230, 230, 230] },
  { name: "EMBOSS",      color: [210, 210, 210] },
  { name: "CARTOON",     color: [  0, 225, 255] },
  { name: "GLITCH",      color: [255,  45,  75] },
  { name: "PIXELATE",    color: [  0, 190, 255] },
  { name: "BLUR",        color: [180, 180, 255] },
  { name: "DUAL-TONE",   color: [255,  25, 175] },
  { name: "OIL",         color: [ 60, 220, 130] },
  { name: "VIGNETTE",    color: [170, 125, 125] },
  { name: "MIRROR",      color: [200, 235, 255] },
  { name: "CYBERPUNK",   color: [255,  20, 140] },
  { name: "MATRIX",      color: [  0, 255,  80] },
  { name: "LOMO",        color: [255, 155,  50] },
  { name: "ICE",         color: [130, 225, 255] },
  // ── 10 NEW FILTERS ──
  { name: "ANIME",       color: [255, 140, 180] },
  { name: "VAPORWAVE",   color: [255, 110, 220] },
  { name: "CINEMATIC",   color: [ 20, 215, 205] },
  { name: "GOLDEN HOUR", color: [255, 185,  40] },
  { name: "RETRO CRT",   color: [140, 255, 100] },
  { name: "SOLARIZE",    color: [255,  80, 100] },
  { name: "PASTEL GLOW", color: [255, 180, 210] },
  { name: "AEROCHROME",  color: [255,  50, 120] },
  { name: "AMBER NOIR",  color: [235, 150,  30] },
  { name: "AURA",        color: [180, 120, 255] },
];

// Precompute color curves for instant 60 FPS processing
const LUT = {
  thermalR: new Uint8Array(256),
  thermalG: new Uint8Array(256),
  thermalB: new Uint8Array(256),

  duoR: new Uint8Array(256),
  duoG: new Uint8Array(256),
  duoB: new Uint8Array(256),

  cineR: new Uint8Array(256),
  cineG: new Uint8Array(256),
  cineB: new Uint8Array(256),

  vaporR: new Uint8Array(256),
  vaporG: new Uint8Array(256),
  vaporB: new Uint8Array(256),

  solarR: new Uint8Array(256),
  solarG: new Uint8Array(256),
  solarB: new Uint8Array(256),

  amberR: new Uint8Array(256),
  amberG: new Uint8Array(256),
  amberB: new Uint8Array(256),
};

for (let i = 0; i < 256; i++) {
  const v = i / 255;

  // Thermal Ironbow
  LUT.thermalR[i] = Math.min(255, Math.max(0, 255 * (1.6 - Math.abs(3.8 * v - 2.8))));
  LUT.thermalG[i] = Math.min(255, Math.max(0, 255 * (1.6 - Math.abs(3.8 * v - 1.9))));
  LUT.thermalB[i] = Math.min(255, Math.max(0, 255 * (1.6 - Math.abs(3.8 * v - 0.9))));

  // Dual-tone (Electric Magenta to Golden Glow)
  const dv = v * v * (3 - 2 * v);
  LUT.duoR[i] = Math.min(255, (40 + (255 - 40) * dv) | 0);
  LUT.duoG[i] = Math.min(255, (10 + (185 - 10) * dv) | 0);
  LUT.duoB[i] = Math.min(255, (80 + (30 - 80) * dv) | 0);

  // Cinematic Teal & Orange
  LUT.cineR[i] = Math.min(255, (i < 128 ? i * 0.75 : i + (255 - i) * 0.45) | 0);
  LUT.cineG[i] = Math.min(255, (i < 128 ? i * 1.05 + 10 : i + (255 - i) * 0.1) | 0);
  LUT.cineB[i] = Math.min(255, (i < 128 ? i * 1.35 + 25 : i * 0.7) | 0);

  // Vaporwave (Violet / Pink / Pastel Cyan)
  LUT.vaporR[i] = Math.min(255, (45 + v * 210) | 0);
  LUT.vaporG[i] = Math.min(255, (15 + Math.sin(v * Math.PI) * 120 + v * 90) | 0);
  LUT.vaporB[i] = Math.min(255, (85 + Math.cos(v * Math.PI * 0.5) * 170) | 0);

  // Solarize
  const sol = Math.abs(2 * i - 255);
  LUT.solarR[i] = Math.min(255, (sol * 1.2) | 0);
  LUT.solarG[i] = Math.min(255, (sol * 0.9 + 20) | 0);
  LUT.solarB[i] = Math.min(255, (255 - sol * 0.6) | 0);

  // Amber Noir
  const sc = v < 0.5 ? 2 * v * v : 1 - 2 * (1 - v) * (1 - v);
  LUT.amberR[i] = Math.min(255, (sc * 255 * 1.05) | 0);
  LUT.amberG[i] = Math.min(255, (sc * 185) | 0);
  LUT.amberB[i] = Math.min(255, (sc * 55) | 0);
}

// ─────────────────────────────────────────────
// DOM REFS
// ─────────────────────────────────────────────
const video            = document.getElementById('webcam');
const canvas           = document.getElementById('output_canvas');
const ctx              = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
const loadingEl        = document.getElementById('loading');
const permPrompt       = document.getElementById('perm-prompt');
const retryBtn         = document.getElementById('retry-btn');

// Floating Trigger Buttons
const guideToggleBtn   = document.getElementById('guide-toggle-btn');
const filterToggleBtn  = document.getElementById('filter-toggle-btn');
const filterBtnDot     = document.getElementById('filter-btn-dot');
const filterBtnName    = document.getElementById('filter-btn-name');

// Guide Modal & Filter Dock
const gestureModal     = document.getElementById('gesture-modal');
const closeGuideBtn    = document.getElementById('close-guide-btn');
const filterDock       = document.getElementById('filter-dock');
const closeFilterBtn   = document.getElementById('close-filter-btn');

// Filter Controls
const filterName       = document.getElementById('filter-name');
const filterDot        = document.getElementById('filter-dot');
const filterCount      = document.getElementById('filter-counter');
const prevFilterBtn    = document.getElementById('prev-filter-btn');
const nextFilterBtn    = document.getElementById('next-filter-btn');
const fullscreenToggle = document.getElementById('fullscreen-toggle');
const toggleSub        = document.getElementById('toggle-sub');
const errToast         = document.getElementById('err-toast');
const ppTitle          = permPrompt ? permPrompt.querySelector('.pp-title') : null;
const ppSub            = permPrompt ? permPrompt.querySelector('.pp-sub') : null;
const ppIcon           = permPrompt ? permPrompt.querySelector('.pp-icon') : null;

// Offscreen canvases
const offC  = document.createElement('canvas');
const offX  = offC.getContext('2d', { willReadFrequently: true });
const miniC = document.createElement('canvas');
const miniX = miniC.getContext('2d', { willReadFrequently: true });

// ─────────────────────────────────────────────
// HAND CONNECTIONS FOR SKELETON TRACKER
// ─────────────────────────────────────────────
const HAND_CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,4],        // Thumb
  [0,5],[5,6],[6,7],[7,8],        // Index
  [5,9],[9,10],[10,11],[11,12],   // Middle
  [9,13],[13,14],[14,15],[15,16], // Ring
  [13,17],[0,17],[17,18],[18,19],[19,20] // Pinky
];

// ─────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────
let curFilter        = 0;
let filterMode       = 'PORTAL'; // 'PORTAL' or 'FULL'
let gestureTriggered = false;
let camRunning       = false;
let processing       = false;
let lastAccent       = '#00e5a0';
let animFrame        = 0;
let handsInstance    = null;
let handsReady       = false;
let stream           = null;
let animId           = null;
let lastSendTime     = 0;
let smoothPoly       = null;

// ─────────────────────────────────────────────
// UI TOGGLE HELPERS
// ─────────────────────────────────────────────
function toggleFilterDock(show) {
  const willOpen = (show !== undefined) ? show : !filterDock.classList.contains('open');
  if (willOpen) {
    filterDock.classList.add('open');
    if (filterToggleBtn) filterToggleBtn.classList.add('active');
  } else {
    filterDock.classList.remove('open');
    if (filterToggleBtn) filterToggleBtn.classList.remove('active');
  }
}

function toggleGuideModal(show) {
  const willOpen = (show !== undefined) ? show : !gestureModal.classList.contains('open');
  if (willOpen) {
    gestureModal.classList.add('open');
    if (guideToggleBtn) guideToggleBtn.classList.add('active');
  } else {
    gestureModal.classList.remove('open');
    if (guideToggleBtn) guideToggleBtn.classList.remove('active');
  }
}

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

let errTimer = null;
function showError(msg, duration = 4500) {
  errToast.textContent = msg;
  errToast.style.display = 'block';
  clearTimeout(errTimer);
  errTimer = setTimeout(() => { errToast.style.display = 'none'; }, duration);
}

function showPrompt(title, sub, icon = '&#128247;') {
  if (ppTitle) ppTitle.textContent = title;
  if (ppSub) ppSub.innerHTML = sub;
  if (ppIcon) ppIcon.innerHTML = icon;
  loadingEl.style.display  = 'none';
  permPrompt.style.display = 'flex';
}

// ─────────────────────────────────────────────
// APPLY FILTER TO REGION
// Returns an ImageData or OffscreenCanvas to blit
// ─────────────────────────────────────────────
function applyFilter(name, sx, sy, sw, sh) {
  if (sw < 2 || sh < 2) return null;

  offC.width  = sw;
  offC.height = sh;

  // 1. Instant CSS hardware-accelerated filters
  const cssMap = {
    'MONO':      'grayscale(100%) contrast(120%) brightness(1.02)',
    'SEPIA':     'sepia(100%) saturate(140%) brightness(1.05) contrast(105%)',
    'INVERT':    'invert(100%) hue-rotate(180deg)',
    'BLUR':      'blur(12px)',
    'MIRROR':    null,
    'PIXELATE':  null,
  };

  if (name === 'MIRROR') {
    offX.save();
    offX.translate(sw, 0); offX.scale(-1, 1);
    offX.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);
    offX.restore();
    return offC;
  }

  if (name === 'PIXELATE') {
    const pw = Math.max(2, (sw / 14) | 0), ph = Math.max(2, (sh / 14) | 0);
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

  // 2. Pixel shaders and LUT filters
  offX.drawImage(canvas, sx, sy, sw, sh, 0, 0, sw, sh);
  const imgData = offX.getImageData(0, 0, sw, sh);
  const d = imgData.data;
  const len = d.length;
  const t = Date.now() * 0.001;

  if (name === 'NORMAL') {
    return offC;
  }

  // ── THERMAL (Smooth FLIR Ironbow Heatmap) ──
  else if (name === 'THERMAL') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      d[i]   = LUT.thermalR[lum];
      d[i+1] = LUT.thermalG[lum];
      d[i+2] = LUT.thermalB[lum];
    }
  }

  // ── DUAL-TONE (Synthwave Magenta & Gold) ──
  else if (name === 'DUAL-TONE') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      d[i]   = LUT.duoR[lum];
      d[i+1] = LUT.duoG[lum];
      d[i+2] = LUT.duoB[lum];
    }
  }

  // ── CINEMATIC (Hollywood Teal & Orange) ──
  else if (name === 'CINEMATIC') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = LUT.cineR[d[i]];
      d[i+1] = LUT.cineG[d[i+1]];
      d[i+2] = LUT.cineB[d[i+2]];
    }
  }

  // ── VAPORWAVE (80s Aesthetic Lilac & Cyan) ──
  else if (name === 'VAPORWAVE') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      const row = (i >> 2) / sw | 0;
      const scan = (row % 3 === 0) ? 0.88 : 1.0;
      d[i]   = (LUT.vaporR[lum] * scan) | 0;
      d[i+1] = (LUT.vaporG[lum] * scan) | 0;
      d[i+2] = (LUT.vaporB[lum] * scan) | 0;
    }
  }

  // ── SOLARIZE (Sabattier Metallic Halo) ──
  else if (name === 'SOLARIZE') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = LUT.solarR[d[i]];
      d[i+1] = LUT.solarG[d[i+1]];
      d[i+2] = LUT.solarB[d[i+2]];
    }
  }

  // ── AMBER NOIR (Classic Tungsten Film Noir) ──
  else if (name === 'AMBER NOIR') {
    const cx = sw >> 1, cy = sh >> 1;
    const maxD = Math.hypot(cx, cy) + 1e-5;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      const vig = Math.max(0.1, 1 - Math.pow(Math.hypot(x - cx, y - cy) / maxD, 1.8));
      d[i]   = (LUT.amberR[lum] * vig) | 0;
      d[i+1] = (LUT.amberG[lum] * vig) | 0;
      d[i+2] = (LUT.amberB[lum] * vig) | 0;
    }
  }

  // ── CARTOON (Anime Cel-Shading + Ink Contours) ──
  else if (name === 'CARTOON') {
    const copy = new Uint8ClampedArray(d);
    for (let y = 0; y < sh - 1; y++) {
      const row = y * sw * 4, nr = (y + 1) * sw * 4;
      for (let x = 0; x < sw - 1; x++) {
        const i = row + x * 4, r = row + (x + 1) * 4, dn = nr + x * 4;
        const lum  = (copy[i]  * 77 + copy[i+1]  * 150 + copy[i+2]  * 29) >> 8;
        const lumR = (copy[r]  * 77 + copy[r+1]  * 150 + copy[r+2]  * 29) >> 8;
        const lumD = (copy[dn] * 77 + copy[dn+1] * 150 + copy[dn+2] * 29) >> 8;
        const edge = Math.abs(lum - lumR) + Math.abs(lum - lumD);

        if (edge > 32) {
          d[i] = 18; d[i+1] = 18; d[i+2] = 24;
        } else {
          const cel = lum < 65 ? 45 : lum < 130 ? 105 : lum < 195 ? 175 : 240;
          const factor = (cel / (lum + 1e-4));
          d[i]   = Math.min(255, (copy[i]   * factor * 1.15) | 0);
          d[i+1] = Math.min(255, (copy[i+1] * factor * 1.15) | 0);
          d[i+2] = Math.min(255, (copy[i+2] * factor * 1.15) | 0);
        }
      }
    }
  }

  // ── ANIME (Studio Ghibli Warm Palette) ──
  else if (name === 'ANIME') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = Math.min(255, (d[i]   * 1.18 + 15) | 0);
      d[i+1] = Math.min(255, (d[i+1] * 1.12 + 10) | 0);
      d[i+2] = Math.min(255, (d[i+2] * 0.95 + 25) | 0);
    }
    offX.putImageData(imgData, 0, 0);
    offX.globalCompositeOperation = 'soft-light';
    offX.fillStyle = 'rgba(255, 220, 160, 0.25)';
    offX.fillRect(0, 0, sw, sh);
    offX.globalCompositeOperation = 'source-over';
    return offC;
  }

  // ── SKETCH (Pencil Sketch on Warm Parchment) ──
  else if (name === 'SKETCH') {
    const copy = new Uint8ClampedArray(d);
    for (let y = 0; y < sh - 1; y++) {
      const row = y * sw * 4, nr = (y + 1) * sw * 4;
      for (let x = 0; x < sw - 1; x++) {
        const i = row + x * 4, r = row + (x + 1) * 4, dn = nr + x * 4;
        const g1 = (copy[i]  * 77 + copy[i+1]  * 150 + copy[i+2]  * 29) >> 8;
        const gR = (copy[r]  * 77 + copy[r+1]  * 150 + copy[r+2]  * 29) >> 8;
        const gD = (copy[dn] * 77 + copy[dn+1] * 150 + copy[dn+2] * 29) >> 8;
        const diff = Math.hypot(gR - g1, gD - g1);
        const val = Math.max(0, Math.min(255, 255 - diff * 4.2));
        d[i]   = (val * 0.97) | 0;
        d[i+1] = (val * 0.94) | 0;
        d[i+2] = (val * 0.88) | 0;
      }
    }
  }

  // ── NEON (Cyber Laser Outline) ──
  else if (name === 'NEON') {
    const copy = new Uint8ClampedArray(d);
    for (let y = 0; y < sh - 1; y++) {
      const row = y * sw * 4, nr = (y + 1) * sw * 4;
      for (let x = 0; x < sw - 1; x++) {
        const i = row + x * 4, r = row + (x + 1) * 4, dn = nr + x * 4;
        const lum  = (copy[i]  * 77 + copy[i+1]  * 150 + copy[i+2]  * 29) >> 8;
        const lumR = (copy[r]  * 77 + copy[r+1]  * 150 + copy[r+2]  * 29) >> 8;
        const lumD = (copy[dn] * 77 + copy[dn+1] * 150 + copy[dn+2] * 29) >> 8;
        const edge = Math.min(255, Math.hypot(lumR - lum, lumD - lum) * 4.5);

        const huePhase = (x / sw + t * 0.3) % 1;
        const nr2 = (huePhase * 255) | 0;
        d[i]   = (edge > 25) ? Math.min(255, (edge * (nr2 / 255))) | 0 : (copy[i] * 0.08) | 0;
        d[i+1] = (edge > 25) ? Math.min(255, (edge * (1 - nr2 / 255))) | 0 : (copy[i+1] * 0.08) | 0;
        d[i+2] = (edge > 25) ? Math.min(255, edge) : (copy[i+2] * 0.12) | 0;
      }
    }
  }

  // ── GLITCH (RGB Chromatic Split & Drift) ──
  else if (name === 'GLITCH') {
    const shift = Math.max(4, (sw * 0.015) | 0);
    const copy  = new Uint8ClampedArray(d);
    for (let y = 0; y < sh; y++) {
      const row = y * sw * 4;
      const isGlitchRow = Math.sin(y * 0.25 + t * 9) > 0.45;
      const rowShift = isGlitchRow ? ((Math.sin(y + t * 15) * 12) | 0) : 0;
      for (let x = 0; x < sw; x++) {
        const i  = row + x * 4;
        const rx = Math.min(sw - 1, Math.max(0, x + shift + rowShift));
        const bx = Math.max(0, Math.min(sw - 1, x - shift - rowShift));
        d[i]   = copy[row + rx * 4];
        d[i+2] = copy[row + bx * 4 + 2];
      }
    }
  }

  // ── RETRO CRT (90s Tube TV + Phosphor Triad) ──
  else if (name === 'RETRO CRT') {
    for (let y = 0; y < sh; y++) {
      const row = y * sw * 4;
      const isScanline = (y % 3 === 0);
      const scanMult = isScanline ? 0.68 : 1.0;
      for (let x = 0; x < sw; x++) {
        const i = row + x * 4;
        const phosphor = x % 3;
        d[i]   = Math.min(255, (d[i]   * scanMult * (phosphor === 0 ? 1.25 : 0.88)) | 0);
        d[i+1] = Math.min(255, (d[i+1] * scanMult * (phosphor === 1 ? 1.25 : 0.88)) | 0);
        d[i+2] = Math.min(255, (d[i+2] * scanMult * (phosphor === 2 ? 1.25 : 0.88)) | 0);
      }
    }
  }

  // ── NIGHT (NVG Phosphor Green + Tube Vignette) ──
  else if (name === 'NIGHT') {
    const cx = sw >> 1, cy = sh >> 1;
    const maxD = Math.hypot(cx, cy) + 1e-5;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      const vig = Math.max(0, 1 - Math.pow(Math.hypot(x - cx, y - cy) / maxD, 1.6));
      const noise = (Math.random() - 0.5) * 16;
      d[i]   = Math.min(255, Math.max(0, (lum * 0.15 * vig) | 0));
      d[i+1] = Math.min(255, Math.max(0, (lum * 2.1 * vig + noise + 20) | 0));
      d[i+2] = Math.min(255, Math.max(0, (lum * 0.35 * vig) | 0));
    }
  }

  // ── GOLDEN HOUR (Radiant Warm Sunset Glow) ──
  else if (name === 'GOLDEN HOUR') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = Math.min(255, (d[i]   * 1.28 + 25) | 0);
      d[i+1] = Math.min(255, (d[i+1] * 1.10 + 12) | 0);
      d[i+2] = Math.min(255, (d[i+2] * 0.75) | 0);
    }
  }

  // ── PASTEL GLOW (Ethereal Bloom & Mist) ──
  else if (name === 'PASTEL GLOW') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = Math.min(255, (d[i]   * 1.1 + 30) | 0);
      d[i+1] = Math.min(255, (d[i+1] * 1.05 + 25) | 0);
      d[i+2] = Math.min(255, (d[i+2] * 1.2 + 40) | 0);
    }
  }

  // ── AEROCHROME (Kodak False-Color Crimson Infrared) ──
  else if (name === 'AEROCHROME') {
    for (let i = 0; i < len; i += 4) {
      const r = d[i], g = d[i+1], b = d[i+2];
      const isGreen = g > r * 0.85 && g > b * 0.9;
      if (isGreen) {
        d[i]   = Math.min(255, (g * 1.5 + 30) | 0);
        d[i+1] = Math.min(255, (r * 0.35 + 10) | 0);
        d[i+2] = Math.min(255, (g * 0.8 + 20) | 0);
      } else {
        d[i]   = Math.min(255, (r * 1.1) | 0);
        d[i+1] = Math.min(255, (g * 0.9) | 0);
        d[i+2] = Math.min(255, (b * 1.25) | 0);
      }
    }
  }

  // ── AURA (Rainbow Energy Wave) ──
  else if (name === 'AURA') {
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      const angle = (Math.hypot(x - sw/2, y - sh/2) / 60 - t * 3);
      d[i]   = Math.min(255, (lum * 0.6 + Math.sin(angle) * 110 + 110) | 0);
      d[i+1] = Math.min(255, (lum * 0.6 + Math.sin(angle + 2.09) * 110 + 110) | 0);
      d[i+2] = Math.min(255, (lum * 0.6 + Math.sin(angle + 4.18) * 110 + 110) | 0);
    }
  }

  // ── MATRIX (Digital Phosphor Code Rain) ──
  else if (name === 'MATRIX') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      d[i]   = 0;
      d[i+1] = Math.min(255, (lum * 2.1) | 0);
      d[i+2] = (lum * 0.2) | 0;
    }
    offX.putImageData(imgData, 0, 0);
    offX.font = '11px "JetBrains Mono", monospace';
    offX.fillStyle = 'rgba(0, 255, 120, 0.7)';
    const cols = Math.floor(sw / 16);
    for (let c = 0; c < cols; c++) {
      const cy = ((t * 80 + c * 47) % (sh + 40)) - 20;
      offX.fillText(String.fromCharCode(0x30A0 + (c * 17) % 96), c * 16, cy);
    }
    return offC;
  }

  // ── VINTAGE (Kodachrome 70s + Vignette) ──
  else if (name === 'VINTAGE') {
    const cx = sw >> 1, cy = sh >> 1;
    const maxD = Math.hypot(cx, cy) + 1e-5;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const r = d[i], g = d[i+1], b = d[i+2];
      const sr = Math.min(255, 0.393*r + 0.769*g + 0.189*b);
      const sg = Math.min(255, 0.349*r + 0.686*g + 0.168*b);
      const sb = Math.min(255, 0.272*r + 0.534*g + 0.131*b);
      const vig = Math.max(0.1, 1 - Math.pow(Math.hypot(x-cx, y-cy)/maxD, 1.6));
      d[i]   = (sr * vig) | 0;
      d[i+1] = (sg * vig) | 0;
      d[i+2] = (sb * vig) | 0;
    }
  }

  // ── OCEAN (Bioluminescent Deep Sea) ──
  else if (name === 'OCEAN') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = (d[i]   * 0.25) | 0;
      d[i+1] = Math.min(255, (d[i+1] * 0.95 + 15) | 0);
      d[i+2] = Math.min(255, (d[i+2] * 1.55 + 35) | 0);
    }
  }

  // ── FIRE (Volcanic Magma Flames) ──
  else if (name === 'FIRE') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      d[i]   = Math.min(255, (lum * 3.2) | 0);
      d[i+1] = Math.min(255, Math.max(0, (lum - 70) * 3));
      d[i+2] = Math.min(255, Math.max(0, (lum - 160) * 3));
    }
  }

  // ── RAINBOW (Animated Chromatic Wave) ──
  else if (name === 'RAINBOW') {
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw;
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      const angle = (x / sw + t * 0.25) * Math.PI * 2;
      d[i]   = Math.min(255, (lum * 0.4 + Math.sin(angle) * 115 + 115) | 0);
      d[i+1] = Math.min(255, (lum * 0.4 + Math.sin(angle + 2.094) * 115 + 115) | 0);
      d[i+2] = Math.min(255, (lum * 0.4 + Math.sin(angle + 4.189) * 115 + 115) | 0);
    }
  }

  // ── GALAXY (Nebula & Animated Starfield) ──
  else if (name === 'GALAXY') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = (d[i]   * 0.25 + 15) | 0;
      d[i+1] = (d[i+1] * 0.08 + 8) | 0;
      d[i+2] = Math.min(255, (d[i+2] * 0.65 + 35) | 0);
    }
    offX.putImageData(imgData, 0, 0);
    for (let s = 0; s < 75; s++) {
      const sx2 = ((Math.sin(s * 137.5 + t) * 0.5 + 0.5) * sw) | 0;
      const sy2 = ((Math.cos(s * 97.3  + t * 0.7) * 0.5 + 0.5) * sh) | 0;
      const alpha = (Math.sin(s + t * 2.5) * 0.5 + 0.5);
      offX.fillStyle = s % 3 === 0 ? `rgba(210,90,255,${alpha})` :
                       s % 3 === 1 ? `rgba(0,240,180,${alpha})` :
                                     `rgba(255,255,255,${alpha*0.6})`;
      offX.beginPath();
      offX.arc(sx2, sy2, (s % 2) + 0.9, 0, Math.PI*2);
      offX.fill();
    }
    return offC;
  }

  // ── EMBOSS (3D Metal Sculpt) ──
  else if (name === 'EMBOSS') {
    const copy = new Uint8ClampedArray(d);
    for (let y = 1; y < sh - 1; y++) {
      for (let x = 1; x < sw - 1; x++) {
        const i   = (y * sw + x) * 4;
        const tl  = ((y - 1) * sw + (x - 1)) * 4;
        const br  = ((y + 1) * sw + (x + 1)) * 4;
        const gTL = (copy[tl]   * 77 + copy[tl+1] * 150 + copy[tl+2] * 29) >> 8;
        const gBR = (copy[br]   * 77 + copy[br+1] * 150 + copy[br+2] * 29) >> 8;
        const val = Math.min(255, Math.max(0, (gBR - gTL) * 1.6 + 128));
        d[i] = d[i+1] = d[i+2] = val;
      }
    }
  }

  // ── OIL (Impressionist Paint Smear) ──
  else if (name === 'OIL') {
    for (let i = 0; i < len; i += 4) {
      d[i]   = Math.min(255, (((d[i]   / 28) | 0) * 28 + 10));
      d[i+1] = Math.min(255, (((d[i+1] / 28) | 0) * 28 + 10));
      d[i+2] = Math.min(255, (((d[i+2] / 28) | 0) * 28 + 10));
    }
  }

  // ── VIGNETTE (Cinematic Lens Focus) ──
  else if (name === 'VIGNETTE') {
    const cx = sw >> 1, cy = sh >> 1;
    const maxD = Math.hypot(cx, cy) + 1e-5;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const vig = Math.max(0.05, 1 - Math.pow(Math.hypot(x-cx, y-cy)/maxD, 1.8));
      d[i]   = (d[i]   * vig) | 0;
      d[i+1] = (d[i+1] * vig) | 0;
      d[i+2] = (d[i+2] * vig) | 0;
    }
  }

  // ── CYBERPUNK (Neo-Tokyo Magenta & Cyan) ──
  else if (name === 'CYBERPUNK') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      const t2  = lum / 255;
      d[i]   = Math.min(255, (lum * 0.5 + 255 * t2 * 0.85) | 0);
      d[i+1] = Math.min(255, (lum * 0.15 + 15) | 0);
      d[i+2] = Math.min(255, (lum * 0.5 + 255 * (1 - t2) * 0.75) | 0);
    }
  }

  // ── LOMO (Cross-Processed Saturated Contrast) ──
  else if (name === 'LOMO') {
    const cx = sw >> 1, cy = sh >> 1;
    const maxD = Math.hypot(cx, cy) + 1e-5;
    for (let i = 0; i < len; i += 4) {
      const idx = i >> 2;
      const x = idx % sw, y = (idx / sw) | 0;
      const vig = Math.max(0.08, 1 - Math.pow(Math.hypot(x-cx, y-cy)/maxD, 1.35));
      d[i]   = Math.min(255, (d[i]   * 1.25 * vig) | 0);
      d[i+1] = Math.min(255, (d[i+1] * 0.95 * vig) | 0);
      d[i+2] = Math.min(255, (d[i+2] * 0.75 * vig) | 0);
    }
  }

  // ── ICE (Arctic Crystalline Frost) ──
  else if (name === 'ICE') {
    for (let i = 0; i < len; i += 4) {
      const lum = (d[i] * 77 + d[i+1] * 150 + d[i+2] * 29) >> 8;
      d[i]   = Math.min(255, (lum * 0.65 + 35) | 0);
      d[i+1] = Math.min(255, (lum * 0.90 + 55) | 0);
      d[i+2] = Math.min(255, (lum * 1.35 + 85) | 0);
    }
  }

  offX.putImageData(imgData, 0, 0);
  return offC;
}

// ─────────────────────────────────────────────
// UPDATE FILTER BADGE UI
// ─────────────────────────────────────────────
function updateBadge(idx) {
  curFilter = idx;
  const f = FILTERS[idx];
  const ac = rgb(f.color);

  if (filterName) {
    filterName.textContent = f.name;
    filterName.style.color = ac;
    filterName.style.textShadow = `0 0 16px ${ac}`;
  }
  if (filterDot) {
    filterDot.style.background = ac;
    filterDot.style.boxShadow = `0 0 10px ${ac}`;
  }
  if (filterCount) {
    filterCount.textContent = `${String(idx+1).padStart(2,'0')} / ${FILTERS.length}`;
  }
  if (filterBtnName) {
    filterBtnName.textContent = f.name;
    filterBtnName.style.color = ac;
  }
  if (filterBtnDot) {
    filterBtnDot.style.background = ac;
    filterBtnDot.style.boxShadow = `0 0 8px ${ac}`;
  }
  lastAccent = ac;
}
updateBadge(0);

// ─────────────────────────────────────────────
// FILTER MODE TOGGLE (PORTAL / FULLSCREEN)
// ─────────────────────────────────────────────
function setFilterMode(mode) {
  filterMode = mode;
  const isFull = (filterMode === 'FULL');
  if (fullscreenToggle) {
    if (isFull) {
      fullscreenToggle.classList.add('active');
      if (toggleSub) toggleSub.textContent = 'Mode: Satu Layar (Aktif)';
    } else {
      fullscreenToggle.classList.remove('active');
      if (toggleSub) toggleSub.textContent = 'Mode: Portal Tangan';
    }
  }

  const modeIconEl  = document.getElementById('gg-mode-icon');
  const modeTitleEl = document.getElementById('gg-mode-title');
  const modeDescEl  = document.getElementById('gg-mode-desc');
  if (modeIconEl && modeTitleEl && modeDescEl) {
    if (isFull) {
      modeIconEl.textContent = '🖥️';
      modeTitleEl.textContent = 'Mode: Satu Layar (Aktif)';
      modeDescEl.innerHTML = 'Filter mengisi <b>seluruh layar</b>. Tracker aktif di tangan. Sentuh kelingking & jempol untuk berganti!';
    } else {
      modeIconEl.textContent = '🖐️';
      modeTitleEl.textContent = 'Mode: Portal Tangan (Bawaan)';
      modeDescEl.innerHTML = 'Filter hanya aktif di area jari/tangan. Aktifkan <b>"Terapkan Satu Layar"</b> di panel kanan.';
    }
  }
}

// ─────────────────────────────────────────────
// MEDIAPIPE RESULT HANDLER
// ─────────────────────────────────────────────
function onResults(results) {
  processing = false;
  animFrame++;

  const W = canvas.width, H = canvas.height;
  const vw = video.videoWidth || 1280;
  const vh = video.videoHeight || 720;

  // Kamera full screen tanpa pembungkus/border (edge-to-edge full bleed)
  const scale = Math.max(W / vw, H / vh);
  const dw = vw * scale;
  const dh = vh * scale;
  const dx = (W - dw) * 0.5;
  const dy = (H - dh) * 0.5;

  ctx.save();
  ctx.translate(dx + dw, dy);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, dw, dh);
  ctx.restore();

  const fdata       = FILTERS[curFilter];
  const accentColor = rgb(fdata.color);
  const hands       = results.multiHandLandmarks;
  const isFull      = (filterMode === 'FULL');

  // 1. If in FULLSCREEN mode: apply filter to the entire canvas!
  if (isFull) {
    const fullFiltered = applyFilter(fdata.name, 0, 0, W, H);
    if (fullFiltered) {
      ctx.drawImage(fullFiltered, 0, 0, W, H);
    }
  }

  // Coordinate projector from normalized 0..1 to canvas
  function toCanvas(lm) {
    return {
      x: dx + (1 - lm.x) * dw,
      y: dy + lm.y * dh
    };
  }

  let triggerChange = false;
  let isTouching    = false;
  const portalPts   = [];

  if (hands && hands.length > 0) {
    // ── Two-hand gesture (index tips meet) ──
    if (hands.length >= 2) {
      const p0 = toCanvas(hands[0][8]);
      const p1 = toCanvas(hands[1][8]);
      if (Math.hypot(p0.x - p1.x, p0.y - p1.y) < 50) triggerChange = true;
    }

    for (const hand of hands) {
      // ── Draw Hand Tracker Skeleton on the hand ──
      ctx.save();
      ctx.strokeStyle = isFull ? 'rgba(0, 229, 160, 0.85)' : 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth   = isFull ? 2.2 : 1.6;
      if (isFull) {
        ctx.shadowColor = '#00e5a0';
        ctx.shadowBlur  = 6;
      }
      for (const [s, e] of HAND_CONNECTIONS) {
        const p1 = toCanvas(hand[s]);
        const p2 = toCanvas(hand[e]);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
      ctx.restore();

      // Knuckle joint dots
      for (let k = 0; k < 21; k++) {
        if (k === 4 || k === 8 || k === 20) continue;
        const kp = toCanvas(hand[k]);
        ctx.save();
        ctx.fillStyle = isFull ? '#00e5a0' : 'rgba(255, 255, 255, 0.65)';
        if (isFull) {
          ctx.shadowColor = '#00e5a0';
          ctx.shadowBlur  = 4;
        }
        ctx.beginPath(); ctx.arc(kp.x, kp.y, isFull ? 3.5 : 2.6, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
      }

      const thumb = toCanvas(hand[4]);
      const index = toCanvas(hand[8]);
      const pinky = toCanvas(hand[20]);

      portalPts.push(thumb, index);

      const dist     = Math.hypot(thumb.x - pinky.x, thumb.y - pinky.y);
      const normDist = Math.hypot(hand[4].x - hand[20].x, hand[4].y - hand[20].y);
      const nearTrig = dist < 110 || normDist < 0.15;
      const onTrig   = dist < 52  || normDist < 0.07;
      if (onTrig) {
        triggerChange = true;
        isTouching = true;
      }

      // Draw connector line between thumb and pinky
      if (nearTrig) {
        ctx.save();
        ctx.strokeStyle = onTrig ? '#ef4444' : '#fbbf24';
        ctx.lineWidth   = onTrig ? 3.5 : 2;
        ctx.setLineDash(onTrig ? [] : [6, 4]);
        ctx.shadowColor = onTrig ? '#ef4444' : '#fbbf24';
        ctx.shadowBlur  = onTrig ? 10 : 5;
        ctx.beginPath();
        ctx.moveTo(thumb.x, thumb.y);
        ctx.lineTo(pinky.x, pinky.y);
        ctx.stroke();
        ctx.restore();
      }

      // Pulsing contact ripple when touching
      if (onTrig) {
        const mx = (thumb.x + pinky.x) * 0.5, my = (thumb.y + pinky.y) * 0.5;
        ctx.save();
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth   = 2.5;
        ctx.shadowColor = '#ef4444';
        ctx.shadowBlur  = 12;
        ctx.beginPath();
        ctx.arc(mx, my, 16 + ((animFrame % 8) * 3), 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      // Pinky dot (turns bright red when touching thumb)
      const pinkyColor = onTrig ? '#ef4444' : (isFull ? '#00e5a0' : '#a855f7');
      ctx.save();
      ctx.fillStyle = pinkyColor;
      ctx.shadowColor = pinkyColor;
      ctx.shadowBlur  = onTrig ? 12 : 6;
      ctx.beginPath(); ctx.arc(pinky.x, pinky.y, 9, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.8;
      ctx.beginPath(); ctx.arc(pinky.x, pinky.y, 13, 0, Math.PI * 2); ctx.stroke();
      ctx.restore();

      // Thumb & index dots (in current filter accent color)
      for (const pt of [thumb, index]) {
        ctx.save();
        ctx.fillStyle = accentColor;
        ctx.shadowColor = accentColor;
        ctx.shadowBlur  = 6;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 8.5, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.8;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 12, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
      }
    }

    // Visual feedback on guide card when touching
    const giThumb = document.getElementById('gi-thumb-pinky');
    if (giThumb) {
      if (isTouching) giThumb.classList.add('highlight');
      else giThumb.classList.remove('highlight');
    }

    // ── Debounce filter change ──
    if (triggerChange) {
      if (!gestureTriggered) {
        nextFilter();
        gestureTriggered = true;
      }
    } else {
      gestureTriggered = false;
    }

    // ── Portal filter region ONLY in PORTAL mode ──
    if (!isFull) {
      if (portalPts.length >= 4) {
        // 2 hands: 4-point quadrilateral portal
        const sorted = [...portalPts].sort((a,b) => a.y - b.y);
        const topPts = sorted.slice(0, 2).sort((a,b) => a.x - b.x);
        const botPts = sorted.slice(2, 4).sort((a,b) => a.x - b.x);
        const poly   = [topPts[0], topPts[1], botPts[1], botPts[0]];

        // Smooth polygon points with LERP for jitter-free tracking
        if (!smoothPoly || smoothPoly.length !== 4) {
          smoothPoly = poly.map(p => ({ x: p.x, y: p.y }));
        } else {
          for (let k = 0; k < 4; k++) {
            smoothPoly[k].x += (poly[k].x - smoothPoly[k].x) * 0.35;
            smoothPoly[k].y += (poly[k].y - smoothPoly[k].y) * 0.35;
          }
        }

        const pxs = smoothPoly.map(p => p.x), pys = smoothPoly.map(p => p.y);
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
            ctx.moveTo(smoothPoly[0].x, smoothPoly[0].y);
            for (let k=1; k<4; k++) ctx.lineTo(smoothPoly[k].x, smoothPoly[k].y);
            ctx.closePath();
            ctx.clip();
            ctx.drawImage(filtered, rsx, rsy);
            ctx.restore();
          }

          // Portal outline with animated laser dash
          ctx.save();
          ctx.strokeStyle = accentColor;
          ctx.lineWidth   = 2.5;
          ctx.globalAlpha = 0.95;
          ctx.setLineDash([10, 5]);
          ctx.lineDashOffset = -animFrame * 0.6;
          ctx.beginPath();
          ctx.moveTo(smoothPoly[0].x, smoothPoly[0].y);
          for (let k=1; k<4; k++) ctx.lineTo(smoothPoly[k].x, smoothPoly[k].y);
          ctx.closePath();
          ctx.stroke();
          ctx.setLineDash([]);
          ctx.restore();

          // Spark particles at corners
          for (const pt of smoothPoly) {
            const px = pt.x + (Math.random()-0.5)*14;
            const py = pt.y + (Math.random()-0.5)*14;
            ctx.save();
            ctx.fillStyle = accentColor;
            ctx.globalAlpha = Math.random() * 0.8 + 0.2;
            ctx.beginPath(); ctx.arc(px, py, Math.random()*2.2+0.8, 0, Math.PI*2); ctx.fill();
            ctx.restore();
          }
        }
      } else if (portalPts.length === 2) {
        // 1 hand: circular lens between thumb and index
        const p1 = portalPts[0], p2 = portalPts[1];
        const cx = (p1.x + p2.x) * 0.5;
        const cy = (p1.y + p2.y) * 0.5;
        const radius = Math.max(45, Math.hypot(p1.x - p2.x, p1.y - p2.y) * 0.85);
        const rx = Math.max(0, (cx - radius) | 0);
        const ry = Math.max(0, (cy - radius) | 0);
        const rw = Math.min(W - rx, (radius * 2) | 0);
        const rh = Math.min(H - ry, (radius * 2) | 0);

        if (rw > 24 && rh > 24) {
          const filtered = applyFilter(fdata.name, rx, ry, rw, rh);
          if (filtered) {
            ctx.save();
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, Math.PI * 2);
            ctx.clip();
            ctx.drawImage(filtered, rx, ry);
            ctx.restore();
          }

          ctx.save();
          ctx.strokeStyle = accentColor;
          ctx.lineWidth   = 2.5;
          ctx.setLineDash([8, 6]);
          ctx.lineDashOffset = -animFrame * 0.6;
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }
      }
    }
  } else {
    smoothPoly = null;
  }
}

// ─────────────────────────────────────────────
// SCRIPT LOADER & MEDIAPIPE CDN FALLBACKS
// ─────────────────────────────────────────────
const HANDS_CDN_POOLS = [
  'https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240',
  'https://unpkg.com/@mediapipe/hands@0.4.1675469240',
  'https://cdn.jsdelivr.net/npm/@mediapipe/hands',
  'https://unpkg.com/@mediapipe/hands'
];

let activeHandsCdn = HANDS_CDN_POOLS[0];

function loadScriptAsync(src) {
  return new Promise((resolve, reject) => {
    const existing = Array.from(document.querySelectorAll('script')).find(s => s.src === src);
    if (existing) {
      if (typeof window.Hands !== 'undefined') return resolve();
      existing.addEventListener('load', () => resolve());
      existing.addEventListener('error', () => reject(new Error('Load error')));
      setTimeout(() => {
        if (typeof window.Hands !== 'undefined') resolve();
        else reject(new Error('Timeout loading ' + src));
      }, 3500);
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load ' + src));
    document.head.appendChild(script);
  });
}

async function getHandsClass() {
  if (typeof window.Hands !== 'undefined') {
    return window.Hands;
  }
  for (const cdn of HANDS_CDN_POOLS) {
    try {
      const scriptUrl = `${cdn}/hands.js`;
      await loadScriptAsync(scriptUrl);
      for (let i = 0; i < 20; i++) {
        if (typeof window.Hands !== 'undefined') {
          activeHandsCdn = cdn;
          return window.Hands;
        }
        await new Promise(r => setTimeout(r, 100));
      }
    } catch (e) {
      console.warn(`CDN ${cdn} gagal atau timeout, mencoba CDN alternatif...`, e);
    }
  }
  return null;
}

function hideLoading() {
  if (loadingEl && loadingEl.style.display !== 'none') {
    loadingEl.style.opacity = '0';
    setTimeout(() => { loadingEl.style.display = 'none'; }, 300);
  }
}

// ─────────────────────────────────────────────
// NATIVE CAMERA INITIALIZATION
// ─────────────────────────────────────────────
async function startCamera() {
  if (stream) {
    try { stream.getTracks().forEach(t => t.stop()); } catch(e){}
    stream = null;
  }

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    const err = new Error('Browser Anda tidak mendukung akses kamera.');
    err.name = 'NotSupportedError';
    throw err;
  }

  const isPortrait = window.innerHeight > window.innerWidth;
  const constraints = {
    video: {
      width: { ideal: isPortrait ? 720 : 1280 },
      height: { ideal: isPortrait ? 1280 : 720 },
      facingMode: 'user'
    },
    audio: false
  };

  try {
    stream = await navigator.mediaDevices.getUserMedia(constraints);
  } catch(e) {
    // Fallback without resolution preference
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  }

  video.srcObject = stream;
  await video.play();
  camRunning = true;
  resizeCanvas();

  // Show live UI overlays (hanya tombol ikon ? dan filter 🎨 yang tampil)
  if (guideToggleBtn)  guideToggleBtn.style.display  = 'flex';
  if (filterToggleBtn) filterToggleBtn.style.display = 'flex';

  // Start continuous rendering loop
  startRenderLoop();
}

function startRenderLoop() {
  if (animId) cancelAnimationFrame(animId);

  const loop = async () => {
    if (!camRunning) return;

    if (video.videoWidth && (canvas.width !== window.innerWidth || canvas.height !== window.innerHeight)) {
      resizeCanvas();
    }

    // Fallback render if hands AI is loading or unavailable
    if (!handsInstance || !handsReady) {
      const W = canvas.width, H = canvas.height;
      const vw = video.videoWidth || 1280;
      const vh = video.videoHeight || 720;

      const scale = Math.max(W / vw, H / vh);
      const dw = vw * scale;
      const dh = vh * scale;
      const dx = (W - dw) * 0.5;
      const dy = (H - dh) * 0.5;

      ctx.save();
      ctx.translate(dx + dw, dy);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0, dw, dh);
      ctx.restore();
    } else {
      // Auto-recover if a send frame got stuck
      if (processing && (Date.now() - lastSendTime > 1200)) {
        processing = false;
      }

      if (!processing && video.readyState >= 2) {
        processing = true;
        lastSendTime = Date.now();
        try {
          await handsInstance.send({ image: video });
        } catch(e) {
          processing = false;
        }
      }
    }

    animId = requestAnimationFrame(loop);
  };

  animId = requestAnimationFrame(loop);
}

// ─────────────────────────────────────────────
// MEDIAPIPE HANDS INITIALIZATION
// ─────────────────────────────────────────────
async function initMediaPipeHands() {
  const loadingText = document.querySelector('#loading .ld-text');
  if (loadingText) loadingText.textContent = 'MEMUAT AI HAND TRACKING...';

  const HandsClass = await getHandsClass();
  if (!HandsClass) {
    console.warn('MediaPipe Hands could not be loaded from any CDN.');
    showError('⚠ AI Hand Tracking gagal dimuat (CDN terblokir/offline). Kamera tetap aktif! Klik layar atau tekan Spasi untuk ganti filter.', 6000);
    hideLoading();
    return;
  }

  try {
    handsInstance = new HandsClass({
      locateFile: f => `${activeHandsCdn}/${f}`
    });
    handsInstance.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.55,
      minTrackingConfidence: 0.5,
    });
    handsInstance.onResults((results) => {
      onResults(results);
      if (!handsReady) {
        handsReady = true;
        hideLoading();
      }
    });
    handsReady = true;
    hideLoading();
  } catch (err) {
    console.error('Gagal inisialisasi MediaPipe Hands:', err);
    showError('⚠ Model AI gagal diinisialisasi: ' + err.message);
    hideLoading();
  }
}

// ─────────────────────────────────────────────
// START APPLICATION
// ─────────────────────────────────────────────
async function startApp() {
  if (camRunning) return;

  // Reset prompt & show loader
  permPrompt.style.display = 'none';
  loadingEl.style.display  = 'flex';
  loadingEl.style.opacity  = '1';
  const loadingText = document.querySelector('#loading .ld-text');
  if (loadingText) loadingText.textContent = 'MEMUAT KAMERA...';

  try {
    // 1. Start webcam stream first so user immediately sees camera
    await startCamera();

    // 2. Initialize MediaPipe Hands in parallel
    initMediaPipeHands();

  } catch (err) {
    console.error('Gagal mengakses kamera:', err);
    loadingEl.style.display  = 'none';

    if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      showPrompt('KAMERA TIDAK DITEMUKAN', 'Webcam tidak terdeteksi di perangkat Anda.<br>Pastikan kamera terpasang dan diaktifkan.', '&#128683;');
      showError('⚠ Kamera tidak ditemukan di perangkat ini.');
    } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      showPrompt('IZIN KAMERA DIBUTUHKAN', 'Izinkan akses kamera di browser Anda,<br>lalu klik tombol di bawah untuk melanjutkan.', '&#128247;');
      showError('⚠ Akses kamera ditolak oleh browser.');
    } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
      showPrompt('KAMERA SEDANG DIGUNAKAN', 'Kamera sedang dipakai aplikasi lain.<br>Tutup aplikasi lain lalu coba lagi.', '&#9888;&#65039;');
      showError('⚠ Kamera sedang digunakan aplikasi lain.');
    } else {
      showPrompt('GAGAL MEMULAI KAMERA', `${err.message || 'Terjadi kesalahan sistem.'}<br>Klik tombol di bawah untuk mencoba kembali.`, '&#9888;&#65039;');
      showError('⚠ ' + err.message);
    }
  }
}

// ─────────────────────────────────────────────
// MANUAL FILTER CONTROLS (CLICK & KEYBOARD)
// ─────────────────────────────────────────────
function nextFilter() {
  curFilter = (curFilter + 1) % FILTERS.length;
  updateBadge(curFilter);
}
function prevFilter() {
  curFilter = (curFilter - 1 + FILTERS.length) % FILTERS.length;
  updateBadge(curFilter);
}

// Hook up floating trigger buttons
if (guideToggleBtn) {
  guideToggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleGuideModal();
  });
}
if (closeGuideBtn) {
  closeGuideBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleGuideModal(false);
  });
}

if (filterToggleBtn) {
  filterToggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleFilterDock();
  });
}
if (closeFilterBtn) {
  closeFilterBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleFilterDock(false);
  });
}

// Prevent click inside panels from triggering canvas nextFilter
if (filterDock) {
  filterDock.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}
if (gestureModal) {
  gestureModal.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

// Hook up buttons in the right-side dock
if (prevFilterBtn) {
  prevFilterBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    prevFilter();
  });
}
if (nextFilterBtn) {
  nextFilterBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    nextFilter();
  });
}
if (fullscreenToggle) {
  fullscreenToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const newMode = (filterMode === 'PORTAL') ? 'FULL' : 'PORTAL';
    setFilterMode(newMode);
    showError(newMode === 'FULL' ? 'Mode Satu Layar Aktif (Sentuh kelingking untuk ganti)' : 'Mode Portal Tangan Aktif (Bentangkan 2 tangan)');
  });
}

canvas.addEventListener('click', () => {
  nextFilter();
});

window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' || e.code === 'ArrowRight' || e.code === 'ArrowDown') {
    e.preventDefault();
    nextFilter();
  } else if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') {
    e.preventDefault();
    prevFilter();
  } else if (e.code === 'KeyM' || e.code === 'KeyP' || e.code === 'KeyF') {
    e.preventDefault();
    const newMode = (filterMode === 'PORTAL') ? 'FULL' : 'PORTAL';
    setFilterMode(newMode);
    showError(newMode === 'FULL' ? 'Mode Satu Layar Aktif' : 'Mode Portal Tangan Aktif');
  } else if (e.code === 'Slash' && e.shiftKey) { // '?' key
    e.preventDefault();
    toggleGuideModal();
  } else if (e.code === 'Escape') {
    toggleGuideModal(false);
    toggleFilterDock(false);
  }
});

// ─────────────────────────────────────────────
// AUTO-START & RETRY
// ─────────────────────────────────────────────
window.addEventListener('load', startApp);
retryBtn.addEventListener('click', () => {
  camRunning = false;
  startApp();
});
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=HTML_PAGE)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "RETROLENS", "filters": 36}
