"""AI feature: draft a production breakdown from a script.

The LLM reads the script and returns characters, scenes, props, costumes,
set pieces and suggested cues. The result is a draft for the director to check.
"""
import json

from . import llm
from .llm import LLMError

MAX_SCRIPT_CHARS = 60_000
CUE_KINDS = ("lighting", "sound", "set")

SYSTEM_PROMPT = """You are an experienced theatre stage manager. You read a script and draft a production breakdown.

Reply with one JSON object and nothing else, in exactly this shape:
{
  "characters": [{"name": "...", "description": "one short line"}],
  "scenes": [{"title": "...", "characters": ["names of characters who appear"]}],
  "props": ["..."],
  "costumes": ["..."],
  "set_pieces": ["..."],
  "cues": [{"scene": "scene title", "kind": "lighting" or "sound" or "set", "description": "..."}]
}

Use character names exactly as they appear in the script. List only items the
script mentions or clearly implies. If the script gives nothing for a list,
return an empty list."""


def draft_breakdown(script):
    """Ask the LLM for a breakdown of the script. Raises LLMError with a user-facing message."""
    script = script.strip()
    if not script:
        raise LLMError("Add the script text before asking for a breakdown.")
    if len(script) > MAX_SCRIPT_CHARS:
        raise LLMError(f"The script is too long for one request (over {MAX_SCRIPT_CHARS:,} characters). "
                       "Try one act at a time.")
    reply = llm.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": script},
    ])
    return parse_breakdown(reply)


def parse_breakdown(text):
    """Turn the LLM's reply into a clean breakdown dict, dropping anything malformed."""
    start, end = text.find("{"), text.rfind("}")
    try:
        raw = json.loads(text[start:end + 1]) if 0 <= start < end else None
    except json.JSONDecodeError:
        raw = None
    if not isinstance(raw, dict):
        raise LLMError("The AI reply wasn't a breakdown. Try again.")

    return {
        "characters": [
            {"name": _text(c.get("name")), "description": _text(c.get("description"))}
            for c in _dicts(raw.get("characters")) if _text(c.get("name"))
        ],
        "scenes": [
            {"title": _text(s.get("title")), "characters": _texts(s.get("characters"))}
            for s in _dicts(raw.get("scenes")) if _text(s.get("title"))
        ],
        "props": _texts(raw.get("props")),
        "costumes": _texts(raw.get("costumes")),
        "set_pieces": _texts(raw.get("set_pieces")),
        "cues": [
            {
                "scene": _text(c.get("scene")),
                "kind": _text(c.get("kind")).lower() if _text(c.get("kind")).lower() in CUE_KINDS else "other",
                "description": _text(c.get("description")),
            }
            for c in _dicts(raw.get("cues")) if _text(c.get("description"))
        ],
    }


def _text(value):
    return str(value).strip() if isinstance(value, (str, int, float)) else ""


def _texts(value):
    return [t for t in (_text(v) for v in value) if t] if isinstance(value, list) else []


def _dicts(value):
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []
