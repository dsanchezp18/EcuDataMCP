# Fork notes (dsanchezp18/EcuDataMCP)

This fork hosts a public instance of EcuDataMCP on Oracle Cloud (Always Free).
It follows `DweskZ/EcuDataMCP` `main`; fork-only changes live in this file and
in `.github/workflows/sync-upstream.yml`, so upstream merges stay conflict-free.

## Hosted endpoint

The Oracle instance has been running since 2026-11-09 on an Always Free
Ampere A1 VM in Bogotá (`sa-bogota-1`):

- MCP: `https://129-38-110-203.sslip.io/mcp`
- Health: `https://129-38-110-203.sslip.io/health`

The hostname is an sslip.io name that resolves to the VM's IP. Clients connect
like this:

```json
{
  "mcpServers": {
    "ecuador-datos": {
      "type": "http",
      "url": "https://129-38-110-203.sslip.io/mcp"
    }
  }
}
```

The VM runs this fork's `main` as the systemd service `ecuador-mcp`, so it only
changes when someone updates it. To update it, on the VM:

```bash
cd ~/EcuDataMCP && git pull && uv sync --no-dev && sudo systemctl restart ecuador-mcp
```

Setup details (network rules, proxy, usage logs) are in `docs/DEPLOYMENT.md` on
the `deploy/oracle-bogota` branch, which is not merged into `main` yet.

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
