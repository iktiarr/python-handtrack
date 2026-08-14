import tkinter as tk
import subprocess
import threading
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BG      = "#0a0a14"
ACCENT  = "#00e5a0"
ACCENT2 = "#7c3aed"
FG      = "#e2e8f0"
FG_DIM  = "#64748b"
BTN_RUN = "#00e5a0"
BTN_STP = "#374151"
BTN_FG  = "#0a0a14"

class RetroLensLauncher:
    def __init__(self):
        self.process = None
        self.root = tk.Tk()
        self.root.title("RETROLENS Launcher")
        self.root.geometry("320x200")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"320x200+{(sw-320)//2}+{sh-260}")
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(18, 0))
        tk.Label(hdr, text="●", font=("Segoe UI", 14), fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(hdr, text=" RETROLENS", font=("Segoe UI", 14, "bold"), fg=FG, bg=BG).pack(side="left")
        tk.Label(self.root, text="Hand Tracking Filter App", font=("Segoe UI", 9), fg=FG_DIM, bg=BG).pack(pady=(2,14))
        tk.Frame(self.root, bg=ACCENT2, height=1).pack(fill="x", padx=20)
        self.btn = tk.Button(
            self.root, text="▶   MULAI RETROLENS",
            font=("Segoe UI", 11, "bold"), fg=BTN_FG, bg=BTN_RUN,
            activeforeground=BTN_FG, activebackground="#00c48a",
            relief="flat", cursor="hand2", bd=0, pady=10,
            command=self._start
        )
        self.btn.pack(fill="x", padx=20, pady=14)
        self.status_var = tk.StringVar(value="Siap dijalankan")
        self.status_lbl = tk.Label(self.root, textvariable=self.status_var,
                                   font=("Segoe UI", 8), fg=FG_DIM, bg=BG)
        self.status_lbl.pack()
        tk.Label(self.root, text="Tekan  Q  di jendela kamera untuk menutup",
                 font=("Segoe UI", 7), fg="#374151", bg=BG).pack(pady=(4,0))

    def _start(self):
        if self.process and self.process.poll() is None:
            return
        self.btn.config(state="disabled", text="■   Sedang Berjalan...", bg=BTN_STP, fg="#9ca3af")
        self.status_var.set("RETROLENS aktif — tekan Q untuk menutup kamera")
        self.status_lbl.config(fg=ACCENT)
        def _run():
            self.process = subprocess.Popen(
                [sys.executable, os.path.join(BASE_DIR, "main.py")], cwd=BASE_DIR)
            self.process.wait()
            self.root.after(0, self._on_stopped)
        threading.Thread(target=_run, daemon=True).start()

    def _on_stopped(self):
        self.process = None
        self.btn.config(state="normal", text="▶   MULAI RETROLENS", bg=BTN_RUN, fg=BTN_FG)
        self.status_var.set("Siap dijalankan")
        self.status_lbl.config(fg=FG_DIM)

    def _on_close(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    RetroLensLauncher().run()