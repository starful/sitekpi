"""Entry point: `uvicorn main:app` (see run.sh). The app lives in the sitekpi package."""

from sitekpi.app import app

__all__ = ["app"]
