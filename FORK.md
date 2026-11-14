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

`sync-upstream.yml` calls GitHub's merge-upstream API daily. When an upstream
change touches `.github/workflows/*`, the default `GITHUB_TOKEN` is refused
(HTTP 422), so the repository needs a `SYNC_TOKEN` secret: a personal access
token with the `workflow` scope (classic) or Contents + Workflows write
(fine-grained). Without it, sync the fork by hand:

```bash
git fetch origin && git merge origin/main && git push fork HEAD:main
```
