import json
import os
import shutil
import urllib.request
import zipfile
from datetime import datetime

JSON_FILE = ""  # Path to the Snapchat JSON file you downloaded
OUTPUT_DIR = ""  # Where you want your videos/images to be saved

os.makedirs(OUTPUT_DIR, exist_ok=True)
existing_files = set(os.listdir(OUTPUT_DIR))

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

media_items = data.get("Saved Media", [])
total_media = len(media_items)

print(f"Total memories found: {total_media}")


def ensure_unique(filename: str) -> str:
    """Return a filename that does not collide with existing files in OUTPUT_DIR."""
    if filename not in existing_files:
        return filename

    stem, ext = os.path.splitext(filename)
    counter = 1
    candidate = f"{stem}_{counter}{ext}"

    while candidate in existing_files:
        counter += 1
        candidate = f"{stem}_{counter}{ext}"

    return candidate


def has_saved_media(base: str) -> bool:
    """Check if any files with the given base name already exist."""
    return any(f.startswith(base) for f in existing_files)


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

    base = capture_dt.strftime("%Y-%m-%d_%H-%M-%S")
    time_str = capture_dt.strftime("%H:%M:%S UTC")
    media_label = "VIDEO" if media_type == "video" else "PHOTO"

    if has_saved_media(base):
        print(f"[{idx}/{total_media}] {media_label:<5} {base} ({time_str}) ⏭ Already saved")
        continue

    print(f"[{idx}/{total_media}] {media_label:<5} {base} ({time_str})")

    zip_name = f"{base}_memory.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)

    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print(f"    ❌ Failed to download ({e})")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        continue

    try:
        if zipfile.is_zipfile(zip_path):
            temp_dir = zip_path + "_unzipped"
            os.makedirs(temp_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(temp_dir)

            os.remove(zip_path)

            saved_any = False
            for filename in os.listdir(temp_dir):
                if filename.startswith("._"):
                    continue

                src = os.path.join(temp_dir, filename)
                lowercase = filename.lower()

                if lowercase.endswith(".png"):
                    out_name = f"{base}_caption.png"
                elif lowercase.endswith(".jpg"):
                    out_name = f"{base}_image.jpg"
                elif lowercase.endswith(".mp4"):
                    out_name = f"{base}_video.mp4"
                else:
                    continue

                final_name = ensure_unique(out_name)
                shutil.move(src, os.path.join(OUTPUT_DIR, final_name))
                existing_files.add(final_name)
                saved_any = True

            shutil.rmtree(temp_dir, ignore_errors=True)

            if saved_any:
                print("    ✅ Saved media files")
            else:
                print("    ⚠️ ZIP had no supported files")
        else:
            final_name = ensure_unique(f"{base}{ext}")
            shutil.move(zip_path, os.path.join(OUTPUT_DIR, final_name))
            existing_files.add(final_name)
            print("    ✅ Downloaded")
    except Exception as e:
        print(f"    ❌ Failed to process ({e})")
        if os.path.exists(zip_path):
            os.remove(zip_path)

print("All remaining Snapchat memories downloaded ✅")
