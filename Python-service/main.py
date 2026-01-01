from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
import os

# ======================
# CONFIG
# ======================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HOST = os.getenv("PYTHON_SERVICE_HOST", "0.0.0.0")
PORT = int(os.getenv("PYTHON_SERVICE_PORT", "8000"))

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "models/text-embedding-004"
GENERATION_MODEL = "models/gemini-1.5-flash"

app = FastAPI(title="RAG_Python-Service", version="1.0")

class Chunk(BaseModel):
    id: str
    text: str
    metadata: dict | None = None


class EmbedRequest(BaseModel):
    documents: List[Chunk]


class Embedding(BaseModel):
    id: str
    vector: List[float]


class EmbedResponse(BaseModel):
    embeddings: List[Embedding]


class GenerateRequest(BaseModel):
    question: str
    context: List[str]


class GenerateResponse(BaseModel):
    answer: str

@app.post("/api/embed", response_model=EmbedResponse)
def embed_documents(req: EmbedRequest):
    """
    Receives text chunks from Java
    Returns vector embeddings
    """

    embeddings: List[Embedding] = []

    try:
        for doc in req.documents:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=doc.text
            )

            embeddings.append(
                Embedding(
                    id=doc.id,
                    vector=result["embedding"]
                )
            )

        return EmbedResponse(embeddings=embeddings)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
def generate_answer(req: GenerateRequest):
    """
    Receives:
      - user question
      - top-K context chunks from Java
    Returns:
      - final AI-generated answer
    """

    try:
        model = genai.GenerativeModel(GENERATION_MODEL)

        context_text = "\n\n".join(req.context)

        prompt = f"""
You are a helpful assistant.
Answer the question strictly using the provided context.
If the answer is not present, say you don't know.

Context:
{context_text}

Question:
{req.question}

Answer:
"""

        response = model.generate_content(prompt)

        return GenerateResponse(answer=response.text.strip())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def test():
    return {"working, status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
