#!/usr/bin/env python3
"""
Shared Concentrate AI API client.

Provides a single `call_model()` function used by compare.py, agent.py, and discover.py.
Handles authentication, request construction, response parsing, and error handling.
"""

import json
import os
import sys
import time
from typing import Any

import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
RETRY_STATUSES = {429, 500, 502, 503, 504}

BASE_URL = "https://api.concentrate.ai/v1"
RESPONSES_URL = f"{BASE_URL}/responses/"
MODELS_URL = f"{BASE_URL}/models/"
API_KEY = os.getenv("CONCENTRATE_API_KEY", "")

# Provider-prefixed model identifiers
# Confirmed via /v1/models/ catalog — run discover.py to verify
MODELS = {
    "openai": "openai/gpt-5.1",
    "anthropic": "anthropic/claude-sonnet-4-5",
    "google": "vertex/gemini-2.5-pro",
    "xai": "xai/grok-4-1-fast-reasoning",
}


def _headers() -> dict[str, str]:
    """Build request headers with API key authentication."""
    if not API_KEY:
        print(
            "ERROR: CONCENTRATE_API_KEY not set.\n"
            "  Copy .env.example to .env and add your key.\n"
            "  Get a key at https://app.concentrate.ai"
        )
        sys.exit(1)
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Core API call
# ---------------------------------------------------------------------------


def call_model(
    model: str,
    prompt: str | list,
    *,
    temperature: float = 0.7,
    max_output_tokens: int = 500,
    tools: list[dict] | None = None,
    routing: dict | None = None,
    stream: bool = False,
    timeout: int = 60,
) -> dict[str, Any]:
    """
    Send a request to the Concentrate API and return a parsed result dict.

    Args:
        model: Model identifier (e.g., "openai/gpt-4.1") or "auto" for routing.
        prompt: Input text (str) or message array (list of dicts).
        temperature: Sampling temperature (0.0-2.0).
        max_output_tokens: Maximum tokens in response.
        tools: Optional list of tool definitions for function calling.
        routing: Optional routing config (e.g., {"strategy": "min", "metric": "cost"}).
        stream: If True, use SSE streaming.
        timeout: Request timeout in seconds.

    Returns:
        Dict with keys: model, text, tool_calls, latency_ms, status,
        stop_reason, error, raw_response. If streaming, also includes
        stream_events (int) and time_to_first_token_ms (float).
    """
    payload: dict[str, Any] = {
        "model": model if not routing else "auto",
        "input": prompt,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if tools:
        payload["tools"] = tools
    if routing:
        payload["routing"] = routing
    if stream:
        payload["stream"] = True

    start = time.perf_counter()
    resp = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(
                RESPONSES_URL,
                headers=_headers(),
                json=payload,
                timeout=timeout,
                stream=stream,
            )
            if resp.status_code in RETRY_STATUSES and attempt < MAX_RETRIES:
                wait = 2 ** attempt  # 1s, 2s, 4s
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait = min(int(retry_after), 30)
                    except ValueError:
                        pass
                print(f"  [retry {attempt + 1}/{MAX_RETRIES}] HTTP {resp.status_code}, waiting {wait}s...")
                time.sleep(wait)
                continue
            break
        except RequestException as e:
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                print(f"  [retry {attempt + 1}/{MAX_RETRIES}] {type(e).__name__}, waiting {wait}s...")
                time.sleep(wait)
                continue
            return {
                "model": model,
                "text": "",
                "tool_calls": [],
                "latency_ms": (time.perf_counter() - start) * 1000,
                "status": "error",
                "stop_reason": None,
                "error": str(e),
                "raw_response": None,
            }

    if not stream:
        elapsed_ms = (time.perf_counter() - start) * 1000
    else:
        elapsed_ms = None  # computed after reading stream

    if resp.status_code != 200:
        elapsed_ms = elapsed_ms or (time.perf_counter() - start) * 1000
        return {
            "model": model,
            "text": "",
            "tool_calls": [],
            "latency_ms": elapsed_ms,
            "status": f"http_{resp.status_code}",
            "stop_reason": None,
            "error": resp.text[:500],
            "raw_response": None,
        }

    # --- Streaming response ---
    if stream:
        return _parse_stream(resp, model, start)

    # --- Standard response ---
    elapsed_ms = elapsed_ms or (time.perf_counter() - start) * 1000
    data = resp.json()
    return _parse_response(data, model, elapsed_ms)


def _parse_response(data: dict, model: str, elapsed_ms: float) -> dict[str, Any]:
    """Parse a standard (non-streaming) Concentrate API response."""
    text = ""
    tool_calls = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text += content.get("text", "")
        elif item.get("type") == "function_call":
            tool_calls.append({
                "name": item.get("name"),
                "arguments": item.get("arguments"),
                "call_id": item.get("call_id"),
            })

    return {
        "model": data.get("model", model),
        "text": text,
        "tool_calls": tool_calls,
        "latency_ms": elapsed_ms,
        "status": data.get("status", "unknown"),
        "stop_reason": data.get("stop_reason"),
        "error": None,
        "raw_response": data,
    }


def _parse_stream(
    resp: requests.Response, model: str, start: float
) -> dict[str, Any]:
    """
    Parse an SSE streaming response.

    Collects all events, measures time-to-first-token, and assembles
    the full text from streamed deltas.
    """
    text_chunks: list[str] = []
    event_count = 0
    ttft_ms: float | None = None

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:]  # strip "data: "
        if payload.strip() == "[DONE]":
            break

        event_count += 1
        if ttft_ms is None:
            ttft_ms = (time.perf_counter() - start) * 1000

        try:
            event = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            continue

        # Extract text deltas from streamed events
        for item in event.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text_chunks.append(content.get("text", ""))

    total_ms = (time.perf_counter() - start) * 1000

    return {
        "model": model,
        "text": "".join(text_chunks),
        "tool_calls": [],
        "latency_ms": total_ms,
        "time_to_first_token_ms": ttft_ms or total_ms,
        "stream_events": event_count,
        "status": "completed",
        "stop_reason": None,
        "error": None,
        "raw_response": None,
    }


# ---------------------------------------------------------------------------
# Model catalog
# ---------------------------------------------------------------------------


def fetch_models() -> dict[str, Any]:
    """
    Fetch the model catalog from GET /v1/models/.

    Returns the raw JSON response, or an error dict.
    """
    try:
        resp = requests.get(MODELS_URL, headers=_headers(), timeout=30)
    except requests.RequestException as e:
        return {"error": str(e), "data": []}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}: {resp.text[:300]}", "data": []}

    return resp.json()


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def extract_text(result: dict, max_len: int = 200) -> str:
    """Get display-safe text from result (truncated to max_len)."""
    text = result.get("text", "") or ""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text
