"""
Based on SnapchatMemoryDownloader by girachawda:
https://github.com/girachawda/SnapchatMemoryDownloader

Extended with:
- GUI
- Async downloads
- ETA prediction
- Performance optimisations

Author: Aragan
"""

# ========================
# Dependency bootstrap
# ========================
import sys
import subprocess
import importlib

REQUIRED_PACKAGES = ["aiohttp", "aiofiles", "certifi"]

def ensure_dependencies():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            *missing
        ])

ensure_dependencies()

# ========================
# Imports (safe after install)
# ========================
import ssl
import certifi
import json
import os
import time
import asyncio
import aiohttp
import aiofiles
import threading
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ========================
# SSL context (macOS safe)
# ========================
ssl_context = ssl.create_default_context(cafile=certifi.where())

# ========================
# Helpers
# ========================
def extract_media_items(data):
    saved_media = data.get("Saved Media")
    if isinstance(saved_media, list):
        return saved_media
    if isinstance(saved_media, dict):
        out = []
        for v in saved_media.values():
            if isinstance(v, list):
                out.extend(v)
        return out
    return []

# ========================
# Async download worker
# ========================
async def download_worker(session, item, output_dir, existing_files, semaphore):
    media_type = item.get("Media Type", "").lower()
    ext = ".mp4" if media_type == "video" else ".jpg"

    date_str = item.get("Date")
    url = item.get("Media Download Url") or item.get("Media Url")
    if not date_str or not url:
        return False, None

    filename = datetime.strptime(
        date_str, "%Y-%m-%d %H:%M:%S UTC"
    ).strftime("%Y-%m-%d_%H-%M-%S") + ext

    if filename in existing_files:
        return True, filename

    filepath = os.path.join(output_dir, filename)

    try:
        async with semaphore:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}")

                async with aiofiles.open(filepath, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024):  # 1 MB
                        await f.write(chunk)

        existing_files.add(filename)
        return True, filename

    except Exception:
        return False, filename

# ========================
# Async manager
# ========================
async def async_download(json_file, output_dir, progress_cb, status_cb, done_cb, max_concurrent):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    media_items = extract_media_items(data)
    total = len(media_items)
    existing_files = set(os.listdir(output_dir))

    completed = 0
    start_time = time.time()
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:

        tasks = [
            download_worker(session, item, output_dir, existing_files, semaphore)
            for item in media_items
        ]

        for coro in asyncio.as_completed(tasks):
            _, filename = await coro
            completed += 1

            progress_cb(completed, total)

            elapsed = time.time() - start_time
            avg = elapsed / completed
            remaining = avg * (total - completed)
            h, r = divmod(int(remaining), 3600)
            m, s = divmod(r, 60)

            status_cb(f"{completed}/{total}  ETA {h:02d}:{m:02d}:{s:02d}")

    done_cb()

# ========================
# Background runner
# ========================
def run_in_background(*args):
    loop = asyncio.new_event_loop()

    def runner():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_download(*args))

    threading.Thread(target=runner, daemon=True).start()

# ========================
# GUI
# ========================
class SnapchatDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snapchat Memories Downloader")
        self.root.resizable(False, False)

        self.json_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.max_concurrent = tk.IntVar(value=24)

        self.build_ui()

    def build_ui(self):
        pad = {"padx": 10, "pady": 6}

        tk.Label(self.root, text="Snapchat JSON file").grid(row=0, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.json_path, width=52).grid(row=0, column=1, **pad)
        tk.Button(self.root, text="Browse", command=self.select_json).grid(row=0, column=2, **pad)

        tk.Label(self.root, text="Output folder").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.output_dir, width=52).grid(row=1, column=1, **pad)
        tk.Button(self.root, text="Browse", command=self.select_output).grid(row=1, column=2, **pad)

        tk.Label(self.root, text="Concurrent downloads").grid(row=2, column=0, sticky="w", **pad)
        tk.Entry(self.root, textvariable=self.max_concurrent, width=8).grid(row=2, column=1, sticky="w", **pad)

        self.start_btn = tk.Button(self.root, text="Start download", command=self.start)
        self.start_btn.grid(row=3, column=1, pady=10)

        self.progress = ttk.Progressbar(self.root, length=420)
        self.progress.grid(row=4, column=0, columnspan=3, padx=10)

        self.status = tk.Label(self.root, text="Idle", anchor="w")
        self.status.grid(row=5, column=0, columnspan=3, sticky="w", padx=10, pady=(5, 10))

    def select_json(self):
        p = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if p:
            self.json_path.set(p)

    def select_output(self):
        p = filedialog.askdirectory()
        if p:
            self.output_dir.set(p)

    def start(self):
        if not self.json_path.get() or not self.output_dir.get():
            messagebox.showerror("Error", "Select JSON file and output folder")
            return

        self.start_btn.config(state="disabled")
        self.progress["value"] = 0
        self.status.config(text="Starting...")

        run_in_background(
            self.json_path.get(),
            self.output_dir.get(),
            lambda d, t: self.progress.config(value=int(d / t * 100)),
            lambda s: self.status.config(text=s),
            lambda: self.finish(),
            self.max_concurrent.get()
        )

    def finish(self):
        self.start_btn.config(state="normal")
        self.status.config(text="All downloads finished ✅")

# ========================
# Entry point
# ========================
if __name__ == "__main__":
    root = tk.Tk()
    SnapchatDownloaderGUI(root)
    root.mainloop()
