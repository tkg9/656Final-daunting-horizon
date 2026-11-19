"""AI script breakdown (Sprint 2: first slice).

draft_breakdown() returns suggestions for the director to review: scenes, the
characters in each, and (later) props, costumes, set pieces and cues. This
version uses the rule-based parser in script.py; an LLM backend will replace
it behind the same function, so the views and tests don't change.
"""
from . import script


def draft_breakdown(production):
    scenes = []
    everyone = []
    for scene in production.scenes.all():
        cast = script.characters(scene.text)
        scenes.append({"number": scene.number, "heading": scene.heading, "characters": cast})
        everyone += [c for c in cast if c not in everyone]
    return {"characters": everyone, "scenes": scenes, "source": "rules"}
