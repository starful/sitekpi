# Release notes

One file per release: `vX.Y.md`, front matter first.

```
---
tag: v0.7.3
target: <full commit sha that went live>
title: "Numbers by page"
date: 2026-11-20
---
```

When a new file reaches `main`, `.github/workflows/release_notes.yml` runs `scripts/publish_releases.py`,
which creates the tag and the GitHub Release. Releases that already exist are left as they are.
