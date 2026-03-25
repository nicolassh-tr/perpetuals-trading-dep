"""Load API keys from environment (.env supported via python-dotenv)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root (src/../..) when developing, then current working directory.
_here = Path(__file__).resolve()
for _depth in (3, 4):
    if len(_here.parents) > _depth:
        _root = _here.parents[_depth]
        load_dotenv(_root / ".env", override=False)
        load_dotenv(_root / ".env.local", override=False)
load_dotenv(Path.cwd() / ".env", override=False)


def _flag(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def binance_keys() -> tuple[str | None, str | None]:
    return os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET")


def binance_testnet() -> bool:
    return _flag("BINANCE_TESTNET")


def okx_keys() -> tuple[str | None, str | None, str | None]:
    return (
        os.environ.get("OKX_API_KEY"),
        os.environ.get("OKX_API_SECRET"),
        os.environ.get("OKX_PASSPHRASE"),
    )


def okx_testnet() -> bool:
    return _flag("OKX_TESTNET")


def bybit_keys() -> tuple[str | None, str | None]:
    return os.environ.get("BYBIT_API_KEY"), os.environ.get("BYBIT_API_SECRET")


def bybit_testnet() -> bool:
    return _flag("BYBIT_TESTNET")
