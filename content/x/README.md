# X post drafts (SiteKPI)

Markdown drafts for the `@sitekpi` account. GitHub Actions (`.github/workflows/post_to_x.yml`) picks one unpublished file and posts it.

## File format

```markdown
---
slug: two-yardsticks
url: https://sitekpi.net/samples
image: content/x/images/example.png
tags:
  - GA4
  - SiteKPI
---
Body text that becomes the post.
Keep it short — CJK counts as ~2 toward the 280 weighted limit.
```

- `slug` (required): stable id recorded in `data/posted_to_x.json`
- `url` (optional): defaults to `https://sitekpi.net`
- `image` (optional): repo-relative path or `https://…` URL
- `tags` (optional): hashtags without `#`
- Body: the main text (blank lines allowed)

## Local dry run

```bash
DRY_RUN=1 python3 scripts/post_to_x.py
# or load keys from ./x-key (gitignored):
python3 scripts/post_to_x.py
```
