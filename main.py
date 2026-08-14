import cv2
import mediapipe as mp
import time
import math
import numpy as np

# === MediaPipe Setup =========================================================
BaseOptions           = mp.tasks.BaseOptions
HandLandmarker        = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode     = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.4,   # diturunkan agar terdeteksi di tepi layar
    min_hand_presence_confidence=0.4,
    min_tracking_confidence=0.4
)
landmarker = HandLandmarker.create_from_options(options)

segmenter = None
try:
    ImageSegmenter        = mp.tasks.vision.ImageSegmenter
    ImageSegmenterOptions = mp.tasks.vision.ImageSegmenterOptions
    seg_options = ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path="selfie_segmenter.tflite"),
        running_mode=VisionRunningMode.VIDEO,
        output_category_mask=True
    )
    segmenter = ImageSegmenter.create_from_options(seg_options)
except Exception as e:
    print("Segmenter tidak tersedia:", e)

# === Kamera ==================================================================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
cap.set(cv2.CAP_PROP_FPS,          30)          # target FPS
cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)           # kurangi buffer agar selalu frame terbaru
cap.set(cv2.CAP_PROP_AUTOFOCUS,    1)
cap.set(cv2.CAP_PROP_ZOOM,         100)
cv2.namedWindow("RETROLENS", cv2.WINDOW_NORMAL)

# === Galaxy Background =======================================================
rng = np.random.default_rng(42)
galaxy_bg = np.zeros((1080, 1920, 3), dtype=np.uint8)
galaxy_bg[:] = (30, 10, 40)
coords = rng.integers([0, 0], [1920, 1080], size=(800, 2))
galaxy_bg[coords[:, 1], coords[:, 0]] = 255
for _ in range(120):
    sx, sy = int(rng.integers(0, 1920)), int(rng.integers(0, 1080))
    r = int(rng.integers(2, 7))
    col = (int(rng.integers(150, 256)), int(rng.integers(100, 256)), 255)
    cv2.circle(galaxy_bg, (sx, sy), r, col, -1)

print("Membuka Kamera... Tekan tombol Q di keyboard untuk keluar.")

# === Filter List & Accent Colors =============================================
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

# Konstanta warna landmark — didefinisikan sekali di sini, bukan di dalam loop
PINKY_COLOR  = (200,  50, 255)   # ungu-magenta (normal)
PINKY_ACTIVE = (0,    80, 255)   # merah (saat gesture aktif)

# Cache mask vignette per ukuran ROI agar tidak dihitung ulang tiap frame
_vig_cache: dict = {}

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


# === UI Helpers ==============================================================
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

    # Top bar
    rect_alpha(img, 0, 0, w, 46, (10, 10, 20), alpha=0.78)
    cv2.line(img, (0, 46), (w, 46), accent, 1)
    put_text_shadow(img, "RETROLENS", (18, 32), 0.90, accent, 2)
    fps_color = (0,230,90) if fps_val>=20 else (0,180,255) if fps_val>=10 else (0,80,255)
    put_text_shadow(img, f"FPS {int(fps_val):>3}", (w-100, 32), 0.58, fps_color, 1)

    # Bottom filter strip
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


# === Filter Logic ============================================================
def apply_filter(roi, filter_name, x=0, y=0, mask_person=None, frame_galaxy=None):
    if roi is None or roi.size == 0:
        return roi

    if filter_name == "MONO":
        return cv2.cvtColor(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    elif filter_name == "INVERT":
        return cv2.bitwise_not(roi)
    elif filter_name == "BLUR":
        return cv2.GaussianBlur(roi, (15, 15), 0)   # 15x15 cukup blur, lebih cepat dari 25x25
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
        pw = max(1, w_r//10)
        ph = max(1, h_r//10)
        return cv2.resize(
            cv2.resize(roi, (pw, ph), interpolation=cv2.INTER_LINEAR),
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
    elif filter_name == "GALAXY" and mask_person is not None and frame_galaxy is not None:
        bh, bw = roi.shape[:2]
        m = mask_person[y:y+bh, x:x+bw]
        g = frame_galaxy[y:y+bh, x:x+bw]
        # Safety: pastikan semua dimensi cocok sebelum boolean indexing
        ah = min(bh, m.shape[0], g.shape[0])
        aw = min(bw, m.shape[1], g.shape[1])
        if ah > 0 and aw > 0:
            out = roi[:ah, :aw].copy()
            mask_slice = m[:ah, :aw]
            out[mask_slice == 0] = g[:ah, :aw][mask_slice == 0]
            if ah == bh and aw == bw:
                return out
            result = roi.copy()
            result[:ah, :aw] = out
            return result
        return roi
    elif filter_name == "VINTAGE":
        k = np.array([[0.272,0.534,0.131],[0.349,0.686,0.168],[0.393,0.769,0.189]])
        sepia = np.clip(cv2.transform(roi, k), 0, 255).astype(np.uint8)
        h_r, w_r = roi.shape[:2]
        vig = get_vig_mask(h_r, w_r, 1.5)   # pakai cache
        grain = np.random.randint(0, 25, sepia.shape, dtype=np.uint8)
        return np.clip(sepia.astype(np.float32)*vig - grain, 0, 255).astype(np.uint8)
    elif filter_name == "CARTOON":
        color = cv2.bilateralFilter(roi, 7, 150, 150)   # sigma 150 lebih cepat dari 300
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
        vig = get_vig_mask(h_v, w_v, 1.8)   # pakai cache
        return (roi.astype(np.float32) * vig).astype(np.uint8)
    elif filter_name == "OIL":
        return cv2.medianBlur(cv2.medianBlur(roi, 7), 5)
    return roi


# === Main Loop ===============================================================
try:
    while True:
        success, img = cap.read()
        if not success:
            break

        img  = cv2.flip(img, 1)
        h, w = img.shape[:2]
        frame_galaxy = galaxy_bg[:h, :w]

        img_rgb      = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image     = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        timestamp_ms = time.time_ns() // 1_000_000

        results     = landmarker.detect_for_video(mp_image, timestamp_ms)
        filter_name = FILTERS[current_filter]
        accent      = FILTER_COLORS.get(filter_name, (0, 255, 255))

        now      = time.time()
        raw_fps  = 1.0 / max(now - fps_time, 1e-6)
        fps_time = now
        fps      = fps * 0.85 + raw_fps * 0.15   # EMA smoothing agar angka stabil

        mask_person = None
        frame_galaxy = None
        if filter_name == "GALAXY" and segmenter is not None:
            frame_galaxy = galaxy_bg[:h, :w]   # slice hanya jika GALAXY aktif
            seg_res = segmenter.segment_for_video(mp_image, timestamp_ms)
            if seg_res.category_mask is not None:
                mask_person = seg_res.category_mask.numpy_view()
                if mask_person.shape != (h, w):
                    mask_person = cv2.resize(mask_person, (w, h), interpolation=cv2.INTER_NEAREST)

        pts_portal    = []
        change_filter = False

        if results.hand_landmarks:
            # Gestur 2 tangan: kedua telunjuk bertemu
            if len(results.hand_landmarks) >= 2:
                p0  = results.hand_landmarks[0][8]
                p1  = results.hand_landmarks[1][8]
                pt0 = (int(p0.x*w), int(p0.y*h))
                pt1 = (int(p1.x*w), int(p1.y*h))
                if math.hypot(pt0[0]-pt1[0], pt0[1]-pt1[1]) < 40:
                    change_filter = True

            # Per-tangan: koordinat dihitung SEKALI, dipakai untuk gesture + drawing
            for hand_lms in results.hand_landmarks:
                thumb_pt = (int(hand_lms[4].x*w),  int(hand_lms[4].y*h))
                index_pt = (int(hand_lms[8].x*w),  int(hand_lms[8].y*h))
                pinky_pt = (int(hand_lms[20].x*w), int(hand_lms[20].y*h))

                # Portal points
                pts_portal.append(list(thumb_pt))
                pts_portal.append(list(index_pt))

                # Gesture: jempol & kelingking
                dist_tp      = math.hypot(thumb_pt[0]-pinky_pt[0], thumb_pt[1]-pinky_pt[1])
                near_trigger = dist_tp < 80
                on_trigger   = dist_tp < 40
                if on_trigger:
                    change_filter = True

                # Garis penghubung jempol-kelingking (indikator gesture)
                if near_trigger:
                    lc = PINKY_ACTIVE if on_trigger else (0, 200, 255)
                    lt = 3 if on_trigger else 1
                    cv2.line(img, thumb_pt, pinky_pt, lc, lt, cv2.LINE_AA)

                # Titik KELINGKING [20] — warna berbeda sebagai tanda ganti filter
                pk_c = PINKY_ACTIVE if on_trigger else PINKY_COLOR
                cv2.circle(img, pinky_pt, 13, pk_c, -1)
                cv2.circle(img, pinky_pt, 17, (255,255,255), 1)
                cv2.circle(img, pinky_pt, 20, pk_c, 1)
                put_text_shadow(img, "P", (pinky_pt[0]-5, pinky_pt[1]+5), 0.38, (255,255,255), 1)

                # Titik JEMPOL [4] dan TELUNJUK [8] — portal points dengan glow patch
                for pt in [thumb_pt, index_pt]:
                    cv2.circle(img, pt, 11, accent, -1)
                    cv2.circle(img, pt, 15, (255,255,255), 1)
                    cv2.circle(img, pt, 18, accent, 1)
                    # Glow lokal: hanya patch kecil di sekitar titik (bukan full-frame copy)
                    gr = 22
                    gx1 = max(0, pt[0]-gr); gy1 = max(0, pt[1]-gr)
                    gx2 = min(w, pt[0]+gr); gy2 = min(h, pt[1]+gr)
                    if gx2 > gx1 and gy2 > gy1:
                        patch = img[gy1:gy2, gx1:gx2]
                        ov    = patch.copy()
                        cv2.circle(ov, (pt[0]-gx1, pt[1]-gy1), gr-3, accent, 2)
                        img[gy1:gy2, gx1:gx2] = cv2.addWeighted(ov, 0.4, patch, 0.6, 0)

            # Proses gesture setelah semua tangan dicek
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
                    filtered_roi = apply_filter(roi, filter_name, rx, ry, mask_person, frame_galaxy)
                    if filtered_roi is None:
                        filtered_roi = roi

                    mask_poly = np.zeros((rh, rw), dtype=np.uint8)
                    cv2.fillPoly(mask_poly, [poly - [rx, ry]], 255)
                    mask3ch = cv2.cvtColor(mask_poly, cv2.COLOR_GRAY2BGR)
                    img[ry:ry+rh, rx:rx+rw] = np.where(mask3ch==255, filtered_roi, roi)

                    cv2.polylines(img, [poly], True, (255,255,255), 1)
                    cv2.polylines(img, [poly], True, accent, 2)

                    for i in range(4):
                        p1 = poly[i]; p2 = poly[(i+1)%4]
                        for _ in range(6):
                            a  = np.random.random()
                            gx = int(p1[0]*a+p2[0]*(1-a)) + np.random.randint(-12,13)
                            gy = int(p1[1]*a+p2[1]*(1-a)) + np.random.randint(-12,13)
                            cv2.circle(img, (gx,gy), np.random.randint(1,4), accent, -1)

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
    if segmenter is not None:
        segmenter.close()
