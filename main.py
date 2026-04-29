#!/usr/bin/env python3

import os
import sys
import re
import shutil

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install it with:")
    print("  pip3 install Pillow")
    sys.exit(1)

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".webp", ".png", ".gif", ".tiff", ".bmp", ".heic", ".heif", ".avif"]
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".m4v", ".webm", ".3gp", ".mts", ".m2ts")

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print("Warning: pillow-heif not installed. HEIC/HEIF files will be skipped.")
    print("  To enable HEIC support, run:  pip3 install pillow-heif")
    IMAGE_EXTENSIONS = [e for e in IMAGE_EXTENSIONS if e not in (".heic", ".heif")]

def slugify(folder_name):
    # Remove anything in parentheses e.g. "(13ppl Max)"
    name = re.sub(r'\(.*?\)', '', folder_name)
    # Lowercase
    name = name.lower()
    # Replace any non-alphanumeric characters with hyphens
    name = re.sub(r'[^a-z0-9]+', '-', name)
    # Strip leading/trailing hyphens
    name = name.strip('-')
    return name

def collect_all_files(folder_path):
    """Recursively walk a folder and return all image and video file paths, sorted."""
    image_files = []
    video_files = []
    for root, dirs, files in os.walk(folder_path):
        # Skip hidden directories and the videos subfolder to avoid re-processing
        dirs[:] = sorted([d for d in dirs if not d.startswith(".") and d != "videos"])
        for f in sorted(files):
            if f.startswith("."):
                continue
            ext = os.path.splitext(f)[1].lower()
            full_path = os.path.join(root, f)
            if ext in IMAGE_EXTENSIONS:
                image_files.append(full_path)
            elif ext in VIDEO_EXTENSIONS:
                video_files.append(full_path)
    return image_files, video_files

def process_image(old_path, new_path, ext):
    """Convert any image format to JPG and resize. Returns (old_kb, new_kb)."""
    old_kb = os.path.getsize(old_path) / 1024

    img = Image.open(old_path).convert("RGB")

    # Resize to max 1920px on longest side and save as JPG
    # Applies to all formats: JPG, WebP, PNG, TIFF, BMP, HEIC, etc.
    img.thumbnail((1920, 1920), Image.LANCZOS)
    img.save(new_path, "JPEG", quality=82, optimize=True, progressive=True)

    new_kb = os.path.getsize(new_path) / 1024

    # Remove the original if it's a different path
    if old_path != new_path:
        os.remove(old_path)

    return old_kb, new_kb

def convert_and_rename(base_path):
    base_path = base_path.rstrip("/")

    if not os.path.isdir(base_path):
        print(f"Error: Folder not found: {base_path}")
        sys.exit(1)

    # Get top-level subfolders only
    top_subfolders = sorted([
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f)) and not f.startswith(".")
    ])

    if not top_subfolders:
        print("No subfolders found.")
        return

    print(f"Found {len(top_subfolders)} top-level folder(s).\n")

    for subfolder in top_subfolders:
        subfolder_path = os.path.join(base_path, subfolder)
        new_subfolder_name = slugify(subfolder)
        new_subfolder_path = os.path.join(base_path, new_subfolder_name)

        # Recursively collect all images and videos
        all_images, all_videos = collect_all_files(subfolder_path)

        if not all_images and not all_videos:
            print(f"  [{subfolder}] No files found anywhere inside, skipping.\n")
            continue

        print(f"  [{subfolder}]  ->  [{new_subfolder_name}]")
        print(f"  Found {len(all_images)} image(s) and {len(all_videos)} video(s)...\n")

        # --- Process images ---
        if all_images:
            print(f"  Images:")
            counter = 1
            for old_path in all_images:
                ext = os.path.splitext(old_path)[1].lower()
                new_name = f"{new_subfolder_name}-image-{counter:02d}.jpg"
                new_path = os.path.join(subfolder_path, new_name)

                if old_path == new_path:
                    print("    Skipped (already correct): " + os.path.basename(old_path))
                    counter += 1
                    continue

                if os.path.exists(new_path):
                    print(f"    Skipped (name conflict): {new_name} already exists")
                    continue

                try:
                    old_kb, new_kb = process_image(old_path, new_path, ext)
                    orig_format = ext.replace(".", "").upper()
                    label = f"({orig_format} -> JPG, {old_kb:.0f}kb -> {new_kb:.0f}kb)" if ext not in (".jpg", ".jpeg") else f"({old_kb:.0f}kb -> {new_kb:.0f}kb)"
                    print(f"    {os.path.relpath(old_path, subfolder_path)}  ->  {new_name}  {label}")
                except Exception as e:
                    print(f"    Error processing {os.path.basename(old_path)}: {e}")
                    continue

                counter += 1

        # --- Process videos ---
        if all_videos:
            videos_folder = os.path.join(subfolder_path, "videos")
            os.makedirs(videos_folder, exist_ok=True)
            print(f"\n  Videos  ->  videos/")
            vcounter = 1
            for old_path in all_videos:
                ext = os.path.splitext(old_path)[1].lower()
                new_name = f"{new_subfolder_name}-video-{vcounter:02d}{ext}"
                new_path = os.path.join(videos_folder, new_name)

                if os.path.exists(new_path):
                    print(f"    Skipped (name conflict): {new_name} already exists")
                    continue

                try:
                    old_kb = os.path.getsize(old_path) / 1024
                    shutil.move(old_path, new_path)
                    print(f"    {os.path.relpath(old_path, subfolder_path)}  ->  videos/{new_name}  ({old_kb:.0f}kb)")
                except Exception as e:
                    print(f"    Error moving {os.path.basename(old_path)}: {e}")
                    continue

                vcounter += 1

        # Remove any now-empty subdirectories (skip the videos folder)
        for root, dirs, files in os.walk(subfolder_path, topdown=False):
            if root == subfolder_path or root == os.path.join(subfolder_path, "videos"):
                continue
            try:
                os.rmdir(root)  # Only removes if empty
            except OSError:
                pass

        # Rename the top-level subfolder itself
        if subfolder_path != new_subfolder_path:
            os.rename(subfolder_path, new_subfolder_path)
            print(f"\n  Folder renamed: {subfolder}  ->  {new_subfolder_name}")

        print()

    print("Done!")


if __name__ == "__main__":
    print("=" * 50)
    print("  Image & Video Renamer + Converter")
    print("=" * 50)
    print()
    print("Enter the full path to your folder.")
    print("Example: /Users/yourname/Documents/SmartRez/")
    print("Press Enter with no path to quit.")
    print()

    while True:
        base_folder = input("Folder path (or press Enter to quit): ").strip()

        # Empty input = quit
        if not base_folder:
            print("Exiting.")
            sys.exit(0)

        # Remove accidental quotes if someone pastes a quoted path
        base_folder = base_folder.strip('"').strip("'")

        if os.path.isdir(base_folder):
            break

        print(f"  Warning: Folder not found: '{base_folder}'")
        print("  Please check the path and try again.\n")

    convert_and_rename(base_folder)
