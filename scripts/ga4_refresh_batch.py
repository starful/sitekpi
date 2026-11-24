#!/usr/bin/env python3
"""Run once a day: refresh every connected site's GA4 OAuth grant before it's close to expiring.

See sitekpi/ga4/refresh_batch.py for the logic (it walks the session store directly); this is
just the CLI entry point. Failures land in list_failures(), read via GET /hq/api/ga4-refresh-failures.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sitekpi.ga4.refresh_batch import refresh_all  # noqa: E402


def main() -> None:
    counts = refresh_all()
    print(f"checked={counts['checked']} refreshed={counts['refreshed']} failed={counts['failed']}")
    if counts["failed"]:
        sys.exit(1)  # non-zero exit lets a cron wrapper alert on a bad run without reading output


if __name__ == "__main__":
    main()
