# SOL perpetual timeseries (Binance)

- **`index.html`** — Chart.js chart (loads **`data.json`** next to it).
- **`data.json`** — Built by `../scripts/build_sol_perp_chart_data.py` (public OHLCV from **Binance USDT-M** only, no API keys).

Regenerate data:

```powershell
cd ..
python scripts/build_sol_perp_chart_data.py
```

If TLS fails on your network (corporate proxy), you can try **once** (insecure — dev only):

```powershell
$env:PERP_TRADING_TLS_INSECURE="1"
python scripts/build_sol_perp_chart_data.py
```

**GitHub Pages:** enable Pages on branch `main`, folder **`/sol-perp`**.
