# SiteKPI

マーケティング・グロース向けのサイト / 業務 KPI ボード。GA4 接続 + 業界パック（業界目安つき）。

## Setup

Python 3.12+（開発は 3.14）

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # GOOGLE_CLIENT_ID / SECRET / SESSION_SECRET を設定
.venv/bin/uvicorn main:app --port 8766 --reload
```

## Checks

```bash
.venv/bin/python scripts/smoke_packs.py
```

業界パックの追加方法は [packs/README.md](packs/README.md) を参照。
