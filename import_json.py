import json
import os
import urllib.request
from datetime import datetime

JSON_FILE = "" # Path to the Snapchat JSON file you downloaded
OUTPUT_DIR = "" # Where you want your videos to be saved

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

media_items = data.get("Saved Media", [])
total_media = len(media_items)
existing_files = set(os.listdir(OUTPUT_DIR))

print(f"Total memories found: {total_media}")

def build_filename(dt, ext):
    base = dt.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{base}{ext}"

    counter = 1
    while filename in existing_files:
        filename = f"{base}_{counter}{ext}"
        counter += 1

    return filename

for idx, item in enumerate(media_items, start=1):
    media_type = item.get("Media Type", "").lower()
    ext = ".mp4" if media_type == "video" else ".jpg"

    date_str = item.get("Date")
    if not date_str:
        print(f"[{idx}/{total_media}] Skipped (missing date)")
        continue
    try:
        capture_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        print(f"[{idx}/{total_media}] Skipped (bad date format)")
        continue

    url = item.get("Media Download Url")
    if not url:
        print(f"[{idx}/{total_media}] Skipped (missing URL)")
        continue

    filename = build_filename(capture_dt, ext)
    filepath = os.path.join(OUTPUT_DIR, filename)
    media_label = "VIDEO" if media_type == "video" else "PHOTO"
    time_str = capture_dt.strftime("%H:%M:%S UTC")

    print(f"[{idx}/{total_media}] {media_label:<5} {filename} ({time_str})")

    try:
        urllib.request.urlretrieve(url, filepath)
        existing_files.add(filename)
        print("    ✅ Downloaded")
    except Exception as e:
        print(f"    ❌ Failed ({e})")

print("All Snapchat memories downloaded ✅")
