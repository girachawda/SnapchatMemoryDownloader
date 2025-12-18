import json
import os
import urllib.request
import re
import argparse
import sys

def build_filename(memory, index):
    """
    Generates a filename based on the memory's date, type, and location.
    Format: YYYYMMDD_HHMMSS_MediaType_Lat_Long_Index.ext
    """
    # Parse date: "2025-08-30 13:31:28 UTC" -> "20250830_133128"
    date_str = memory.get("Date", "")
    date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", date_str)
    date_formatted = "unknown"
    if date_match:
        year, month, day, hour, minute, sec = date_match.groups()
        date_formatted = f"{year}{month}{day}_{hour}{minute}{sec}"

    # Parse location: "Latitude, Longitude: 52.98347, -6.9959426" -> "52.98347_-6.9959426"
    location_str = memory.get("Location", "")
    loc_match = re.search(r"Latitude,\s*Longitude:\s*([-\d.]+),\s*([-\d.]+)", location_str)
    loc_formatted = "0.0_0.0"
    if loc_match:
        loc_formatted = f"{loc_match.group(1)}_{loc_match.group(2)}"

    # Determine file extension based on media type
    media_type = memory.get("Media Type", "Unknown")
    ext = "mp4" if media_type.lower() == "video" else "jpg"

    # Add index to ensure uniqueness for memories with same timestamp
    return f"{date_formatted}_{media_type}_{loc_formatted}_{index}.{ext}"

def download_file(url, filepath):
    """Downloads a file from url to filepath."""
    try:
        urllib.request.urlretrieve(url, filepath)
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download Snapchat memories from a JSON export.")
    parser.add_argument("--input", default="memories_history.json", help="Path to the Snapchat JSON file (default: memories_history.json)")
    parser.add_argument("--output", default="memories", help="Directory to save downloaded media (default: memories)")
    args = parser.parse_args()

    json_file = args.input
    output_dir = args.output

    if not os.path.exists(json_file):
        print(f"Error: JSON file '{json_file}' not found.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    media_items = data.get("Saved Media", [])
    if not media_items:
        print("No media items found in the JSON file.")
        return

    existing_files = set(os.listdir(output_dir))
    failed_indices = []

    print(f"Found {len(media_items)} items. Starting download to '{output_dir}'...")

    for index, item in enumerate(media_items):
        url = item.get("Media Download Url")
        if not url:
            continue

        filename = build_filename(item, index)
        filepath = os.path.join(output_dir, filename)

        if filename in existing_files:
            print(f"Skipping: {filename} is already downloaded.")
            continue

        print(f"Downloading [{index+1}/{len(media_items)}] {filename}...")
        
        if download_file(url, filepath):
            existing_files.add(filename)
        else:
            failed_indices.append(index)

    # Retry failed downloads once
    if failed_indices:
        print(f"\nRetrying {len(failed_indices)} failed downloads...")
        still_failing = []
        for index in failed_indices:
            item = media_items[index]
            url = item.get("Media Download Url")
            filename = build_filename(item, index)
            filepath = os.path.join(output_dir, filename)

            print(f"Re-downloading {filename}...")
            if download_file(url, filepath):
                existing_files.add(filename)
            else:
                still_failing.append(index)
        failed_indices = still_failing

    if failed_indices:
        print(f"\nCompleted with {len(failed_indices)} permanent failures.")
    else:
        print("\nAll memories downloaded successfully! ✅")

if __name__ == "__main__":
    main()

