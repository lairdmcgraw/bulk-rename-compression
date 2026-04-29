# bulk-rename-compression
A Python script that batch renames, converts, and compresses media files across nested folders for website deployment. Converts all image formats (WebP, PNG, HEIC, AVIF, etc.) to optimised JPGs, renames files and folders to clean URL-friendly slugs, and sorts videos into their own subfolder — all in one run.


# 📁 Image & Video Renamer + Converter

A Python script that organises, renames, converts, and compresses image and video files across nested folders — designed for website-ready media.

---

## What It Does

Point the script at a folder containing subfolders of media files and it will:

- ✅ **Rename subfolders** to clean, web-friendly names (lowercase, hyphens, no brackets)
- ✅ **Dig through all nested subfolders** to find every image and video, no matter how deep
- ✅ **Convert all images to JPG** — WebP, PNG, TIFF, BMP, HEIC, AVIF and more
- ✅ **Resize images** to a maximum of 1920px on the longest side
- ✅ **Compress images** to a website-friendly size (roughly 300–800kb)
- ✅ **Rename images** sequentially using the folder name
- ✅ **Move videos** into their own `videos/` subfolder and rename them too
- ✅ **Clean up** empty leftover folders after processing

---

## Example

**Before:**

```
Folder/
  55ft Sealine Vic (13ppl Max)/
    raw/
      photos/
        IMG_001.heic
        IMG_002.png
      clips/
        video1.mp4
  40ft RINKER YACHT (13ppl Max)/
    photo.webp
    clip.mov
```

**After:**

```
Folder/
  55ft-sealine-vic/
    55ft-sealine-vic-image-01.jpg
    55ft-sealine-vic-image-02.jpg
    videos/
      55ft-sealine-vic-video-01.mp4
  40ft-rinker-yacht/
    40ft-rinker-yacht-image-01.jpg
    videos/
      40ft-rinker-yacht-video-01.mov
```

---

## Requirements

You need **Python 3** and two libraries installed.

### Step 1 — Check Python is installed

Open Terminal and run:

```bash
python3 --version
```

You should see something like `Python 3.11.0`. If not, download it from [python.org](https://www.python.org/downloads/).

### Step 2 — Install required libraries

Run both of these commands in Terminal:

```bash
pip3 install Pillow
pip3 install pillow-heif
```

> `Pillow` handles all image processing. `pillow-heif` adds support for HEIC files (iPhone photos). If you skip `pillow-heif`, the script will still work but HEIC files will be skipped.

---

## How to Run

1. Open **Terminal**
2. Navigate to the folder where the script is saved:

```bash
cd /path/to/script/folder
```

3. Run the script:

```bash
python3 rename_files.py
```

4. When prompted, paste the full path to your folder and press **Enter**:

```
Folder path: /Users/yourname/Documents/Folder/
```

> The terminal will print every file as it is processed so you can see exactly what happened.

---

## Supported File Types

| Type | Formats |
|---|---|
| Images (converted to JPG) | `.jpg` `.jpeg` `.webp` `.png` `.gif` `.tiff` `.bmp` `.heic` `.heif` `.avif` |
| Videos (moved, not converted) | `.mp4` `.mov` `.avi` `.mkv` `.wmv` `.flv` `.m4v` `.webm` `.3gp` `.mts` `.m2ts` |

---

## Finding Your Folder Path (Mac)

In Finder, right-click your folder, hold down the **Option** key, then click **"Copy [folder] as Pathname"**. Paste that directly into the Terminal when prompted.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python3: command not found` | Download Python from [python.org](https://www.python.org/downloads/) |
| `ModuleNotFoundError: PIL` | Run `pip3 install Pillow` in Terminal |
| `ModuleNotFoundError: pillow_heif` | Run `pip3 install pillow-heif` in Terminal |
| `Error: Folder not found` | Double-check the path you entered — make sure there are no typos |
| HEIC files being skipped | Run `pip3 install pillow-heif` in Terminal |
| VS Code wrong interpreter | Press `Cmd+Shift+P` → "Python: Select Interpreter" → choose the path shown by `which python3` |

---

## Notes

- Original files are **deleted** after a successful conversion or rename — make a backup first if you want to keep the originals
- Files are numbered in **alphabetical order** of their original filename
- Folders are only renamed at the **top level** — nested folders are cleaned up after processing
- The script will never overwrite a file if a name conflict is detected — it will skip and warn you instead
