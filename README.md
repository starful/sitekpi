# SiteKPI

マーケティング・グロース向けのサイト / 業務 KPI ボード。GA4 接続 + 業界パック（業界目安つき）。

## Run

```bash
./run.sh          # → http://127.0.0.1:8766
```

Finder なら `run.command` をダブルクリック。初回（または .venv が壊れているとき）は Python 3.12+ で
.venv を作り直し、requirements.txt が変わったときだけパッケージを入れ直します。
`.env` は `.env.example` をコピーして GOOGLE_CLIENT_ID / SECRET / SESSION_SECRET を設定
（デモ接続だけなら不要）。ポート変更は `PORT=9000 ./run.sh`。

## Checks

```bash
.venv/bin/python scripts/smoke_packs.py
```

業界パックの追加方法は [packs/README.md](packs/README.md) を参照。
