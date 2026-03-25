#!/usr/bin/env python3
"""
Fetch public SOL USDT perpetual OHLCV from Binance (USDT-M) → sol-perp/data.json
(no API keys).

Optional: PERP_TRADING_TLS_INSECURE=1 to disable TLS verify (dev / MITM proxies only).

Usage (from repo root):
  python scripts/build_sol_perp_chart_data.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import ccxt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sol-perp" / "data.json"

SYMBOL = "SOL/USDT:USDT"
TIMEFRAME = "1h"
LIMIT = 168  # 7 days hourly
VENUE = "binance"


def _maybe_insecure_tls(ex: ccxt.Exchange) -> None:
    if os.environ.get("PERP_TRADING_TLS_INSECURE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        ex.session.verify = False  # noqa: S501 — opt-in only for broken corporate TLS


def main() -> int:
    ex = ccxt.binanceusdm({"enableRateLimit": True})
    _maybe_insecure_tls(ex)
    ohlcv = ex.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=LIMIT)

    series = []
    for row in ohlcv:
        ts, _o, _h, _l, c, _v = row
        series.append({"ts": int(ts), VENUE: float(c)})

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "venues": [VENUE],
        "count": len(series),
        "series": series,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(series)} rows, Binance USDT-M only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
