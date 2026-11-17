# Fork notes (dsanchezp18/EcuDataMCP)

This fork hosts a public instance of EcuDataMCP on Oracle Cloud (Always Free).
It follows `DweskZ/EcuDataMCP` `main`; fork-only changes live in this file and
in `.github/workflows/sync-upstream.yml`, so upstream merges stay conflict-free.

## Hosted endpoint

The Oracle instance is not deployed yet, so there is no public URL. Add the
MCP and health URLs here once it is running. Clients will connect like this:

```json
{
  "mcpServers": {
    "ecuador-datos": {
      "type": "http",
      "url": "https://<oracle-host>/mcp"
    }
  }
}
```

## Upstream sync

Nothing syncs this fork automatically. `sync-upstream.yml` only runs when
triggered by hand ("Run workflow" in the Actions tab) and calls GitHub's
merge-upstream API. When an upstream change touches `.github/workflows/*`, the
default `GITHUB_TOKEN` is refused (HTTP 422) and the run fails, so no
`SYNC_TOKEN` secret is configured and none is needed. Sync from your own
machine instead:

```bash
git fetch origin && git merge origin/main && git push fork HEAD:main
```

This fork's `main` has commits upstream does not, so `gh repo sync` (a
fast-forward) fails here; merge instead, as above, or use "Sync fork > Update
branch" on GitHub.

## Disabled workflows

`Smoke test` (daily) and `Refresh stored answers` (Mondays) are disabled on this
fork; they run on `DweskZ/EcuDataMCP`. To turn one back on, use the Actions tab
or `gh workflow enable "<name>" --repo dsanchezp18/EcuDataMCP`.
