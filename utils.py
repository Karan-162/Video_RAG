import shutil
import os
from config import SHORT_VIDEO_FOLDER, OUTPUT_FOLDER

CHROMA_FOLDER = "chroma_db"


def clean_all():
    print("🧹 Cleaning previous data...")

    shutil.rmtree(SHORT_VIDEO_FOLDER, ignore_errors=True)
    shutil.rmtree(OUTPUT_FOLDER, ignore_errors=True)
    shutil.rmtree(CHROMA_FOLDER, ignore_errors=True)

    os.makedirs(SHORT_VIDEO_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print("✅ Cleanup done.")