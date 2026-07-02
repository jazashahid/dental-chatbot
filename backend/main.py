"""
FastAPI app: routes only. All Claude call logic lives in claude_client.py;
all practice data lives in practice_config.py.
"""

import json
import logging
from pathlib import Path

import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from .claude_client import stream_reply
from .practice_config import PRACTICE_INFO
from .schemas import ChatRequest

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title=f"{PRACTICE_INFO['name']} — Virtual Assistant")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/practice-info")
async def practice_info():
    """Minimal public data for the frontend header — sourced from the same
    config the system prompt is built from, so there's one source of truth."""
    return {"name": PRACTICE_INFO["name"], "tagline": PRACTICE_INFO["tagline"]}


@app.post("/chat")
async def chat(request: ChatRequest):
    """Stream the assistant's reply as Server-Sent Events.

    Each SSE `data:` line carries a JSON-encoded string so that newlines and
    special characters inside a streamed text chunk can't break the SSE
    framing (which is newline-delimited).
    """
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def event_stream():
        try:
            async for chunk in stream_reply(messages):
                yield f"data: {json.dumps(chunk)}\n\n"
        except anthropic.APIError as exc:
            logger.error("Anthropic API error: %s", exc)
            friendly = "Sorry, I'm having trouble responding right now. Please try again in a moment, or call the office directly."
            yield f"event: error\ndata: {json.dumps(friendly)}\n\n"
        except Exception:
            logger.exception("Unexpected error while streaming chat reply")
            friendly = "Something went wrong on our end. Please try again, or call the office directly."
            yield f"event: error\ndata: {json.dumps(friendly)}\n\n"
        finally:
            yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Mounted last so it doesn't shadow the API routes above — Starlette matches
# routes in registration order, and StaticFiles("/") is a catch-all.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
