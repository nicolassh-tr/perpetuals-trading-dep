#!/usr/bin/env python3
"""
Fetch public SOL data from Binance → sol-perp/data.json (no API keys):

- USDⓈ-M perpetual: hourly close
- Spot SOL/USDT: hourly close (aligned timestamps)
- Perpetual funding rate: forward-filled onto each hour (Binance settles every 8h;
  each bar carries the rate in effect after the latest settlement at or before that bar).

Note: GitHub-hosted Actions often get HTTP 451 from Binance (geo). The Pages workflow
falls back to the existing committed data.json when this script fails in CI.

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

SYMBOL_PERP = "SOL/USDT:USDT"
SYMBOL_SPOT = "SOL/USDT"
TIMEFRAME = "1h"
LIMIT = 168  # 7 days hourly
# Extra lookback so the first hourly bars have a funding rate before series start.
FUNDING_LOOKBACK_MS = 30 * 24 * 60 * 60 * 1000
FUNDING_FETCH_LIMIT = 500


def _maybe_insecure_tls(ex: ccxt.Exchange) -> None:
    if os.environ.get("PERP_TRADING_TLS_INSECURE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        ex.session.verify = False  # noqa: S501 — opt-in only for broken corporate TLS


def _forward_funding(
    bar_timestamps_ms: list[int], funding_rows: list[dict]
) -> list[float | None]:
    """For each bar open time, last fundingRate whose funding timestamp <= bar time."""
    events = sorted(
        (int(r["timestamp"]), float(r["fundingRate"])) for r in funding_rows if r.get("timestamp") is not None
    )
    if not events:
        return [None] * len(bar_timestamps_ms)

    out: list[float | None] = []
    idx = 0
    current: float | None = None
    for ts in bar_timestamps_ms:
        while idx < len(events) and events[idx][0] <= ts:
            current = events[idx][1]
            idx += 1
        out.append(current)
    return out


def main() -> int:
    ex_usdm = ccxt.binanceusdm({"enableRateLimit": True})
    ex_spot = ccxt.binance({"enableRateLimit": True})
    _maybe_insecure_tls(ex_usdm)
    _maybe_insecure_tls(ex_spot)

    ohlcv_perp = ex_usdm.fetch_ohlcv(SYMBOL_PERP, TIMEFRAME, limit=LIMIT)
    ohlcv_spot = ex_spot.fetch_ohlcv(SYMBOL_SPOT, TIMEFRAME, limit=LIMIT)

    spot_close: dict[int, float] = {int(row[0]): float(row[4]) for row in ohlcv_spot}

    first_ts = int(ohlcv_perp[0][0])
    funding_since = first_ts - FUNDING_LOOKBACK_MS
    funding_raw = ex_usdm.fetch_funding_rate_history(
        SYMBOL_PERP, since=funding_since, limit=FUNDING_FETCH_LIMIT
    )

    bar_ts = [int(row[0]) for row in ohlcv_perp]
    funding_per_bar = _forward_funding(bar_ts, funding_raw)

    series = []
    for row, fr in zip(ohlcv_perp, funding_per_bar, strict=True):
        ts, _o, _h, _l, c, _v = row
        ts_i = int(ts)
        spot_c = spot_close.get(ts_i)
        if spot_c is None:
            raise SystemExit(f"Missing spot candle for perp bar ts={ts_i} — alignment failed")
        series.append(
            {
                "ts": ts_i,
                "perp": float(c),
                "spot": spot_c,
                "funding_rate": fr,
            }
        )

    last_fr_row = max(funding_raw, key=lambda r: int(r["timestamp"])) if funding_raw else None

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "symbol_perp": SYMBOL_PERP,
        "symbol_spot": SYMBOL_SPOT,
        "timeframe": TIMEFRAME,
        "venues": {"perp": "binance_usdm", "spot": "binance"},
        "funding_interval_note": "Binance USDT-M funding settles every 8h; each bar uses the rate after the latest settlement at or before that bar open.",
        "latest_funding_rate": float(last_fr_row["fundingRate"]) if last_fr_row else None,
        "latest_funding_time": last_fr_row.get("datetime") if last_fr_row else None,
        "count": len(series),
        "series": series,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUT} ({len(series)} rows; perp+spot+funding; "
        f"latest funding {payload['latest_funding_rate']!r} @ {payload['latest_funding_time']!r})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
