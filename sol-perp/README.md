# Multi-asset spot vs perp (Binance)

- **`index.html`** — **Light green** page, **eToro** wordmark (`etoro-logo.svg`), **five stacked** charts in order **BTC → ETH → XRP → ADA → SOL** (loads **`data.json`**).
- **`etoro-logo.svg`** — Simple green **eToro** wordmark for the header (replace with official artwork if required by brand).
- **`data.json`** — Built by `../scripts/build_sol_perp_chart_data.py` (no API keys): **BTC, ETH, XRP, ADA, SOL** — **USDⓈ-M** + **spot** **1m** closes, **2 days** window (paginated OHLCV), **funding** per bar, per-asset **overnight bps** heuristic (see disclaimer in JSON).

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
