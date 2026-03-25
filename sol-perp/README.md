# SOL perpetual timeseries (3 venues)

- **`index.html`** — Chart.js chart (loads **`data.json`** next to it).
- **`data.json`** — Built by `../scripts/build_sol_perp_chart_data.py` (public OHLCV, no API keys).

Regenerate data:

```powershell
cd ..
python scripts/build_sol_perp_chart_data.py
```

If **OKX/Bybit** fail on your network (SSL / firewall), only working venues are used. For strict corporate TLS, you can try **once** (insecure — dev only):

```powershell
$env:PERP_TRADING_TLS_INSECURE="1"
python scripts/build_sol_perp_chart_data.py
```

**GitHub Pages:** enable Pages on branch `main`, folder **`/sol-perp`**, then open  
`https://<user>.github.io/perpetuals-trading-dep/` (if the repo is named `perpetuals-trading-dep`).
