"""Script breakdown.

draft_breakdown() returns suggestions for the director to review. When
OPENROUTER_API_KEY is set, the draft comes from OpenRouter. Otherwise, and
whenever that call fails, it comes from the script parser in script.py.
"""
import json
import urllib.error
import urllib.request

from django.conf import settings

from . import script

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"
MAX_CHARS = 12000


def draft_breakdown(production):
    rules = _from_rules(production)
    key = (settings.OPENROUTER_API_KEY or "").strip()
    if not key:
        return rules
    try:
        return _from_llm(production, key)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError):
        return rules


def _from_rules(production):
    scenes = []
    everyone = []
    for scene in production.scenes.all():
        cast = script.characters(scene.text)
        scenes.append({"number": scene.number, "heading": scene.heading, "characters": cast})
        everyone += [c for c in cast if c not in everyone]
    return {"characters": everyone, "scenes": scenes, "source": "rules"}


def _from_llm(production, key):
    known = list(production.scenes.all())
    parsed = _parse_content(_chat(key, _prompt(known)))
    by_number = {}
    for item in parsed.get("scenes") or []:
        if not isinstance(item, dict) or not isinstance(item.get("number"), int):
            continue
        by_number[item["number"]] = _names(item.get("characters"))
    scenes = []
    everyone = []
    for scene in known:
        cast = by_number.get(scene.number, script.characters(scene.text))
        scenes.append({"number": scene.number, "heading": scene.heading, "characters": cast})
        everyone += [c for c in cast if c not in everyone]
    return {"characters": _names(parsed.get("characters")) or everyone, "scenes": scenes, "source": "llm"}


def _names(value):
    if not isinstance(value, list):
        return []
    found = []
    for name in value:
        if not isinstance(name, str):
            continue
        cleaned = name.strip()
        if cleaned and cleaned not in found:
            found.append(cleaned)
    return found


def _prompt(scenes):
    chunks = []
    for scene in scenes:
        chunks.append(f"--- scene {scene.number}: {scene.heading}\n{scene.text}")
    body = "\n\n".join(chunks)[:MAX_CHARS]
    return (
        "List the speaking characters in this play script. "
        'Reply with JSON only, in this shape: '
        '{"characters": ["NAME"], "scenes": [{"number": 1, "characters": ["NAME"]}]}. '
        "Use the scene numbers given. Use character names from the script.\n\n"
        + body
    )


def _chat(key, prompt):
    payload = {
        "model": settings.OPENROUTER_MODEL or DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "You extract cast lists from plays. You reply with JSON only."},
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        parsed = json.loads(response.read().decode())
    return parsed["choices"][0]["message"]["content"]


def _parse_content(content):
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("model JSON must be an object")
    return parsed
