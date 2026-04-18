from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.models.models import User
from app.core.security import require_reader
from app.services.gemini_service import chat, translate_all

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])


class ChatMessage(BaseModel):
    message: str
    lang: Optional[str] = "es"   # es | en | nah
    history: Optional[list] = []


@router.post("/")
async def chat_endpoint(
    body: ChatMessage,
    current_user: User = Depends(require_reader),
):
    """Chatbot técnico especializado en reactores nucleares."""
    response = await chat(
        user_message = body.message,
        history      = body.history or [],
        lang         = body.lang or "es",
    )
    return {
        "response": response,
        "lang":     body.lang,
        "user":     current_user.email,
    }


class TranslateRequest(BaseModel):
    text: str


@router.post("/translate")
async def translate_endpoint(
    body: TranslateRequest,
    current_user: User = Depends(require_reader),
):
    """Traduce un texto a español, inglés y náhuatl."""
    translations = await translate_all(body.text)
    return translations
