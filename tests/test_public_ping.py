"""Public API smoke tests (no API keys). Requires network."""

import pytest
import ccxt

from perpetuals_trading_dep.exchanges.clients import create_public_exchange


@pytest.mark.parametrize("name", ["binance", "okx", "bybit"])
def test_fetch_time_public(name: str) -> None:
    try:
        ex = create_public_exchange(name)  # type: ignore[arg-type]
        t = ex.fetch_time()
    except (ccxt.NetworkError, ccxt.ExchangeError, OSError) as e:
        pytest.skip(f"{name}: {e}")
    assert isinstance(t, int)
    assert t > 1_000_000_000_000  # ms since epoch, rough sanity
