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

This script automates the download of your media files and organizes them using a standardized naming convention that includes the date, media type, location, and an index for uniqueness.

1. Export your Snapchat memories as a JSON file from Snapchat.
2. Run the script from your terminal, passing the JSON file path and your desired output directory.

### Execution

```bash
python3 sc_downloader.py --input memories_history.json --output ./my_memories
```

### Script Arguments

| Argument   | Description                          | Default                 |
| :--------- | :----------------------------------- | :---------------------- |
| `--input`  | Path to the Snapchat JSON file.      | `memories_history.json` |
| `--output` | Directory where media will be saved. | `memories`              |

### Features

- **Standardized Naming**: Files are saved as `YYYYMMDD_HHMMSS_Type_Lat_Long_Index.ext`.
- **Deduplication**: Automatically skips files that have already been downloaded.
- **Retry Logic**: Automatically retries failed downloads at the end of the process.

## Requirements

- Python 3.x
- Internet connection
- `urllib` and `argparse` (included in Python standard library)
- Access to the JSON export from Snapchat
