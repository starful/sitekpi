# SiteKPI

A site / business KPI board for marketing and growth teams: connect GA4 and read your numbers against the previous period and industry benchmarks (業界目安). UI languages: Japanese (default), English, Korean.

- Product plan (goals, screens, rules, roadmap): [docs/plan/index.html](docs/plan/index.html)
- Developer spec (structure, routes, data flow, storage): [docs/SPEC.md](docs/SPEC.md)

## Run

Login keeps it up (same idea as Starful HQ): LaunchAgent `com.starful.sitekpi` → http://127.0.0.1:8766. `./kpi-ctl.sh on|off|status|log`. `./run.sh` while that is running only opens the page.

```bash
./run.sh          # → http://127.0.0.1:8766  (or just opens it, if already up)
```

On macOS you can double-click `run.command` in Finder. On the first run (or when `.venv` is broken) it rebuilds `.venv` with Python 3.12+, and reinstalls packages only when `requirements.txt` changes.
Copy `.env.example` to `.env` and set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `SESSION_SECRET` (not needed for the demo connection only). Change the port with `PORT=9000 ./run.sh`.

## Checks

```bash
.venv/bin/pip install -r requirements-dev.txt   # first time only
.venv/bin/python -m pytest                      # tests/ (OAuth state checks, board, flow, …)
.venv/bin/python scripts/smoke_packs.py         # render every industry pack × 3 languages
```

## Sessions / deploy notes

- Sessions are server-side (`.data/sessions.sqlite3`, encrypted). The cookie holds only a random id.
- Custom benchmarks (自社目安) and flow event mappings live in `.data/app.sqlite3` (override with `APP_DB_PATH`), per GA4 property (custom benchmarks on sample boards are per browser).
- On a single server you can run several processes with `--workers N` (they share SQLite).
- For multiple instances (e.g. Cloud Run with more than one instance), replace the store in `sitekpi/session.py` with a shared one (Redis / Firestore / Cloud SQL, …).
- In production (https) `SESSION_SECRET` is required; the app refuses to start when it is unset or still the example value.

## Structure

```
main.py              entry point (uvicorn main:app)
sitekpi/
  app.py             FastAPI app, sessions, gzip, routers
  session.py         server-side sessions (encrypted SQLite)
  cache.py           in-process TTL cache
  benchmarks.py      industry benchmarks (pack defaults + custom overrides)
  flow.py            visitor flow (event mappings, custom flows, branches, sample flow)
  selection.py       the live board's "visitor behaviour × industry"
  routes/            pages.py (board, builder, settings) / connect.py (GA4) / setup.py / benchmarks.py / flow.py / nav.py
  ga4/               oauth.py (auth) / data.py (GA4 Data API)
  board/             data.py (board rows) / extras.py (8-week trends, devices, revenue) / prev.py
  views/             view models for templates (no HTML in Python)
  templating.py      Jinja2 (autoescape, t(), static_url())
  templates/         base.html, pages, partials/, board/
  packs/             industry packs (one file per industry), sources.py (citations), flows.py (flow steps), behaviors.py (behaviours → industries)
  i18n/  metrics/    UI strings (ja/en/ko) and metric help texts
static/              css/, js/, vendor/ (Sortable bundled), icons
docs/                plan/ (product plan + screen designs), SPEC.md
brand/               logo drafts (not served)
scripts/             smoke_packs.py, …
```

Static files get `?v=<content hash>` through `static_url()` and are cached for a year (the URL changes when the content does).

To add an industry pack, see [sitekpi/packs/README.md](sitekpi/packs/README.md).

## Repository conventions

- File and folder names are English (ASCII) only.
- README files are written in English.
