import json
import os

import speech_recognition as sr
from moviepy import VideoFileClip
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

from config import (
    BLIP_MODEL,
    OUTPUT_FOLDER,
    SHORT_VIDEO_FOLDER,
    WHISPER_MODEL,
)

# Ensure folders always exist
os.makedirs(SHORT_VIDEO_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Lazy load BLIP
_blip_processor = None
_blip_model = None


def _load_blip():
    global _blip_processor, _blip_model
    if _blip_processor is None:
        print("🤖 Loading BLIP model...")
        _blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL)
        _blip_model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL)
        print("✅ BLIP ready.")


# ─────────────────────────────────────────────
def get_video_path() -> str | None:
    """Return first .mp4 file."""
    if not os.path.exists(SHORT_VIDEO_FOLDER):
        return None

    for fname in os.listdir(SHORT_VIDEO_FOLDER):
        if fname.endswith(".mp4"):
            return os.path.join(SHORT_VIDEO_FOLDER, fname)
    return None


# ─────────────────────────────────────────────
def extract_frames(video_path: str, frames_folder: str):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    interval = 10

    t, idx = 0, 1
    while t <= duration:
        frame_path = os.path.join(frames_folder, f"frame_{idx:04d}.jpg")
        clip.save_frame(frame_path, t=t)
        t += interval
        idx += 1

    clip.close()
    print(f"🖼️ Extracted {idx-1} frames.")


# ─────────────────────────────────────────────
def extract_audio(video_path: str, audio_path: str):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec="pcm_s16le", logger=None)
    clip.close()
    print("🔊 Audio saved.")


# ─────────────────────────────────────────────
def transcribe_audio(audio_path: str) -> str:
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_whisper(audio_data, model=WHISPER_MODEL)
        print(f"📝 Transcript ({len(text)} chars)")
        return text
    except sr.UnknownValueError:
        print("⚠️ Transcription failed")
        return ""


# ─────────────────────────────────────────────
def caption_frames(frames_folder: str) -> str:
    _load_blip()
    captions = []

    for fname in sorted(os.listdir(frames_folder)):
        if fname.endswith(".jpg"):
            img_path = os.path.join(frames_folder, fname)
            img = Image.open(img_path).convert("RGB")

            inputs = _blip_processor(img, text="", return_tensors="pt")
            out = _blip_model.generate(**inputs, max_new_tokens=50)

            caption = _blip_processor.decode(out[0], skip_special_tokens=True)
            captions.append(caption)

    print(f"🤖 Generated {len(captions)} captions")
    return " ".join(captions)


# ─────────────────────────────────────────────
def load_metadata() -> dict:
    if not os.path.exists(SHORT_VIDEO_FOLDER):
        return {}

    for fname in os.listdir(SHORT_VIDEO_FOLDER):
        if fname.endswith("_metadata.json"):
            path = os.path.join(SHORT_VIDEO_FOLDER, fname)
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return {}


# ─────────────────────────────────────────────
def build_document(metadata, transcript, captions) -> str:
    def clean(text):
        return text.strip() if text and len(text.split()) >= 4 else ""

    hashtags = metadata.get("hashtags") or []

    return "\n".join([
        f"title: {metadata.get('title', '')}",
        f"uploader: {metadata.get('uploader', '')}",
        f"description: {metadata.get('description', '')}",
        f"hashtags: {', '.join(hashtags)}",
        f"transcript: {clean(transcript)}",
        f"visual_context: {captions}",
    ])


# ─────────────────────────────────────────────
def run_preprocessing() -> str:
    video_path = get_video_path()

    if not video_path:
        raise FileNotFoundError("❌ No video found. Run downloader first.")

    video_id = os.path.basename(video_path).split(".")[0]

    # Create structured folders
    video_folder = os.path.join(OUTPUT_FOLDER, video_id)
    frames_folder = os.path.join(video_folder, "frames")

    os.makedirs(video_folder, exist_ok=True)
    os.makedirs(frames_folder, exist_ok=True)

    # Paths
    audio_path = os.path.join(video_folder, "audio.wav")
    transcript_path = os.path.join(video_folder, "transcript.txt")

    # Pipeline
    extract_frames(video_path, frames_folder)
    extract_audio(video_path, audio_path)
    transcript = transcribe_audio(audio_path)
    captions = caption_frames(frames_folder)
    metadata = load_metadata()

    doc = build_document(metadata, transcript, captions)

    # Save output
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(doc)

    print(f"✅ Saved at: {transcript_path}")

    return doc