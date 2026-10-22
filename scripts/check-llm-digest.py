#!/usr/bin/env python3
"""
Check that docs/guidelines.md and docs/guidelines-llm.md are in sync.

docs/guidelines-llm.md condenses "##" sections of docs/guidelines.md for
LLMs, under the same headings. Each of its "##" sections carries a comment

    <!-- sync: guide=<sha256> llm=<sha256> -->

holding the hashes of the guide section and of the condensed section at the
time they were last brought in sync. If either side changed since, the check
fails and lists the section, so that every change to one file is mirrored
in the other.

Usage:
  python scripts/check-llm-digest.py           # check, exit 1 if out of sync
  python scripts/check-llm-digest.py --update  # record the current hashes,
                                               # after mirroring the change
"""

import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GUIDE = REPO_ROOT / "docs" / "guidelines.md"
DIGEST = REPO_ROOT / "docs" / "guidelines-llm.md"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SYNC_RE = re.compile(r"<!-- sync: guide=([0-9a-f]*) llm=([0-9a-f]*) -->\n?")


def sections(text: str) -> dict[str, str]:
    """Map each "##" heading title to its section text (up to the next "#" or "##" heading), skipping fenced code."""
    result: dict[str, str] = {}
    title: str | None = None
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING_RE.match(line)
        if match and len(match.group(1)) <= 2:
            if title is not None:
                result[title] = "\n".join(lines)
            title = match.group(2) if len(match.group(1)) == 2 else None
            lines = []
        if title is not None:
            lines.append(line)
    if title is not None:
        result[title] = "\n".join(lines)
    return result


def section_hash(text: str) -> str:
    """Hash of a section without its sync comment, ignoring trailing whitespace and blank lines."""
    text = SYNC_RE.sub("", text)
    normalized = "\n".join(line.rstrip() for line in text.splitlines() if line.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def main() -> int:
    update = "--update" in sys.argv[1:]
    guide = sections(GUIDE.read_text(encoding="utf-8"))
    digest_text = DIGEST.read_text(encoding="utf-8")
    out_of_sync: list[tuple[str, str]] = []
    for title, body in sections(digest_text).items():
        if title not in guide:
            print(f"ERROR: section '{title}' of {DIGEST.name} has no section with the same heading in {GUIDE.name}", file=sys.stderr)
            return 1
        match = SYNC_RE.search(body)
        if match is None:
            print(f"ERROR: section '{title}' of {DIGEST.name} has no sync comment", file=sys.stderr)
            return 1
        guide_hash, llm_hash = section_hash(guide[title]), section_hash(body)
        if (match.group(1), match.group(2)) == (guide_hash, llm_hash):
            continue
        if update:
            comment = f"<!-- sync: guide={guide_hash} llm={llm_hash} -->\n"
            digest_text = digest_text.replace(body, body.replace(match.group(0), comment, 1), 1)
            continue
        changed = [name for name, recorded, current in (
            (GUIDE.name, match.group(1), guide_hash),
            (DIGEST.name, match.group(2), llm_hash),
        ) if recorded != current]
        out_of_sync.append((title, " and ".join(changed)))
    if update:
        DIGEST.write_text(digest_text, encoding="utf-8")
        print(f"Recorded the current hashes in {DIGEST.relative_to(REPO_ROOT)}")
        return 0
    if out_of_sync:
        print(f"{GUIDE.name} and {DIGEST.name} are out of sync. These sections changed since they were last synced:")
        for title, changed in out_of_sync:
            print(f"  - {title} (changed in {changed})")
        print(f"Mirror the change in the other file, then run: python scripts/check-llm-digest.py --update")
        return 1
    print(f"{GUIDE.name} and {DIGEST.name} are in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
