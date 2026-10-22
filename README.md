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
.venv/bin/pip install -r requirements-dev.txt   # 初回のみ
.venv/bin/python -m pytest                      # tests/（OAuth state 検証など）
.venv/bin/python scripts/smoke_packs.py         # 全業界パック × 3言語の描画
```

## Sessions / deploy notes

- セッションはサーバー側（`.data/sessions.sqlite3`、暗号化）。Cookie にはランダムな ID のみ。
- 1台のサーバーなら `--workers N` で複数プロセス可（SQLite を共有）。
- 複数台（Cloud Run の複数インスタンス等）にする場合は、`sitekpi/session.py` のストアを
  共有ストア（Redis / Firestore / Cloud SQL など）に差し替える。
- 本番（https）では `SESSION_SECRET` 必須。未設定・例の値のままだと起動しない。

## Structure

```
main.py              エントリ（uvicorn main:app）
sitekpi/
  app.py             FastAPI 本体・ルーター登録
  session.py         サーバー側セッション（暗号化 SQLite）
  cache.py           プロセス内 TTL キャッシュ
  routes/            pages.py（ボード・ビルダー・設定）/ connect.py（GA4 接続）
  ga4/               oauth.py（認証）/ data.py（GA4 Data API）
  board/data.py      ボードの行データ生成
  views/             HTML（board / builder / connect / settings / home / branding）
  packs/             業界パック（1ファイル1業界）
  i18n/  metrics/    文言（ja/en/ko）・説明テキスト
static/              配信する画像・アイコン
brand/               ロゴ案（配信しない素材）
scripts/             smoke_packs.py など
```

業界パックの追加方法は [sitekpi/packs/README.md](sitekpi/packs/README.md) を参照。
