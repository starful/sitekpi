"""Turn docs/releases/<tag>.md into GitHub Releases (run by .github/workflows/release_notes.yml).

Each file starts with front matter (tag, target commit, title, date) followed by the notes in Markdown.
A release that already exists is left alone, so editing an old file does not touch the published release.
The newest tag (by version number) is marked as the latest release.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "docs" / "releases"


def parse(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: no front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    for key in ("tag", "target", "title", "date"):
        if not meta.get(key):
            raise SystemExit(f"{path.name}: missing {key}")
    return meta, m.group(2).strip() + "\n"


def version(tag: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", tag))


def exists(tag: str) -> bool:
    return subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0


def main() -> int:
    files = sorted(DIR.glob("v*.md"), key=lambda p: version(p.stem))
    newest = files[-1].stem if files else ""
    for path in files:
        meta, body = parse(path)
        if exists(meta["tag"]):
            print(f"{meta['tag']}: already published")
            continue
        notes = DIR / f".{meta['tag']}.notes.md"
        notes.write_text(body, encoding="utf-8")
        cmd = ["gh", "release", "create", meta["tag"], "--target", meta["target"],
               "--title", f"{meta['tag']} · {meta['title']} ({meta['date']})", "--notes-file", str(notes),
               f"--latest={'true' if meta['tag'] == newest else 'false'}"]
        subprocess.run(cmd, check=True)
        notes.unlink()
        print(f"{meta['tag']}: published")
    return 0


if __name__ == "__main__":
    sys.exit(main())
