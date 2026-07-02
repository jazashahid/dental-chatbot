"""
Anthropic API call logic, kept separate from the FastAPI route handler.

The route handler (main.py) only knows about HTTP/SSE concerns. This module
owns everything about talking to Claude: which model, the system prompt, and
how the response is streamed back as plain text chunks.
"""

from collections.abc import AsyncIterator

from dotenv import load_dotenv

# Load .env before the Anthropic client is constructed below, so
# ANTHROPIC_API_KEY is available regardless of import order elsewhere.
load_dotenv()

import anthropic

from .practice_config import build_system_prompt

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# The SDK reads ANTHROPIC_API_KEY from the environment automatically —
# never hardcode a key here.
_client = anthropic.AsyncAnthropic()
_SYSTEM_PROMPT = build_system_prompt()


async def stream_reply(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    """Stream the assistant's reply as a sequence of text chunks.

    `messages` is the full conversation history (see schemas.Message) — the
    Anthropic API is stateless, so every turn resends the whole conversation.
    """
    async with _client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
