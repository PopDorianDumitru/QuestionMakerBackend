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
    instructions: str

custom_prompt = """Formatul răspunsului tău trebuie să fie strict următorul JSON (nu adăuga nicio explicație suplimentară):
{
  "question": "Formulează aici întrebarea",
  "A": "Varianta A",
  "B": "Varianta B",
  "C": "Varianta C",
  "D": "Varianta D",
  "correct_answers": ["A", "C" ...]
}
"""

@openai_router.post("/generate_question")
async def generate_question(payload: TopicRequest, authorization: Optional[str] = Header(None)):
    await service.canCreateQuiz(authorization)
    print(payload.instructions)
    url = settings.openai_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.openai_key}"
    }
    if(payload.instructions == ""):
        data = {
            "model": "gpt-4.1-nano-2025-04-14",
            "prompt": {
                "id": settings.prompt_id,
            },
            "input": payload.topic,
        }
    else:
        data = {
            "model": "gpt-4.1-nano-2025-04-14",
            "input": payload.topic,
            "instructions": custom_prompt + "\n" + payload.instructions
        }
    async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=data, headers=headers)
            print(response)
            return response.json()