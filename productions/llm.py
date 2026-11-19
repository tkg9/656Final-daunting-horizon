"""Server-side client for OpenRouter's chat completions API.

All LLM calls go through chat(). The browser never talks to the LLM, and the
API key stays in the OPENROUTER_API_KEY environment variable. Tests mock
urlopen or chat(); the test runner blanks the key so a real call can't happen.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)

URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(Exception):
    """The LLM call failed or its reply was unusable. The message is safe to show users."""


def chat(messages):
    """Send chat messages to OpenRouter and return the reply text."""
    if not settings.OPENROUTER_API_KEY:
        raise LLMError("AI is not configured on this server yet (OPENROUTER_API_KEY is not set).")

    request = urllib.request.Request(
        URL,
        data=json.dumps({"model": settings.OPENROUTER_MODEL, "messages": messages}).encode(),
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "X-Title": "StageCraft",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.OPENROUTER_TIMEOUT) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as e:
        log.error("OpenRouter returned HTTP %s: %s", e.code, e.read().decode(errors="replace")[:500])
        raise LLMError(f"The AI service returned an error (HTTP {e.code}). Try again in a minute.") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        log.error("OpenRouter request failed: %s", e)
        raise LLMError("Could not reach the AI service. Try again in a minute.") from e

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = None
    if not content:
        log.error("Unexpected OpenRouter response: %s", str(payload)[:500])
        raise LLMError("The AI service returned an empty or unexpected reply. Try again.")
    log.info("OpenRouter %s replied (%s)", settings.OPENROUTER_MODEL, payload.get("usage", {}))
    return content
