from fastapi import FastAPI
from routers.file_router import file_router
import os
from fastapi.middleware.cors import CORSMiddleware
from settings import settings
from routers.openai_router import openai_router

app = FastAPI()


origins = settings.frontend_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # whitelist your frontend origins explicitly
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # only needed methods
    allow_headers=["Authorization", "Content-Type", "Accept"],  # restrict to needed headers
)

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

app.include_router(file_router)
app.include_router(openai_router)