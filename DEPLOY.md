# Deploy / CI

This repo is primarily **Python libraries and scripts** for perpetuals trading work—not a static website like [hl-vs-etoro](https://github.com/nicolassh-tr/hl-vs-etoro).

## GitHub Actions

On every push to `main`, **CI** runs (see `.github/workflows/ci.yml`): install dependencies and smoke-import the package.

## Future options

- Publish docs to **GitHub Pages** from a `docs/` build.
- Add **Databricks** notebooks in-repo and sync via **Repos** (see [DATABRICKS_SYNC.md](./DATABRICKS_SYNC.md)).
