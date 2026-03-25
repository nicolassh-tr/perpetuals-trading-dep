# Deploy this project (GitHub Pages)

Same flow as **[hl-vs-etoro](https://github.com/nicolassh-tr/hl-vs-etoro)**: static files are **built in GitHub Actions**, then published as the Pages site (not “serve raw files from `main`” unless you switch Source).

---

## GitHub Pages (SOL chart)

1. Code is on `main` with `.github/workflows/deploy-pages.yml`.
2. On GitHub: **Settings → Pages**.
3. **Build and deployment → Source:** **GitHub Actions** — not “Deploy from a branch”.
4. **Actions** → wait for **Deploy GitHub Pages** (green check), or **Run workflow** once.
5. Site URL (example):  
   `https://<username>.github.io/perpetuals-trading-dep/`

### If `data.json` on the live URL looks like the small seed in git

That usually means Pages is still tied to **branch** deploy, so the **CI-built** `data.json` (fresh `generated_at`, full `series` from Binance in the runner) is not what gets served.

**Fix:** **Settings → Pages → Source → GitHub Actions**, then **Actions → Deploy GitHub Pages → Run workflow**. After that, `/data.json` should be larger and include a recent `generated_at` ISO timestamp.

The workflow runs on **push to `main`**, **`workflow_dispatch`**, and a **schedule** (4× daily UTC) so the chart refreshes without local builds.

### Private repository

On a **free** personal GitHub account, **GitHub Pages does not publish private repos**. Use a **public** repo, **GitHub Pro**, or host `sol-perp/` elsewhere (e.g. Cloudflare Pages, Netlify).

---

## Optional: commit `data.json` back to `main`

To refresh the copy **in the repository** (e.g. for Databricks Repos), use **Actions → SOL perpetual chart data → Run workflow** (`sol-perp-data.yml`). That is separate from what visitors see on Pages when Source is **GitHub Actions**.
