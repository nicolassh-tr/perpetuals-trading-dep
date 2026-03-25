# Databricks ↔ GitHub workflow

**Source of truth:** this repo on GitHub (`main`). Commit and push from your PC.

## After `git push`

### Databricks Repos

1. **Workspace** → **Repos** → **Add repo** → paste `https://github.com/nicolassh-tr/perpetuals-trading-dep.git` (or your fork URL).
2. Use **Pull** whenever you want the workspace copy to match `main`.

### Related: `Nicolas_Cursor_Project` bundle

If you also deploy notebooks or jobs from `Nicolas_Cursor_Project` on the same machine:

```powershell
cd C:\Users\nicolassh\Desktop\Nicolas_Cursor_Project
databricks bundle deploy -t dev
```

That syncs the **bundle** to Databricks; it is separate from this repo unless you copy files between them.
