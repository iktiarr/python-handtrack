# RETROLENS — Hand Tracking Filter App

> Aplikasi filter kamera interaktif berbasis gesture tangan. Buat "portal" dengan jari Anda dan terapkan 21 filter visual secara real-time menggunakan MediaPipe dan OpenCV.

---

## ⚡ Cara Tercepat (Windows)

**Tidak perlu install manual!** Cukup:

1. Clone atau download project ini
2. **Double-click `run.bat`**
3. Launcher muncul → klik **▶ MULAI RETROLENS**

`run.bat` akan otomatis membuat virtual environment dan menginstal semua dependensi.

---

## 📋 Persyaratan Sistem

| | |
|--|--|
| OS | Windows 10 / 11 |
| Python | 3.9 atau lebih baru |
| Webcam | Diperlukan (built-in atau eksternal) |
| RAM | Minimal 4 GB |

---

## 🚀 Instalasi Manual

```bash
# 1. Clone repo
git clone <URL_GITHUB_ANDA>
cd python-handtrack

# 2. Buat virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan launcher
python launcher.py

# Atau langsung jalankan tanpa launcher
python main.py
```

---

## 🎮 Cara Penggunaan

### Membuat Portal Filter
Arahkan **kedua tangan** ke kamera. Gunakan:
- **Jempol [T]** dan **Telunjuk [I]** dari **kedua tangan** (total 4 titik)
- Bentangkan tangan untuk memperbesar area portal
- Efek filter akan muncul di dalam area polygon tersebut

### Mengganti Filter
| Gestur | Aksi |
|--------|------|
| **Jempol + Kelingking [P]** (1 tangan) | Ganti filter berikutnya |
| **Kedua telunjuk bertemu** (2 tangan) | Ganti filter berikutnya |

> 💡 **Tip:** Titik **ungu [P]** = kelingking. Saat mendekati jempol, muncul garis kuning. Saat menyentuh (< 40px), muncul garis merah = filter berganti!

### Menutup Aplikasi
- Klik jendela kamera, lalu tekan **`Q`**
- Launcher akan muncul kembali dengan tombol **MULAI**

---

## 🎨 Daftar Filter (21 Filter)

| # | Nama | Efek |
|---|------|------|
| 1 | MONO | Grayscale |
| 2 | DUAL-TONE | Dua warna oranye & pink |
| 3 | PIXELATE | Efek piksel kotak |
| 4 | INVERT | Warna terbalik (negatif) |
| 5 | SEPIA | Foto vintage kecoklatan |
| 6 | BLUR | Blur Gaussian |
| 7 | THERMAL | Heatmap kamera termal |
| 8 | SKETCH | Efek pensil/sketsa |
| 9 | GLITCH | Distorsi glitch digital |
| 10 | NEON | Tepi bercahaya neon |
| 11 | GALAXY | Background luar angkasa (AI segmentation) |
| 12 | VINTAGE | Sepia + vignette + grain |
| 13 | CARTOON | Cel-shading kartun |
| 14 | EMBOSS | Efek timbul 3D |
| 15 | NIGHT | Night vision hijau |
| 16 | OCEAN | Warna bawah laut biru |
| 17 | FIRE | Heatmap api |
| 18 | RAINBOW | Spektrum pelangi |
| 19 | MIRROR | Cermin horizontal |
| 20 | VIGNETTE | Tepi gelap dramatis |
| 21 | OIL | Lukisan cat minyak |

---

## 🏗️ Struktur File

```
python-handtrack/
├── main.py                  # Program utama (camera + filter loop)
├── launcher.py              # Launcher GUI (tombol MULAI)
├── run.bat                  # ⬅ Double-click ini untuk mulai!
├── build_exe.bat            # Build ke .exe standalone (PyInstaller)
├── requirements.txt         # Dependencies Python
├── hand_landmarker.task     # Model MediaPipe (hand detection)
└── selfie_segmenter.tflite  # Model MediaPipe (segmentasi GALAXY)
```

---

## 📦 Deploy sebagai .EXE (Opsional)

Untuk membagikan aplikasi tanpa Python terinstall:

```bash
# Double-click build_exe.bat
# atau manual:
pip install pyinstaller
python build_exe.bat
```

File `.exe` akan ada di folder `dist/RETROLENS.exe` — bisa langsung dibagikan!

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Kamera tidak muncul | Pastikan tidak ada aplikasi lain yang menggunakan webcam |
| Tangan tidak terdeteksi | Pastikan pencahayaan cukup, tangan terlihat jelas |
| Error `No module named cv2` | Jalankan `run.bat` atau `pip install -r requirements.txt` |
| Layar terlalu zoom | Jauhkan sedikit dari kamera, atau kurangi zoom kamera di Settings |
| FPS rendah | Tutup aplikasi berat lainnya |

---

## 📄 Lisensi

MIT License — bebas digunakan dan dimodifikasi.