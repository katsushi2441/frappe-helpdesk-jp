#!/usr/bin/env python3
"""Validate the Japanese Helpdesk translation catalog."""

from __future__ import annotations

from collections import Counter
from io import BytesIO
from pathlib import Path
import re

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "helpdesk/locale/main.pot"
JAPANESE = ROOT / "helpdesk/locale/ja.po"

PATTERNS = {
    "placeholders": re.compile(
        r"\{\{[^{}]+\}\}|(?<!\{)\{(?:\d+|[A-Za-z_][\w.]*|)\}(?!\})|"
        r"%(?:\([^)]+\))?[#0+\-]*\d*(?:\.\d+)?[diouxXeEfFgGcrs]"
    ),
    "HTML tags": re.compile(r"</?[A-Za-z][^>]*>"),
    "URLs": re.compile(
        r"https?://[^\s\"'<>]+|(?<=href=[\"'])[^\"']+(?=[\"'])"
    ),
    "escaped newlines": re.compile(r"\\n"),
}


def load_catalog(path: Path):
    with path.open("rb") as stream:
        return read_po(stream)


def translated_text(message) -> str:
    if isinstance(message.string, tuple):
        return "".join(message.string)
    return message.string or ""


def main() -> int:
    source = [message for message in load_catalog(SOURCE) if message.id]
    japanese_catalog = load_catalog(JAPANESE)
    japanese = [message for message in japanese_catalog if message.id]
    by_id = {message.id: message for message in japanese}
    errors: list[str] = []

    if Counter(message.id for message in source) != Counter(
        message.id for message in japanese
    ):
        errors.append("source and Japanese message IDs differ")

    untranslated = [message.id for message in japanese if not translated_text(message)]
    fuzzy = [message.id for message in japanese if "fuzzy" in message.flags]
    if untranslated:
        errors.append(f"{len(untranslated)} messages are untranslated")
    if fuzzy:
        errors.append(f"{len(fuzzy)} messages are fuzzy")

    for label, pattern in PATTERNS.items():
        mismatches = []
        for message in source:
            target = by_id.get(message.id)
            if target is None:
                continue
            if Counter(pattern.findall(message.id)) != Counter(
                pattern.findall(translated_text(target))
            ):
                mismatches.append(message.id)
        if mismatches:
            errors.append(f"{label}: {len(mismatches)} preservation errors")

    whitespace_errors = []
    for message in source:
        target = by_id.get(message.id)
        if target is None:
            continue
        translated = translated_text(target)
        source_edges = (
            re.match(r"^\s*", message.id).group(),
            re.search(r"\s*$", message.id).group(),
        )
        target_edges = (
            re.match(r"^\s*", translated).group(),
            re.search(r"\s*$", translated).group(),
        )
        if source_edges != target_edges:
            whitespace_errors.append(message.id)
    if whitespace_errors:
        errors.append(
            f"outer whitespace: {len(whitespace_errors)} preservation errors"
        )

    if not errors:
        output = BytesIO()
        write_mo(output, japanese_catalog)
        if not output.getvalue():
            errors.append("Babel produced an empty MO catalog")

    print(f"source messages: {len(source)}")
    print(f"Japanese messages: {len(japanese)}")
    print(f"translated: {len(japanese) - len(untranslated)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
