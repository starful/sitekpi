#!/usr/bin/env python3
"""Post one SiteKPI draft from content/x/ to X (@sitekpi).

Used by .github/workflows/post_to_x.yml (Tue/Thu 08:00 JST).
Drafts are markdown with optional image / url / tags front matter.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

import frontmatter
import tweepy
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "content" / "x"
HISTORY_PATH = BASE_DIR / "data" / "posted_to_x.json"
SITE_URL = os.getenv("SITE_URL", "https://sitekpi.net").rstrip("/")
HISTORY_KEEP = 60
TWEET_WEIGHTED_LIMIT = 280
URL_WEIGHTED_LENGTH = 23
MAX_IMAGE_BYTES = 4_800_000
X_KEY_PATH = BASE_DIR / "x-key"


def weighted_len(text: str) -> int:
    """Approximate X weighted length (CJK/emoji ≈ 2, ASCII ≈ 1)."""
    n = 0
    for ch in text:
        n += 2 if ord(ch) > 0x7F else 1
    return n


def trim_weighted(text: str, limit: int) -> str:
    if weighted_len(text) <= limit:
        return text
    out: list[str] = []
    used = 0
    for ch in text:
        w = 2 if ord(ch) > 0x7F else 1
        if used + w > limit:
            break
        out.append(ch)
        used += w
    return "".join(out).rstrip()


def load_x_key_file() -> None:
    """Fill missing X_* env vars from a local x-key dump (gitignored)."""
    if not X_KEY_PATH.is_file():
        return
    text = X_KEY_PATH.read_text(encoding="utf-8")
    mapping = {
        "X_API_KEY": r"消費者\s*キー?\s*\n(\S+)",
        "X_API_SECRET": r"Secret Key\s*\n(\S+)",
        "X_ACCESS_TOKEN": r"액세스\s*토큰\s*\n(\S+)|アクセス\s*トークン\s*\n(\S+)",
        "X_ACCESS_SECRET": r"액세스\s*토큰\s*시크릿\s*\n(\S+)|アクセス\s*トークン\s*シークレット\s*\n(\S+)",
    }
    for env_name, pattern in mapping.items():
        if os.getenv(env_name):
            continue
        m = re.search(pattern, text)
        if not m:
            continue
        val = next((g for g in m.groups() if g), None)
        if val:
            os.environ[env_name] = val


def load_history() -> list[str]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(data, list):
        return [str(s) for s in data]
    if not isinstance(data, dict):
        return []
    slugs = data.get("slugs") or []
    if not isinstance(slugs, list):
        return []
    return [str(s) for s in slugs]


def save_history(slugs: list[str]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(
        json.dumps({"slugs": slugs[-HISTORY_KEEP:]}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def load_posts() -> list[dict]:
    posts: list[dict] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.name.upper() == "README.MD" or path.name.lower() == "readme.md":
            continue
        try:
            post = frontmatter.load(path)
        except Exception as exc:
            print(f"skip {path}: {exc}", file=sys.stderr)
            continue
        slug = str(post.get("slug") or path.stem).strip()
        body = (post.content or "").strip()
        if not slug or not body:
            continue
        url = str(post.get("url") or SITE_URL).strip() or SITE_URL
        image = str(post.get("image") or "").strip()
        tags_raw = post.get("tags") or []
        if isinstance(tags_raw, str):
            tags = [tags_raw]
        elif isinstance(tags_raw, list):
            tags = [str(t).strip() for t in tags_raw if str(t).strip()]
        else:
            tags = []
        posts.append(
            {
                "slug": slug,
                "body": body,
                "url": url,
                "image": image,
                "tags": tags,
                "path": str(path.relative_to(BASE_DIR)),
            }
        )
    if not posts:
        raise FileNotFoundError(f"No markdown drafts under {POSTS_DIR}")
    return posts


def pick_post(posts: list[dict], recent: list[str]) -> dict:
    recent_set = set(recent)
    unused = [p for p in posts if p["slug"] not in recent_set]
    pool = unused or posts
    return random.choice(pool)


def build_tweet(post: dict) -> str:
    url = post["url"]
    tags = post.get("tags") or []
    tag_line = " ".join(f"#{t.lstrip('#')}" for t in tags)
    body = re.sub(r"\n{3,}", "\n\n", post["body"]).strip()

    # Budget: body + blank + url + optional tags. URL counts as fixed t.co length.
    parts_tail = ["", url]
    if tag_line:
        parts_tail.extend(["", tag_line])
    fixed = "\n".join(parts_tail)
    budget = (
        TWEET_WEIGHTED_LIMIT
        - weighted_len(fixed)
        - URL_WEIGHTED_LENGTH
        + weighted_len(url)
    )
    body = trim_weighted(body, max(20, budget))
    return "\n".join([body, *parts_tail])


def credentials() -> tuple[str, str, str, str]:
    load_x_key_file()
    key = os.getenv("X_API_KEY")
    secret = os.getenv("X_API_SECRET")
    token = os.getenv("X_ACCESS_TOKEN")
    token_secret = os.getenv("X_ACCESS_SECRET")
    missing = [
        name
        for name, val in [
            ("X_API_KEY", key),
            ("X_API_SECRET", secret),
            ("X_ACCESS_TOKEN", token),
            ("X_ACCESS_SECRET", token_secret),
        ]
        if not val
    ]
    if missing:
        raise SystemExit(f"Missing env: {', '.join(missing)}")
    return key, secret, token, token_secret


def v2_client() -> tweepy.Client:
    key, secret, token, token_secret = credentials()
    return tweepy.Client(
        consumer_key=key,
        consumer_secret=secret,
        access_token=token,
        access_token_secret=token_secret,
    )


def v1_api() -> tweepy.API:
    key, secret, token, token_secret = credentials()
    auth = tweepy.OAuth1UserHandler(key, secret, token, token_secret)
    return tweepy.API(auth)


def resolve_image(image: str) -> Path | None:
    if not image:
        return None
    if image.startswith(("http://", "https://")):
        suffix = Path(image.split("?", 1)[0]).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            suffix = ".jpg"
        tmp = tempfile.NamedTemporaryFile(prefix="sitekpi-x-", suffix=suffix, delete=False)
        tmp.close()
        dest = Path(tmp.name)
        req = urllib.request.Request(image, headers={"User-Agent": "sitekpi-x-poster/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read(MAX_IMAGE_BYTES + 1)
            if not data or len(data) > MAX_IMAGE_BYTES:
                dest.unlink(missing_ok=True)
                return None
            dest.write_bytes(data)
            return dest
        except Exception as exc:
            print(f"image download failed: {exc}", file=sys.stderr)
            dest.unlink(missing_ok=True)
            return None
    path = Path(image)
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.is_file():
        print(f"image missing: {path}", file=sys.stderr)
        return None
    return path


def upload_image(image: str) -> str | None:
    path = resolve_image(image)
    if not path:
        return None
    delete_after = path.parent == Path(tempfile.gettempdir()) or path.name.startswith(
        "sitekpi-x-"
    )
    try:
        media = v1_api().media_upload(filename=str(path))
        return str(media.media_id)
    except tweepy.TweepyException as exc:
        print(f"image upload failed: {exc}", file=sys.stderr)
        return None
    finally:
        if delete_after:
            path.unlink(missing_ok=True)


def main() -> None:
    dry_run = os.getenv("DRY_RUN", "").lower() in {"1", "true", "yes"}
    posts = load_posts()
    recent = load_history()
    chosen = pick_post(posts, recent)
    tweet = build_tweet(chosen)
    print(f"slug={chosen['slug']}")
    print(f"path={chosen['path']}")
    print(f"image={chosen.get('image') or '(none)'}")
    print("--- tweet ---")
    print(tweet)
    print("-------------")
    print(f"weighted≈{weighted_len(tweet) - weighted_len(chosen['url']) + URL_WEIGHTED_LENGTH}")

    if dry_run:
        print("DRY_RUN=1 — not posting")
        return

    media_ids = None
    if chosen.get("image"):
        media_id = upload_image(chosen["image"])
        if media_id:
            media_ids = [media_id]
            print(f"attached media_id={media_id}")
        else:
            print("posting without image")

    api = v2_client()
    try:
        kwargs: dict = {"text": tweet}
        if media_ids:
            kwargs["media_ids"] = media_ids
        api.create_tweet(**kwargs)
    except tweepy.TweepyException as exc:
        raise SystemExit(f"X API error: {exc}") from exc

    recent.append(chosen["slug"])
    save_history(recent)
    print(f"posted: {chosen['slug']}")


if __name__ == "__main__":
    main()
