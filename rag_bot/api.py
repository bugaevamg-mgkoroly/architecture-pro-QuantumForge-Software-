"""FastAPI REST API для RAG-бота."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bot.rag_chain import ask

app = FastAPI(
    title="QuantumForge Knowledge Base API",
    description="RAG-бот для корпоративной базы знаний",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    status: str


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Задать вопрос базе знаний."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустым")

    result = ask(request.question, interface="api")
    return AskResponse(**result)


@app.get("/health")
async def health():
    """Проверка работоспособности."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)