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

## Repository layout

| Path | Purpose |
|------|--------|
| `src/perpetuals_trading_dep/` | Python package |
| `tests/` | Tests |
| `scripts/` | Helper scripts (e.g. Git push helper) |
| `.github/workflows/ci.yml` | CI on `main` |

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
