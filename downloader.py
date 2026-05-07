"""
downloader.py
Downloads a YouTube Shorts video + saves its metadata as JSON.
"""
import json
import os
import yt_dlp
from config import SHORT_VIDEO_FOLDER
os.makedirs(SHORT_VIDEO_FOLDER, exist_ok=True)

def download_shorts(url: str) -> dict:
    """
    Downloads video into shorts_videos/ folder.
    Returns metadata dict (title, uploader, duration, etc.)
    """
    os.makedirs(SHORT_VIDEO_FOLDER, exist_ok=True)

    ydl_opts = {
        "outtmpl":        f"{SHORT_VIDEO_FOLDER}/%(id)s.%(ext)s",
        "format":         "best[ext=mp4]/best",   # single mp4, no merging needed
        "writethumbnail": False,
        "writeinfojson":  False,
        "quiet":          True,
        "no_warnings":    True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    metadata = {
        "id":          info.get("id", ""),
        "title":       info.get("title", ""),
        "uploader":    info.get("uploader", ""),
        "upload_date": info.get("upload_date", ""),
        "duration":    info.get("duration", 0),
        "view_count":  info.get("view_count", 0),
        "like_count":  info.get("like_count", 0),
        "description": info.get("description", ""),
        "webpage_url": info.get("webpage_url", url),
        "hashtags":    info.get("tags") or [],   # tags can be None
    }

    # Save metadata next to the video
    meta_path = os.path.join(SHORT_VIDEO_FOLDER, f"{metadata['id']}_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    return metadata
