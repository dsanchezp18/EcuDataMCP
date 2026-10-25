# Fork notes (dsanchezp18/EcuDataMCP)

This fork hosts a public instance of EcuDataMCP on Render. It follows
`DweskZ/EcuDataMCP` `main`; fork-only changes live in this file and in
`.github/workflows/sync-upstream.yml`, so upstream merges stay conflict-free.

## Hosted endpoint

- MCP: `https://ecuador-mcp-lb0s.onrender.com/mcp`
- Health: `https://ecuador-mcp-lb0s.onrender.com/health`

Render service `ecuador-mcp` in the `ecuador-mcp` workspace, deploying this
fork's `main` on every commit. It replaced `https://ecuador-mcp.onrender.com`
(service in "My Workspace"), which should no longer be used.

Free instance: the first request after a period of inactivity can take about
a minute while the service wakes up.

```json
{
  "mcpServers": {
    "ecuador-datos": {
      "type": "http",
      "url": "https://ecuador-mcp-lb0s.onrender.com/mcp"
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
