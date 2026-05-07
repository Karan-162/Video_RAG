import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHORT_VIDEO_FOLDER = os.path.join(BASE_DIR, "shorts_videos")
"""
config.py — Minimal config for downloader + preprocessor
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────
# Folders (AUTO-CREATED)
SHORT_VIDEO_FOLDER = os.path.join(BASE_DIR, "shorts_videos")
OUTPUT_FOLDER      = os.path.join(BASE_DIR, "useful_data")

os.makedirs(SHORT_VIDEO_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ─────────────────────────────────────────
# Models (used in preprocessing)
WHISPER_MODEL = "base"
BLIP_MODEL    = "Salesforce/blip-image-captioning-base"
# ─────────────────────────────────────────
# RAG SETTINGS (NOW REQUIRED)

# 🔑 Groq API (REQUIRED for answering)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.1-8b-instant"

# 📐 Embedding model (local)
EMBED_MODEL = "all-MiniLM-L6-v2"

# ✂️ Chunking
CHUNK_SIZE    = 400
CHUNK_OVERLAP = 60

# 🔎 Retrieval
RETRIEVER_K = 4