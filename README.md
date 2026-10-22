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
- 自社目安と行動フローのイベント割り当ては `.data/app.sqlite3`（`APP_DB_PATH` で変更可）。GA4 プロパティ単位（自社目安の見本はブラウザ単位）。
- 1台のサーバーなら `--workers N` で複数プロセス可（SQLite を共有）。
- 複数台（Cloud Run の複数インスタンス等）にする場合は、`sitekpi/session.py` のストアを
  共有ストア（Redis / Firestore / Cloud SQL など）に差し替える。
- 本番（https）では `SESSION_SECRET` 必須。未設定・例の値のままだと起動しない。

## Structure

```
main.py              エントリ（uvicorn main:app）
sitekpi/
  app.py             FastAPI 本体・セッション・gzip・ルーター登録
  session.py         サーバー側セッション（暗号化 SQLite）
  cache.py           プロセス内 TTL キャッシュ
  benchmarks.py      業界目安（初期値＋自社目安）
  flow.py            行動フロー（イベント割り当て・見本フロー）
  routes/            pages.py（ボード・ビルダー・設定）/ connect.py（GA4 接続）/ benchmarks.py / flow.py / nav.py
  ga4/               oauth.py（認証）/ data.py（GA4 Data API）
  board/data.py      ボードの行データ生成
  views/             テンプレートに渡すデータ（HTML は書かない）
  templating.py      Jinja2（自動エスケープ・t()・static_url()）
  templates/         base.html と各ページ、partials/、board/_macros.html
  packs/             業界パック（1ファイル1業界）・sources.py（出典）・flows.py（行動フローの段）・behaviors.py（行動タイプ → 業種）
  i18n/  metrics/    文言（ja/en/ko）・説明テキスト
static/              css/・js/・vendor/（Sortable 同梱）・アイコン
brand/               ロゴ案（配信しない素材）
scripts/             smoke_packs.py など
```

静的ファイルは `static_url()` で `?v=<内容ハッシュ>` 付きになり、1年キャッシュされる（中身が変われば URL も変わる）。

業界パックの追加方法は [sitekpi/packs/README.md](sitekpi/packs/README.md) を参照。
