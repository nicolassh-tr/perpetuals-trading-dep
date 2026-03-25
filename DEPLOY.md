# Deploy this project (GitHub Pages)

Same flow as **[hl-vs-etoro](https://github.com/nicolassh-tr/hl-vs-etoro)**: static files are **built in GitHub Actions**, then published as the Pages site (not “serve raw files from `main`” unless you switch Source).

---

## GitHub Pages (SOL chart)

1. Code is on `main` with `.github/workflows/deploy-pages.yml`.
2. On GitHub: **Settings → Pages**.
3. **Build and deployment → Source:** **GitHub Actions** — not “Deploy from a branch”.
4. **Actions** → wait for **Deploy GitHub Pages** (green check), or **Run workflow** once.
5. Site URL (examples):  
   `https://<username>.github.io/perpetuals-trading-dep/` or  
   `https://<org>.github.io/perpetuals-trading-dep/` (organization repo)

### If `data.json` on the live URL looks like the small seed in git

That usually means Pages is still tied to **branch** deploy, so the **CI-built** `data.json` (fresh `generated_at`, full `series` from Binance in the runner) is not what gets served.

**Fix:** **Settings → Pages → Source → GitHub Actions**, then **Actions → Deploy GitHub Pages → Run workflow**. After that, `/data.json` should be larger and include a recent `generated_at` ISO timestamp.

The workflow runs on **push to `main`**, **`workflow_dispatch`**, and a **schedule** (4× daily UTC) so the chart refreshes without local builds.

### Private repository

**Company / Team / Enterprise** and **GitHub Pro** can use **GitHub Pages with private repos** — same steps as above (Source **GitHub Actions**, green **Deploy GitHub Pages** run). If **hl-vs-etoro** already works under your org, this repo should too once Pages is enabled and the workflow succeeds.

Only **GitHub Free** (personal, no Pro) blocks Pages on **private** repos; in that case make the repo public, upgrade, or use another host.

### Workflow failed (red “deploy” / exit code 1)

The **Node.js 20 deprecation** banner in the log is usually a **warning**, not the cause of failure. Open the **first step that shows a red X** — often **Build static site** (Binance/CCXT error) or **deploy-pages** (Pages API / permissions).

**Banner still says `checkout@v4` / `setup-python@v5` / `configure-pages@v5`?** That text matches an **older** workflow revision. On the run page, check which **commit** the workflow used (`main` should be recent). In the repo, **Deploy GitHub Pages** on current `main` uses `checkout@v6`, `setup-python@v6`, and **pinned SHAs** for configure/deploy-pages (Node 24). You may still see a separate notice from **`upload-pages-artifact`** (it bundles an `upload-artifact` build that still declares Node 20 until GitHub ships an update).

- **Environment `github-pages` waiting for approval:** **Settings → Environments → github-pages** — approve the deployment or relax protection rules.
- **Binance HTTP 451 in CI:** Binance often blocks **GitHub-hosted** runner IPs (restricted location). The **Deploy GitHub Pages** workflow then **falls back** to the committed `sol-perp/data.json` so the site still publishes. Refresh data on a machine that can reach Binance (`python scripts/build_sol_perp_chart_data.py`) and push, or use a self-hosted Actions runner in an allowed region if you need automated fresh data.

---

## Optional: commit `data.json` back to `main`

To refresh the copy **in the repository** (e.g. for Databricks Repos), use **Actions → SOL perpetual chart data → Run workflow** (`sol-perp-data.yml`). That is separate from what visitors see on Pages when Source is **GitHub Actions**.
