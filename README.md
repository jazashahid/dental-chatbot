# Dental Practice Virtual Assistant

A chatbot that answers patient questions for a dental practice — hours, services, insurance, appointment booking, and common FAQs. Built for Teravista Dentistry, a dental client engaged through the Muslim Professional Society (MPS). Practice details in `backend/practice_config.py` are still placeholders past the name — see the TODO there.

## Stack

- **Backend:** FastAPI (Python), [`anthropic`](https://pypi.org/project/anthropic/) SDK, model `claude-sonnet-4-6`, streamed over Server-Sent Events (SSE)
- **Frontend:** a single `index.html` — vanilla JS and CSS, no framework, no build step
- **Legacy:** the original static page that lived at the repo root is preserved at `legacy/index.html`

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

## Run locally

```bash
uvicorn backend.main:app --reload
```

Open `http://localhost:8000`. FastAPI serves the frontend directly (via `StaticFiles`), so there's no separate frontend server and no CORS to configure.

## Project layout

```
backend/
  main.py             # FastAPI app: routes only (HTTP/SSE concerns)
  claude_client.py     # Anthropic API call + streaming logic
  practice_config.py   # Practice data + system-prompt builder (edit this to rebrand)
  schemas.py            # Pydantic request/response models
frontend/
  index.html            # Chat UI — HTML/CSS/JS, no build step
legacy/
  index.html            # The original static page, preserved
```

## How it works

**Practice config.** All practice data (hours, services, insurance, FAQs, etc.) lives in one dict, `PRACTICE_INFO`, in `backend/practice_config.py`. `build_system_prompt()` renders it into the system prompt sent to Claude, and the `/practice-info` endpoint exposes just the name and tagline as JSON for the frontend header. Rebranding to a different practice is a data edit, not a code change. Swapping `PRACTICE_INFO` for a database call or a RAG retriever later doesn't require touching anything else.

**System prompt & guardrails.** The prompt tells Claude to answer only from the injected practice data and never invent details. It also enforces the safety rules: never diagnose or recommend treatment — redirect to booking an appointment or calling the office instead; treat anything that sounds like an emergency as "call the office now, or 911/ER if urgent or after hours"; and if a question isn't covered by the practice data, say so and point to calling the office rather than guessing.

**Streaming.** `/chat` returns a `StreamingResponse` of Server-Sent Events. Each chunk is JSON-encoded on the `data:` line — SSE framing is newline-delimited, so a streamed token containing a raw newline would otherwise break it. The frontend reads the response body with `fetch()` + a stream reader (not `EventSource`, since that can't send a POST body), and appends each chunk to the current assistant bubble as it arrives.

**Conversation history.** The Anthropic API is stateless, so the frontend keeps the full conversation in a plain JS array and resends it in full with every request. There's no server-side session store — simple for a single-session demo, but it means history is lost on page refresh.

**Error handling.** `claude_client.py` lets Anthropic API errors propagate; `main.py` catches them (plus a broad exception backstop), logs the real error server-side, and sends the client a friendly SSE error event instead of crashing or leaking a stack trace.
