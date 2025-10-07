from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict
from collections import defaultdict, deque
import os, logging
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
import os
from openai import OpenAI

print("🔑 OPENAI_API_KEY loaded:", os.getenv("OPENAI_API_KEY"))


client = OpenAI()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Render pe same-origin use hoga, phir bhi theek
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- memory ---
Memory: Dict[str, deque] = defaultdict(lambda: deque(maxlen=12))

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "demo"

# UI (home page)
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# simple health
@app.get("/healthz")
def healthz():
    return {"ok": True}

# chat api
@app.post("/chat")
def chat_with_bot(req: ChatRequest, request: Request):
    user_msg = (req.query or "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty query")

    session = req.session_id or "demo"

    messages = [
        {"role":"system","content":"You are a helpful, polite customer support assistant. Be concise and clear."},
        *list(Memory[session]),
        {"role":"user","content":user_msg}
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",   # 🔴 confirm karo ke yehi model tumhare account pe available hai
            messages=messages,
            temperature=0.2
        )
        bot = resp.choices[0].message.content
    except Exception as e:
        import traceback
        error_text = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print("🚨 OpenAI API ERROR 🚨")
        print(error_text)
        raise HTTPException(status_code=502, detail=f"Model error: {str(e)}")

    Memory[session].append({"role":"user","content":user_msg})
    Memory[session].append({"role":"assistant","content":bot})
    return {"reply": bot}

# history (optional)
@app.get("/history")
def get_history(session_id: str):
    return {"session_id": session_id, "messages": list(Memory[session_id])}
