from fastapi import APIRouter
from pydantic import BaseModel

from services.container import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    question: str
    repo_id: str
    history: list = []
    limit: int = 5


@router.post("")
def chat(request: ChatRequest):

    result = rag_service.ask(
        question=request.question,
        repo_id=request.repo_id,
        limit=request.limit
    )

    return result