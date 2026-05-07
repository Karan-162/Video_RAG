# 🎬 VidMind — Chat with YouTube Shorts

VidMind is a RAG-powered AI application that lets you **chat with any YouTube Shorts video**. Paste a Shorts URL, and it downloads the video, transcribes the audio, captions the frames, and builds a vector knowledge base — then lets you ask anything about the video using natural language.

---

## ✨ Features

- 📥 **Auto-download** YouTube Shorts via `yt-dlp`
- 🔊 **Audio transcription** using OpenAI Whisper (runs locally)
- 🖼️ **Visual frame captioning** using BLIP (Salesforce)
- 🧠 **RAG pipeline** with LangChain + ChromaDB
- ⚡ **LLM answers** powered by Groq (Llama 3.1 8B)
- 💬 **Clean chat UI** — single HTML file, no build step

---

## 🗂️ Project Structure

```
video_chat/
├── api.py            # FastAPI backend — /process-video & /ask endpoints
├── config.py         # All settings, loaded from .env
├── downloader.py     # Downloads Shorts + saves metadata JSON
├── processing.py     # Extracts frames, audio, transcribes, captions
├── rag.py            # Builds & queries the RAG chain (LangChain + Groq)
├── utils.py          # clean_all() — wipes previous video data
├── vidmind.html      # Frontend chat interface (open in browser)
├── .env              # Your API keys (you create this — see below)
├── shorts_videos/    # Auto-created — downloaded videos stored here
├── useful_data/      # Auto-created — frames, audio, transcripts
└── chroma_db/        # Auto-created — vector store
```

---

## ⚙️ Prerequisites

- Python **3.10+**
- `ffmpeg` installed and available in PATH (required by MoviePy)
- A free **Groq API key** — get one at [console.groq.com/keys](https://console.groq.com/keys)

### Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

---

## 🔑 Step 1 — Create Your `.env` File

In the project root (`video_chat/`), create a file named `.env`:

```bash
# video_chat/.env

GROQ_API_KEY=your_groq_api_key_here
```

> **Where to get the key:** Sign up at [console.groq.com](https://console.groq.com/keys) → API Keys → Create Key. It's free.

---

## 📦 Step 2 — Install Dependencies

Create and activate a virtual environment (recommended):

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Then install all packages:

```bash
pip install fastapi uvicorn python-dotenv \
    yt-dlp moviepy \
    openai-whisper SpeechRecognition \
    Pillow transformers \
    langchain langchain-groq langchain-chroma \
    langchain-huggingface langchain-text-splitters \
    sentence-transformers chromadb
```

> **Note:** The first run will automatically download the Whisper `base` model (~150 MB) and the BLIP captioning model (~900 MB) from HuggingFace. This only happens once.

---

## 🚀 Step 3 — Run the Backend

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
📐 Loading embedding model...
✅ Embeddings ready.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🌐 Step 4 — Open the Frontend

Open `vidmind.html` directly in your browser:

```
# macOS
open vidmind.html

# Linux
xdg-open vidmind.html

# Windows — double-click the file, or:
start vidmind.html
```

The UI connects to `http://localhost:8000` automatically.

---

## 💬 Usage

1. Paste any **YouTube Shorts URL** into the input box
2. Click **Process Video** — wait for download + processing (30–90 sec)
3. Once ready, **type any question** about the video and hit Send
4. VidMind answers using content from the video, enhanced with LLM reasoning

---

## 🔌 API Endpoints

The FastAPI backend exposes two endpoints:

### `POST /process-video`
Downloads and processes a YouTube Shorts video.

```json
// Request
{ "url": "https://www.youtube.com/shorts/abc123" }

// Response
{ "status": "success", "message": "Video processed successfully", "title": "Video Title" }
```

### `POST /ask`
Asks a question about the currently processed video.

```json
// Request
{ "question": "What is this video about?" }

// Response
{ "status": "success", "answer": "From Video:\n..." }
```

---

## ⚙️ Configuration

All settings live in `config.py` and are tunable without touching other files:

| Setting | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`, `base`, `small`, `medium`) |
| `BLIP_MODEL` | `Salesforce/blip-image-captioning-base` | HuggingFace BLIP model |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Groq LLM model |
| `EMBED_MODEL` | `all-MiniLM-L6-v2` | Local sentence-transformer for embeddings |
| `CHUNK_SIZE` | `400` | RAG text chunk size (tokens) |
| `CHUNK_OVERLAP` | `60` | Overlap between chunks |
| `RETRIEVER_K` | `4` | Number of chunks retrieved per query |

---

## 🛠️ Troubleshooting

**`GROQ_API_KEY missing`** — Make sure your `.env` file is in the same folder as `api.py` and the key is correctly set.

**`No video found`** — The Shorts URL may be private, age-restricted, or geo-blocked. Try a different public Shorts link.

**`ffmpeg not found`** — MoviePy requires ffmpeg. Install it using the instructions in Prerequisites above.

**Slow first run** — BLIP and Whisper models are downloaded on first use. Subsequent runs are much faster.

**Port already in use** — Change the port: `uvicorn api:app --port 8001` and update the API URL in `vidmind.html`.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Video Download | yt-dlp |
| Audio Transcription | OpenAI Whisper |
| Frame Captioning | Salesforce BLIP |
| Embeddings | `all-MiniLM-L6-v2` (HuggingFace) |
| Vector Store | ChromaDB |
| RAG Framework | LangChain |
| LLM | Groq — Llama 3.1 8B Instant |
| Frontend | Vanilla HTML/CSS/JS |

---

## 📄 License

MIT — free to use, modify, and distribute.
