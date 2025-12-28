# Snapchat Memory Downloader

Recently, Snapchat introduced a **5GB limit on Memories**, so if you want a complete backup of all your memories, you need to download your data manually. This Python script helps you download all your Snapchat memories from a JSON export.  

As seen on: https://www.tiktok.com/@giraintech/video/7583879890265558280

---

## Getting Your Snapchat Data
1. Open Snapchat and go to Settings → My Data.
2. Request your Memories and select JSON formatting.
3. Snapchat will email you a link to download a ZIP file containing your exported data.
4. Extract the ZIP file and locate the JSON file to use with this script.

## How It Works

1. Export your Snapchat memories as a JSON file from Snapchat.
2. Provide the location of that JSON file in the script (`JSON_FILE` variable).
3. Choose the output directory where you want all your memories to be saved (`OUTPUT_DIR` variable).  

> **Tip for macOS users:** If you want to save directly to an external drive, use the path format `/Volumes/Name_of_Drive`.

4. Run the script:

```bash
python3 download_snapchat.py
```

## Requirements
- Python 3.x
- Internet connection (to download media files)
- urllib (comes with Python standard library)
- Access to the JSON export from Snapchat

## Troubleshooting
### ❌ HTTP Error 403: Forbidden

This is normal and expected.

Snapchat download links expire after some time and can only be used a limited number of times so if you are running this program a bit after downloading the json. You might need to re-export a new json from Snapchat. Re-run the code and use the new memories_history.json

