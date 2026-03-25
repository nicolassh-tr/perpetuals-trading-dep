# Perpetuals Trading Dep

Workspace for perpetual futures / perpetuals trading tooling, analysis, and automation.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Layout

- `src/` — application and library code
- `tests/` — tests (add as needed)
- `scripts/push-to-github.ps1` — helper to add `origin` and push `main` (after you create an empty repo on GitHub)

## Push to GitHub

Create a new **empty** repository on GitHub (no README/license). Then from this folder:

```powershell
.\scripts\push-to-github.ps1 https://github.com/YOUR_USERNAME/perpetuals-trading-dep.git
```

Or manually: `git remote add origin <url>` then `git push -u origin main`.
