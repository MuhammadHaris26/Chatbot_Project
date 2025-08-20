from fastapi import FastAPI, Request, HTTPException
from typing import Optional, Dict, List
import secrets
from pydantic import BaseModel
from typing import Optional, Dict
from collections import defaultdict, deque
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import os, logging
from dotenv import load_dotenv
from fastapi import Query

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    filename="chatbot.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Simple in-memory store: session_id -> deque of messages ---
Memory: Dict[str, deque] = defaultdict(lambda: deque(maxlen=12))  # keep last 12 turns

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "demo"


@app.get("/")
def root():
    return {"message": "FastAPI Customer Service Bot is running 🚀"}







@app.post("/chat")
def chat_with_bot(req: ChatRequest, request: Request):
    user_msg = req.query.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty query")

    session = req.session_id or "demo"
    logging.info(f"[{session}] user: {user_msg}")

    # Build messages: system + memory + new user
    messages = [{"role":"system","content":
        "You are a helpful, polite customer support assistant. Be concise and clear."}]
    messages.extend(list(Memory[session]))
    messages.append({"role":"user","content":user_msg})

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2
        )
        bot = resp.choices[0].message.content
    except Exception as e:
        logging.exception("OpenAI error")
        raise HTTPException(status_code=502, detail=f"Model error: {e}")

    # update memory
    Memory[session].append({"role":"user","content":user_msg})
    Memory[session].append({"role":"assistant","content":bot})

    logging.info(f"[{session}] bot: {bot}")
    return {"reply": bot}
@app.get("/history/{session_id}")
def get_history(session_id: str):
    history = list(Memory[session_id])  # deque -> list
    formatted = []
    for msg in history:
        formatted.append({
            "sender": "user" if msg["role"] == "user" else "bot",
            "text": msg["content"]
        })
    return {"history": formatted}
