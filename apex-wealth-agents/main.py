# main.py (snippet)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from orchestrator import chat

app = FastAPI(title="Apex Advisor")
from fastapi.responses import PlainTextResponse

@app.exception_handler(Exception)
async def _debug_ex_handler(request, exc):
    import traceback, sys
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return PlainTextResponse(tb, status_code=500)

class ChatReq(BaseModel):
    session_id: str
    message: str
    context: List[Dict[str, str]] = []

@app.post("/chat")
def chat_api(req: ChatReq):
    return chat(req.message, req.context)
