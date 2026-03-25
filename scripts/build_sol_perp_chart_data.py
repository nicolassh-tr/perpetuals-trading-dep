#!/usr/bin/env python3
"""
Fetch public Binance spot + USDⓈ-M perp data → sol-perp/data.json (no API keys).

- Assets: BTC, ETH, XRP, ADA, SOL (USDT pairs; this order in JSON)
- 1-minute OHLCV, **2 calendar days** window (paginated past 1000-candle API limit)
- Funding forward-filled per bar; per-asset overnight bps heuristic

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
from typing import Any

import ccxt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sol-perp" / "data.json"

TIMEFRAME = "1m"
WINDOW_DAYS = 2
BATCH_LIMIT = 1000
# (id, perp symbol, spot symbol)
ASSETS: list[tuple[str, str, str]] = [
    ("BTC", "BTC/USDT:USDT", "BTC/USDT"),
    ("ETH", "ETH/USDT:USDT", "ETH/USDT"),
    ("XRP", "XRP/USDT:USDT", "XRP/USDT"),
    ("ADA", "ADA/USDT:USDT", "ADA/USDT"),
    ("SOL", "SOL/USDT:USDT", "SOL/USDT"),
]

FUNDING_LOOKBACK_MS = 30 * 24 * 60 * 60 * 1000
FUNDING_FETCH_LIMIT = 500


def _maybe_insecure_tls(ex: ccxt.Exchange) -> None:
    if os.environ.get("PERP_TRADING_TLS_INSECURE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        ex.session.verify = False  # noqa: S501 — opt-in only for broken corporate TLS


def _fetch_ohlcv_window(
    ex: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    start_ms: int,
    end_ms: int,
) -> list[list[Any]]:
    """Oldest-first candles with open time in [start_ms, end_ms]."""
    tf_sec = ex.parse_timeframe(timeframe)
    tf_ms = int(tf_sec * 1000)
    by_ts: dict[int, list[Any]] = {}
    cursor = start_ms
    for _ in range(32):
        batch = ex.fetch_ohlcv(symbol, timeframe, since=cursor, limit=BATCH_LIMIT)
        if not batch:
            break
        for row in batch:
            ts = int(row[0])
            if start_ms <= ts <= end_ms:
                by_ts[ts] = row
        last_ts = int(batch[-1][0])
        cursor = last_ts + tf_ms
        if last_ts >= end_ms or len(batch) < BATCH_LIMIT:
            break
    return [by_ts[k] for k in sorted(by_ts.keys())]


def _forward_funding(
    bar_timestamps_ms: list[int], funding_rows: list[dict]
) -> list[float | None]:
    events = sorted(
        (int(r["timestamp"]), float(r["fundingRate"]))
        for r in funding_rows
        if r.get("timestamp") is not None
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


def _build_asset(
    ex_usdm: ccxt.Exchange,
    ex_spot: ccxt.Exchange,
    asset_id: str,
    symbol_perp: str,
    symbol_spot: str,
    start_ms: int,
    end_ms: int,
) -> dict[str, Any]:
    ohlcv_perp = _fetch_ohlcv_window(ex_usdm, symbol_perp, TIMEFRAME, start_ms, end_ms)
    ohlcv_spot = _fetch_ohlcv_window(ex_spot, symbol_spot, TIMEFRAME, start_ms, end_ms)

    if not ohlcv_perp:
        raise SystemExit(f"{asset_id}: no perp OHLCV in window")

    spot_close = {int(row[0]): float(row[4]) for row in ohlcv_spot}

    first_ts = int(ohlcv_perp[0][0])
    funding_since = first_ts - FUNDING_LOOKBACK_MS
    funding_raw = ex_usdm.fetch_funding_rate_history(
        symbol_perp, since=funding_since, limit=FUNDING_FETCH_LIMIT
    )

    bar_ts = [int(row[0]) for row in ohlcv_perp]
    funding_per_bar = _forward_funding(bar_ts, funding_raw)

    series = []
    for row, fr in zip(ohlcv_perp, funding_per_bar, strict=True):
        ts_i = int(row[0])
        spot_c = spot_close.get(ts_i)
        if spot_c is None:
            raise SystemExit(f"{asset_id}: missing spot candle for perp ts={ts_i}")
        series.append(
            {
                "ts": ts_i,
                "perp": float(row[4]),
                "spot": spot_c,
                "funding_rate": fr,
            }
        )

    last_fr_row = max(funding_raw, key=lambda r: int(r["timestamp"])) if funding_raw else None

    fr_samples = [float(r["funding_rate"]) for r in series if r.get("funding_rate") is not None]
    avg_funding_rate_8h = sum(fr_samples) / len(fr_samples) if fr_samples else None
    binance_daily_funding_decimal_approx = (
        avg_funding_rate_8h * 3 if avg_funding_rate_8h is not None else None
    )
    etoro_overnight_fee_bps_approx = (
        binance_daily_funding_decimal_approx * 10_000
        if binance_daily_funding_decimal_approx is not None
        else None
    )

    return {
        "id": asset_id,
        "symbol_perp": symbol_perp,
        "symbol_spot": symbol_spot,
        "count": len(series),
        "series": series,
        "latest_funding_rate": float(last_fr_row["fundingRate"]) if last_fr_row else None,
        "latest_funding_time": last_fr_row.get("datetime") if last_fr_row else None,
        "avg_funding_rate_8h": avg_funding_rate_8h,
        "binance_daily_funding_decimal_approx": binance_daily_funding_decimal_approx,
        "etoro_overnight_fee_bps_approx": etoro_overnight_fee_bps_approx,
    }


def main() -> int:
    ex_usdm = ccxt.binanceusdm({"enableRateLimit": True})
    ex_spot = ccxt.binance({"enableRateLimit": True})
    _maybe_insecure_tls(ex_usdm)
    _maybe_insecure_tls(ex_spot)

    end_ms = ex_usdm.milliseconds()
    start_ms = end_ms - WINDOW_DAYS * 24 * 60 * 60 * 1000

    assets_out: list[dict[str, Any]] = []
    for aid, sym_p, sym_s in ASSETS:
        block = _build_asset(ex_usdm, ex_spot, aid, sym_p, sym_s, start_ms, end_ms)
        assets_out.append(block)
        print(
            f"  {aid}: {block['count']} bars; "
            f"bps~ {block['etoro_overnight_fee_bps_approx']!r}"
        )

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "timeframe": TIMEFRAME,
        "window_days": WINDOW_DAYS,
        "venues": {"perp": "binance_usdm", "spot": "binance"},
        "funding_interval_note": (
            "Binance USDT-M funding every 8h; each bar uses the rate after the latest settlement "
            "at or before that bar open."
        ),
        "etoro_overnight_fee_bps_note": (
            "Illustrative only: mean Binance 8h funding over this chart window × 3 (intervals/day), "
            "as bps of notional per day — not eToro pricing, schedule, or official overnight fee."
        ),
        "assets": assets_out,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(assets_out)} assets, {WINDOW_DAYS}d window, {TIMEFRAME})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
