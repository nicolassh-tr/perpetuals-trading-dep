"""CLI: ``python -m perpetuals_trading_dep ping binance`` (public) or ``--auth`` with API keys."""

from __future__ import annotations

import argparse
import json
import sys

from perpetuals_trading_dep.exchanges.clients import (
    create_exchange,
    create_public_exchange,
    verify_connection,
)


def _cmd_ping(args: argparse.Namespace) -> int:
    name = args.exchange
    if args.auth:
        ex = create_exchange(name)  # type: ignore[arg-type]
        data = verify_connection(ex, authenticated=True)
    else:
        ex = create_public_exchange(name)  # type: ignore[arg-type]
        data = verify_connection(ex, authenticated=False)
    print(json.dumps(data, indent=2, default=str))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="perpetuals_trading_dep")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ping = sub.add_parser("ping", help="Connectivity check (public time, or --auth + balance)")
    p_ping.add_argument("exchange", choices=["binance", "okx", "bybit"])
    p_ping.add_argument(
        "--auth",
        action="store_true",
        help="Use API keys from environment (see .env.example)",
    )
    p_ping.set_defaults(func=_cmd_ping)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
