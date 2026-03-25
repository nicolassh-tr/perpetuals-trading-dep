"""
CCXT clients for perpetual / swap markets: Binance USDT-M, OKX swap, Bybit linear.

Requires API keys in environment (see .env.example). Uses ccxt: https://github.com/ccxt/ccxt
"""

from __future__ import annotations

import os
from typing import Literal

import ccxt

from perpetuals_trading_dep.exchanges import config

ExchangeName = Literal["binance", "okx", "bybit"]


def create_exchange(
    name: ExchangeName,
    *,
    testnet: bool | None = None,
    **ccxt_options: object,
) -> ccxt.Exchange:
    """
    Build a configured ccxt exchange instance for perpetual-style markets.

    - **binance**: USDT-margined futures (`binanceusdm`)
    - **okx**: swap (perpetual) — `defaultType: swap`
    - **bybit**: linear USDT perpetuals — `defaultType: swap`

    Extra kwargs are merged into the ccxt constructor (e.g. `timeout`, `enableRateLimit` is True by default).
    """
    common = {
        "enableRateLimit": True,
        "options": {},
    }
    common.update(ccxt_options)  # type: ignore[arg-type]

    if name == "binance":
        key, secret = config.binance_keys()
        if not key or not secret:
            raise ValueError(
                "Set BINANCE_API_KEY and BINANCE_API_SECRET (see .env.example)."
            )
        use_testnet = config.binance_testnet() if testnet is None else testnet
        ex = ccxt.binanceusdm(
            {
                **common,
                "apiKey": key,
                "secret": secret,
                "options": {**common.get("options", {}), "defaultType": "swap"},
            }
        )
        if use_testnet:
            ex.set_sandbox_mode(True)
        return ex

    if name == "okx":
        key, secret, passphrase = config.okx_keys()
        if not key or not secret or not passphrase:
            raise ValueError(
                "Set OKX_API_KEY, OKX_API_SECRET, and OKX_PASSPHRASE (see .env.example)."
            )
        use_testnet = config.okx_testnet() if testnet is None else testnet
        ex = ccxt.okx(
            {
                **common,
                "apiKey": key,
                "secret": secret,
                "password": passphrase,
                "options": {**common.get("options", {}), "defaultType": "swap"},
            }
        )
        if use_testnet:
            ex.set_sandbox_mode(True)
        return ex

    if name == "bybit":
        key, secret = config.bybit_keys()
        if not key or not secret:
            raise ValueError(
                "Set BYBIT_API_KEY and BYBIT_API_SECRET (see .env.example)."
            )
        use_testnet = config.bybit_testnet() if testnet is None else testnet
        ex = ccxt.bybit(
            {
                **common,
                "apiKey": key,
                "secret": secret,
                "options": {**common.get("options", {}), "defaultType": "swap"},
            }
        )
        if use_testnet:
            ex.set_sandbox_mode(True)
        return ex

    raise ValueError(f"Unknown exchange: {name}")


def create_public_exchange(name: ExchangeName) -> ccxt.Exchange:
    """No API keys — public endpoints only (tickers, order book, time). Useful for connectivity checks."""
    if name == "binance":
        return ccxt.binanceusdm({"enableRateLimit": True})
    if name == "okx":
        return ccxt.okx({"enableRateLimit": True, "options": {"defaultType": "swap"}})
    if name == "bybit":
        return ccxt.bybit({"enableRateLimit": True, "options": {"defaultType": "swap"}})
    raise ValueError(f"Unknown exchange: {name}")


def verify_connection(exchange: ccxt.Exchange, *, authenticated: bool = True) -> dict:
    """
    Lightweight health check: server time (+ fetch_balance if keys present / authenticated).

    Returns a small dict suitable for logging.
    """
    out: dict = {"id": exchange.id, "name": exchange.name}
    out["time_ms"] = exchange.fetch_time()
    if authenticated and getattr(exchange, "apiKey", None):
        try:
            out["balance"] = exchange.fetch_balance()
        except Exception as e:  # noqa: BLE001
            out["balance_error"] = str(e)
    return out
