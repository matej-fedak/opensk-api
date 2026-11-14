#!/usr/bin/env python3
"""Check repository Markdown for empty/broken local links and heading anchors."""

from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def prose(text: str) -> str:
    """Preserve line numbers while ignoring fenced examples and HTML comments."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m[0].count("\n"), text, flags=re.S)
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            lines.append("")
        else:
            lines.append(line if fence is None else "")
    return "\n".join(lines)


def heading_anchors(text: str) -> set[str]:
    anchors = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    counts: dict[str, int] = {}
    for line in prose(text).splitlines():
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading[1])
        title = re.sub(r"<[^>]+>", "", html.unescape(title))
        slug = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def check_file(path: Path) -> tuple[int, list[str]]:
    text = prose(path.read_text(encoding="utf-8"))
    errors = []
    checked = 0
    links = list(re.finditer(r"!?\[[^\]\n]*\]\(([^)\n]*)\)", text))
    links += list(re.finditer(r"^\s{0,3}\[[^]\n]+\]:\s*(\S+)", text, re.M))
    for match in links:
        destination = match[1].strip()
        line = text.count("\n", 0, match.start()) + 1
        if not destination:
            errors.append(f"{path}:{line}: empty link destination")
            continue
        destination = destination[1:destination.index(">", 1)] if destination.startswith("<") and ">" in destination else destination.split()[0]
        url = urlsplit(destination)
        if url.scheme or url.netloc or destination.startswith("/"):
            continue
        checked += 1
        target = path.parent / unquote(url.path) if url.path else path
        if not target.exists():
            errors.append(f"{path}:{line}: missing target {destination}")
        elif url.fragment and target.suffix.lower() == ".md":
            if unquote(url.fragment) not in heading_anchors(target.read_text(encoding="utf-8")):
                errors.append(f"{path}:{line}: missing anchor {destination}")
    return checked, errors


def markdown_files(root: Path = ROOT) -> list[Path]:
    files = list(root.glob("*.md"))
    for directory in ("docs", ".github", "data/raw"):
        files.extend((root / directory).rglob("*.md"))
    return sorted(set(files))


def main() -> int:
    files = markdown_files()
    checked = 0
    errors = []
    for path in files:
        count, issues = check_file(path)
        checked += count
        errors.extend(issues)
    for issue in errors:
        print(issue)
    print(f"Checked {len(files)} Markdown files / {checked} local links; {len(errors)} errors")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
