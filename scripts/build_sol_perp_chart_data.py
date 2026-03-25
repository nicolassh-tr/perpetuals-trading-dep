#!/usr/bin/env python3
"""
Fetch public SOL USDT perpetual OHLCV from Binance, OKX, Bybit → sol-perp/data.json
(no API keys). Continues if one venue fails (e.g. corporate SSL on OKX).

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
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sol-perp" / "data.json"

SYMBOL = "SOL/USDT:USDT"
TIMEFRAME = "1h"
LIMIT = 168  # 7 days hourly
VENUES = ["binance", "okx", "bybit"]


def _maybe_insecure_tls(ex: ccxt.Exchange) -> None:
    if os.environ.get("PERP_TRADING_TLS_INSECURE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        ex.session.verify = False  # noqa: S501 — opt-in only for broken corporate TLS


def _exchange(name: str) -> ccxt.Exchange:
    if name == "binance":
        ex = ccxt.binanceusdm({"enableRateLimit": True})
    elif name == "okx":
        ex = ccxt.okx(
            {"enableRateLimit": True, "options": {"defaultType": "swap"}}
        )
    elif name == "bybit":
        ex = ccxt.bybit(
            {"enableRateLimit": True, "options": {"defaultType": "swap"}}
        )
    else:
        raise ValueError(name)
    _maybe_insecure_tls(ex)
    return ex


def fetch_close_series(name: str) -> pd.DataFrame:
    ex = _exchange(name)
    ohlcv = ex.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(ohlcv, columns=["ts", "o", "h", "l", "c", "v"])
    return df[["ts", "c"]].rename(columns={"c": name})


def main() -> int:
    frames: dict[str, pd.DataFrame] = {}
    errors: dict[str, str] = {}

    for n in VENUES:
        try:
            frames[n] = fetch_close_series(n)
        except Exception as e:  # noqa: BLE001
            errors[n] = str(e)
            print(f"WARN {n}: {e}", file=sys.stderr)

    if not frames:
        print("ERROR: no exchange returned data", file=sys.stderr)
        return 1

    merged = list(frames.values())[0]
    for name in list(frames.keys())[1:]:
        merged = pd.merge(merged, frames[name], on="ts", how="inner")
    merged = merged.sort_values("ts").dropna()

    series = []
    for _, row in merged.iterrows():
        pt: dict = {"ts": int(row["ts"])}
        for n in frames.keys():
            pt[n] = float(row[n])
        series.append(pt)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "venues": list(frames.keys()),
        "errors": errors,
        "count": len(series),
        "series": series,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(series)} rows, venues={payload['venues']})")
    if errors:
        print("Some venues skipped — chart uses remaining inner-joined series.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
