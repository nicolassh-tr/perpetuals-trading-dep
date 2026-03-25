# Perpetuals Trading Dep

Workspace for **perpetual futures / perpetuals** trading tooling, analysis, and automation.

Related dashboard repo (Hyperliquid vs eToro): **[hl-vs-etoro](https://github.com/nicolassh-tr/hl-vs-etoro)**.

---

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

(Optional: `pip install -r requirements.txt` for extra dependencies.)

Package lives under `src/perpetuals_trading_dep/`.

---

## Exchange APIs (Binance, OKX, Bybit)

Uses **[CCXT](https://github.com/ccxt/ccxt)** for USDT-style **perpetuals / swap** markets:

| Exchange | CCXT id | Notes |
|----------|---------|--------|
| Binance Futures | `binanceusdm` | Keys from **USDⓈ-M Futures** on [Binance API management](https://www.binance.com/en/my/settings/api-management) |
| OKX | `okx` | API key + secret + **passphrase** |
| Bybit | `bybit` | Linear **USDT** perpetuals |

1. Copy **`.env.example`** → **`.env`** and fill keys (never commit `.env`).
2. **Public ping** (no keys, checks server time):

```powershell
python -m perpetuals_trading_dep ping binance
python -m perpetuals_trading_dep ping okx
python -m perpetuals_trading_dep ping bybit
```

3. **Authenticated** ping (loads balances if permissions allow):

```powershell
python -m perpetuals_trading_dep ping binance --auth
```

Optional: set `BINANCE_TESTNET=true`, `OKX_TESTNET=true`, or `BYBIT_TESTNET=true` for sandbox endpoints.

### SOL perpetual chart (HTML)

Static page: **eToro-branded** header (logo SVG), **light green** layout, **five stacked charts** (**BTC, ETH, XRP, ADA, SOL**) — **spot** vs **USDⓈ-M perpetual** **1-minute** closes on **Binance** (**2 days**), **funding** on the right axis.

```powershell
python scripts/build_sol_perp_chart_data.py
# Open sol-perp/index.html in a browser (needs data.json alongside).
```

See **[sol-perp/README.md](./sol-perp/README.md)**.

**Live chart:** same **GitHub Pages + Actions** setup as [hl-vs-etoro](https://github.com/nicolassh-tr/hl-vs-etoro) — see **[DEPLOY.md](./DEPLOY.md)**. Example URL:  
**https://nicolassh-tr.github.io/perpetuals-trading-dep/**

---

## Repository layout

| Path | Purpose |
|------|--------|
| `src/perpetuals_trading_dep/` | Python package |
| `tests/` | Tests |
| `sol-perp/` | HTML chart + `data.json` for SOL perpetual (Binance USDT-M) |
| `scripts/` | Helper scripts (e.g. Git push helper, SOL chart data) |
| `.github/workflows/ci.yml` | CI on `main` |
| `.github/workflows/deploy-pages.yml` | GitHub Pages (CI-built SOL chart → `_site`) |

---

## GitHub + Databricks

After you push to GitHub, pull in **Databricks Repos** (or deploy other projects with the asset bundle). See **[DATABRICKS_SYNC.md](./DATABRICKS_SYNC.md)**.

---

## CI / deploy notes

See **[DEPLOY.md](./DEPLOY.md)**.

---

## Push this repo to GitHub

If the remote repo does not exist yet:

1. Create a new **public** repository on GitHub named **`perpetuals-trading-dep`** under **`nicolassh-tr`**, with **no** README/license (empty repo).
2. From this folder:

```powershell
git remote add origin https://github.com/nicolassh-tr/perpetuals-trading-dep.git
git push -u origin main
```

Or use **`scripts/push-to-github.ps1`** with your repo URL.
