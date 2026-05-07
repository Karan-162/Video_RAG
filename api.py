from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
from downloader import download_shorts
from processing import run_preprocessing
from rag import build_rag, ask, reset
from utils import clean_all

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_doc = None


class VideoRequest(BaseModel):
    url: str


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "API is running 🚀"}


@app.post("/process-video")
def process_video(req: VideoRequest):
    global current_doc

    try:
        clean_all()
        reset()

        metadata = download_shorts(req.url)
        doc = run_preprocessing()
        build_rag(doc)

        current_doc = doc

        return {
            "status": "success",
            "message": "Video processed successfully",
            "title": metadata.get("title"),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/ask")
def ask_question(req: QuestionRequest):
    try:
        answer = ask(req.question)
        return {"status": "success", "answer": answer}
    except Exception as e:
        return {"status": "error", "message": str(e)}