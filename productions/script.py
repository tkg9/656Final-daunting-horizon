"""Split pasted script text into scenes and list the speaking characters.

A scene starts at a line beginning with ACT or SCENE (any case). A speaking
character is an all-caps name at the start of a line, followed by a colon or
standing alone on its line.
"""
import re

HEADING = re.compile(r"^\s*(act|scene)\b.*$", re.I | re.M)
SPEAKER = re.compile(r"^\s*([A-Z][A-Z .'-]{1,40}?)\s*(?::|$)", re.M)


def split_scenes(text):
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    starts = [m.start() for m in HEADING.finditer(text)]
    if not starts or starts[0] != 0:
        starts.insert(0, 0)
    scenes = []
    for i, start in enumerate(starts):
        chunk = text[start:starts[i + 1] if i + 1 < len(starts) else len(text)].strip()
        first_line, _, _ = chunk.partition("\n")
        heading = first_line.strip() if HEADING.match(first_line) else f"Scene {i + 1}"
        scenes.append({"number": i + 1, "heading": heading[:200], "text": chunk})
    return scenes


def characters(text):
    found = []
    for m in SPEAKER.finditer(text):
        name = m.group(1).strip()
        if HEADING.match(name) or name in found:
            continue
        found.append(name)
    return found
