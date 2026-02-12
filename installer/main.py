import tkinter as tk
from tkinter import filedialog, ttk
import threading
import requests
import os
from pathlib import Path
from urllib.parse import urlparse

SOURCE_BASE = "https://raw.githubusercontent.com/kookjd7759/Pi_Node_management/main/image/data"
EXE_URL = "https://raw.githubusercontent.com/kookjd7759/Pi_Node_management/main/dist/UI.exe"
IMAGES = [
    "Pi_App_btn.png",
    "basic_mining_rate_txt.png",
    "close_btn.png",
    "node_bonus_txt.png",
    "start_mining_txt.png",
    "status_btn.png"
]

class Installer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Pi Manager Setup")
        self.geometry("400x300")
        self.configure(bg="#1e1e1e")

        self.target_path = None

        self.container = tk.Frame(self, bg="#1e1e1e")
        self.container.pack(fill="both", expand=True)

        self.show_first()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select install folder")
        if folder:
            self.target_path = os.path.join(folder, "Pi Manager")
            self.path_label.config(text=self.target_path, fg="white")

    def show_first(self):
        self.clear()

        tk.Label(self.container,
                 text="Pi Manager Setup",
                 font=("Segoe UI", 18, "bold"),
                 fg="white", bg="#1e1e1e").pack(pady=20)

        tk.Label(self.container,
                 text="Choose installation folder",
                 fg="#bbbbbb", bg="#1e1e1e").pack()

        self.path_label = tk.Label(self.container,
                                   text="No folder selected",
                                   fg="#777777",
                                   bg="#1e1e1e")
        self.path_label.pack(pady=5)

        tk.Button(self.container,
                  text="Browse",
                  command=self.select_folder,
                  bg="#0078d4", fg="white",
                  relief="flat", width=15).pack(pady=5)

        tk.Button(self.container,
                  text="Next",
                  command=self.show_ready,
                  bg="#3c3c3c", fg="white",
                  relief="flat", width=15).pack(pady=20)

    def show_ready(self):
        if not self.target_path:
            return

        self.clear()

        tk.Label(self.container,
                 text="Ready to Install",
                 font=("Segoe UI", 16),
                 fg="white", bg="#1e1e1e").pack(pady=30)

        btn_frame = tk.Frame(self.container, bg="#1e1e1e")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,
                  text="Back",
                  command=self.show_welcome,
                  bg="#3c3c3c", fg="white",
                  relief="flat", width=12).pack(side="left", padx=10)

        tk.Button(btn_frame,
                  text="Install",
                  command=self.start_install,
                  bg="#0078d4", fg="white",
                  relief="flat", width=12).pack(side="left", padx=10)

    def show_progress(self):
        self.clear()

        tk.Label(self.container,
                 text="Installing...",
                 font=("Segoe UI", 14),
                 fg="white", bg="#1e1e1e").pack(pady=10)

        self.progress = ttk.Progressbar(self.container,
                                        length=450,
                                        mode="determinate")
        self.progress.pack(pady=15)

        self.status = tk.Label(self.container,
                               text="Preparing...",
                               fg="#bbbbbb",
                               bg="#1e1e1e")
        self.status.pack()

    def show_complete(self):
        self.clear()

        tk.Label(self.container,
                 text="Installation Complete",
                 font=("Segoe UI", 16),
                 fg="white", bg="#1e1e1e").pack(pady=40)

        tk.Button(self.container,
                  text="OK",
                  command=self.destroy,
                  bg="#0078d4",
                  fg="white",
                  relief="flat",
                  width=15,
                  height=2).pack()

    def start_install(self):
        self.show_progress()
        threading.Thread(target=self.install_process, daemon=True).start()

    def install_process(self):
        try:
            os.makedirs(self.target_path, exist_ok=True)
            data_path = os.path.join(self.target_path, "image", "data")
            os.makedirs(data_path, exist_ok=True)

            total = len(IMAGES) + 1
            count = 0

            for img in IMAGES:
                self.update_status(f"Downloading {img}")
                self.download_file(f"{SOURCE_BASE}/{img}", data_path)
                count += 1
                self.update_progress(count, total)

            self.update_status("Downloading UI.exe")
            self.download_file(EXE_URL, self.target_path)
            count += 1
            self.update_progress(count, total)

            self.after(500, self.show_complete)

        except Exception as e:
            self.update_status(f"Error: {e}")

    def download_file(self, url, target):
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()

        filename = Path(urlparse(url).path).name
        filepath = os.path.join(target, filename)

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

    def update_progress(self, count, total):
        percent = int((count / total) * 100)
        self.after(0, lambda: self.progress.config(value=percent))

    def update_status(self, text):
        self.after(0, lambda: self.status.config(text=text))

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app = Installer()
    app.mainloop()
