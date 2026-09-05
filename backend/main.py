from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.repository import router as repository_router
from api.chat import router as chat_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(repository_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {
        "message": "AI Codebase Assistant API is running"
    }