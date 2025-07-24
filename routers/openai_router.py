from typing import Optional
from fastapi import APIRouter, Header
import httpx
from pydantic import BaseModel
from settings import settings
from services.firebase_service import service
# Create a new router for file transformation
openai_router = APIRouter()

class TopicRequest(BaseModel):
    topic: str

@openai_router.post("/generate_question")
async def generate_question(payload: TopicRequest, authorization: Optional[str] = Header(None)):
    await service.canCreateQuiz(authorization)
    url = settings.openai_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.openai_key}"
    }
    data = {
        "model": "gpt-4.1-nano-2025-04-14",
        "prompt": {
            "id": settings.prompt_id
        },
        "input": payload.topic
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, json=data, headers=headers)
        return response.json()