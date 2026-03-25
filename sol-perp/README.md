# SOL perpetual timeseries (Binance)

- **`index.html`** — Chart.js chart (loads **`data.json`** next to it).
- **`data.json`** — Built by `../scripts/build_sol_perp_chart_data.py` (no API keys): **Binance USDⓈ-M** hourly perp close, **spot** SOL/USDT hourly close (aligned), and **funding rate** forward-filled per bar (8h settlements).

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

**Live site (after Pages is enabled):**  
**https://nicolassh-tr.github.io/perpetuals-trading-dep/**

One-time setup: repo **Settings → Pages → Build and deployment → Source: GitHub Actions** (same as [hl-vs-etoro](https://github.com/nicolassh-tr/hl-vs-etoro)).  
Workflow: `../.github/workflows/deploy-pages.yml` — builds fresh `data.json` in CI, copies `index.html` + `data.json` to `_site`, deploys on every push to `main`, schedule, or **Run workflow**. See **`../DEPLOY.md`**.
