# Snapchat GUI Async Downloader

An optional GUI-based downloader built on top of the original SnapchatMemoryDownloader.

Features:
- GUI file selection
- Async multi-download (high performance)
- Duplicate file skipping
- ETA prediction
- Cross-platform (macOS / Windows)
## macOS (Homebrew Python users)

If Python was installed using Homebrew, tkinter is not included by default.

You must install the tkinter bindings separately:

    brew install python-tk@3.13

(Replace 3.13 with your Python version if different.)

Without this, you may see:
ModuleNotFoundError: No module named '_tkinter'

This does not replace the original CLI tool.
