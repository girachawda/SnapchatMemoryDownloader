# Snapchat GUI Async Downloader

An optional GUI-based downloader built on top of the original [SnapchatMemoryDownloader](https://github.com/girachawda/SnapchatMemoryDownloader).

## Features
- GUI file selection
- Async multi-download (high performance)
- Duplicate file skipping
- ETA prediction
- Failed download tracking with automatic retries
- Cross-platform (macOS / Windows)

> Note: This GUI tool is optional and does not replace the original CLI downloader.

## Requirements
- Python 3.13+  
- `tkinter` (see macOS instructions below)  
- Python packages: `aiohttp`, `aiofiles`, `certifi` (auto-installed if missing)

## How to run
1. Open a terminal/command prompt
2. Navigate to the folder containing `snapchat_memories_downloader.py`
3. Run:

```bash
python snapchat_memories_downloader.py

4. Use the GUI to select your Snapchat JSON file and output folder.
5. Set the number of concurrent downloads (default: 24) and start downloading.

## macOS (Homebrew Python users)

If Python was installed using Homebrew, tkinter is not included by default.

Install the tkinter bindings separately:

```bash
brew install python-tk@3.13

Replace 3.13 with your Python version if different.

Without this, you may see: 
ModuleNotFoundError: No module named '_tkinter'

## Windows

Make sure Python is installed with tkinter included (standard Windows installer). Install the required packages if needed:

```bash
pip install aiohttp aiofiles certifi

## Notes
	•	Files that already exist in the output folder are skipped automatically.
	•	Failed downloads are retried automatically and tracked in the GUI.
