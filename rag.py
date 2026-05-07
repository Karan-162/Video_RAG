"""
rag.py — Improved RAG engine
"""
import os

from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    RETRIEVER_K,
)

# ─────────────────────────────────────────
# State
_vectorstore = None
_rag_chain = None

# ─────────────────────────────────────────
# Load embeddings once
print("📐 Loading embedding model...")
_embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
print("✅ Embeddings ready.")


# ─────────────────────────────────────────
def reset():
    global _vectorstore, _rag_chain
    _vectorstore = None
    _rag_chain = None


# ─────────────────────────────────────────
def build_rag(doc: str):
    global _vectorstore, _rag_chain

    if not doc or len(doc.strip()) < 20:
        raise ValueError("❌ Document is empty or too small")

    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY missing in .env")

    # 1. Split text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(doc)
    print(f"✂️ {len(chunks)} chunks created")

    # 2. Create persistent vector DB (better than in-memory)
    persist_dir = "chroma_db"

    _vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=_embeddings,
        persist_directory=persist_dir,
    )

    # 3. Retriever
    retriever = _vectorstore.as_retriever(
        search_kwargs={"k": RETRIEVER_K}
    )

        # 4. Stronger prompt
    prompt = PromptTemplate.from_template(
        """You are an AI assistant analyzing a YouTube Shorts video.

    Your task:
    - Use the provided context (from the video) as the PRIMARY source.
    - If the context is incomplete or missing details, use your own knowledge to enhance the answer.

    Rules:
    1. Always prioritize video context.
    2. If context is weak or missing, supplement with general knowledge.
    3. Be clear about what comes from the video vs your own understanding.

    Format your answer like this:

    From Video:
    <what is clearly found in the video>

    Enhanced Explanation:
    <your additional explanation, reasoning, or inferred purpose>

    Context:
    {context}

    Question: {question}

    Answer:"""
    )

    # 5. LLM
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.2,
    )

    # 6. Format docs
    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    # 7. Chain
    _rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ RAG ready")


# ─────────────────────────────────────────
def ask(question: str) -> str:
    if _rag_chain is None:
        raise RuntimeError("❌ RAG not initialized. Run build_rag() first.")

    if not question.strip():
        return "❌ Please ask a valid question."

    return _rag_chain.invoke(question)


# ─────────────────────────────────────────
def is_ready() -> bool:
    return _rag_chain is not None