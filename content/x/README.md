# X post drafts (SiteKPI)

Markdown drafts for the `@sitekpi` account. GitHub Actions (`.github/workflows/post_to_x.yml`) picks one unpublished file and posts it (Tue/Thu 08:00 JST, or manual run).

## Direction

**指標辞典 series** — one metric card image + a short hook. Do not pitch the product in the body; the CTA is “see your own numbers on SiteKPI”.

## Hashtags (6–7)

Always include the **common four**, then add **2–3 metric-specific** tags. Do not paste the same seven every time. Prefer searchable Japanese marketing terms; skip `#SiteKPI` until it has search volume.

| Role | Tags |
|---|---|
| Common | `GA4` · `アクセス解析` · `Webマーケティング` · `KPI` |
| Example: 登録CVR | `CVR` · `登録` · `コンバージョン` |
| Example: 流入 | `流入` · `チャネル` · `サイト改善` |
| Example: 業界目安 | `業界目安` · `ベンチマーク` · `サイト改善` |

## File format

```markdown
---
slug: glossary-signup-cvr
url: https://sitekpi.net/glossary
image: content/x/images/glossary-signup-cvr.jpg
tags:
  - GA4
  - アクセス解析
  - Webマーケティング
  - KPI
  - CVR
  - 登録
  - コンバージョン
---
📌 今日の指標：登録CVR

「100人来たら何人が登録したか」に近い数字。
意味・計算・見るポイントは画像の通り。

自分のサイトの数値で見るなら → SiteKPI
```

- `slug` (required): recorded in `data/posted_to_x.json`
- `url` (optional): defaults to `https://sitekpi.net`
- `image` (optional): repo-relative path — prefer a 1280×720 card (same layout as `verdict-cvr-21.jpg`)
- `tags` (optional): 6–7 tags per the table above
- Body: short; the card carries 意味 / 計算

## Local dry run / force one slug

```bash
DRY_RUN=1 python3 scripts/post_to_x.py
SLUG=glossary-signup-cvr DRY_RUN=1 python3 scripts/post_to_x.py
```
