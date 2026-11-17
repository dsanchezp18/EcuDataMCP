# Instancia pública en Oracle Cloud (Bogotá)

Notas de este fork (`dsanchezp18/EcuDataMCP`); el repositorio de origen no las
incluye. Salen de `docs/DEPLOYMENT.md` de la rama `deploy/oracle-bogota` (commits
`0aef351` y `2055803`, 2026-11-09), tal cual, sin cambios de contenido. Esa rama
también cambia `README.md` y `CHANGELOG.md`, archivos compartidos con el origen, así
que no se fusiona: este archivo es solo del fork y no choca con las fusiones del
origen.

La instancia pública corre desde el 2026-11-09 en una VM de Oracle Cloud
Always Free en Bogotá (`sa-bogota-1`): `https://129-38-110-203.sslip.io/mcp`
(`/health` para el estado). Está siempre encendida, sin arranque en frío, y
el disco guarda la base de financieros de Supercías entre reinicios.

- **VM:** Ampere A1 (ARM), 2 OCPU, 12 GB de RAM, 100 GB de disco, Ubuntu
  24.04. Usa cerca de 1 GB de RAM con el servidor en marcha.
- **Servicio:** `systemd` (`ecuador-mcp.service`) corre `main.py` desde un
  clon de la rama `main` del fork `dsanchezp18/EcuDataMCP` con
  `MCP_TRANSPORT=http`, `MCP_HOST=0.0.0.0`, `MCP_PORT=8000`,
  `MCP_PROFILE=public`, `MCP_REQUIRE_AUTH=0`, `MCP_RATE_LIMIT_REQUESTS=120`
  por 60 s, `FORWARDED_ALLOW_IPS=127.0.0.1` y `ECUADOR_MCP_USAGE_LOG=1`. Con un host distinto de
  loopback el SDK no aplica su filtro de `Host` (con `127.0.0.1` responde
  421 detrás del proxy).
- **Proxy:** Caddy con certificado de Let's Encrypt para el nombre de
  [sslip.io](https://sslip.io), que resuelve a la IP de la VM. Solo reenvía
  `/mcp`, `/health` y `/usage`; el resto responde 404. Para pasar a un dominio propio
  basta un registro A a `129.38.110.203` y cambiar el nombre en
  `/etc/caddy/Caddyfile`.
- **Red:** el firewall de la VCN y el `iptables` de la VM abren solo 22, 80 y
  443. El puerto 8000 no es accesible desde fuera.
- **Sin token:** los conectores personalizados de Claude y ChatGPT solo
  aceptan OAuth o ninguna autenticación, no un token Bearer fijo. El servidor
  solo lee datos públicos; el límite por IP queda activo.
- **Uso:** `https://129-38-110-203.sslip.io/usage` da llamadas, errores y
  latencia por herramienta desde el último reinicio. Cada llamada se añade
  además a `~/EcuDataMCP/data/usage.jsonl` (herramienta, resultado y
  duración, nunca argumentos), que sobrevive a reinicios y resume
  `uv run python scripts/usage_report.py`. Caddy guarda cada petición en
  `/var/log/caddy/ecudatamcp-access.log` (JSON, rota a 50 MB, 90 días); el
  `User-Agent` distingue Claude de ChatGPT.
- **Conectores:** "EcuDataMCP (Bogotá)" en la organización de Claude de LIDE
  (cada miembro pulsa Connect una vez; Claude no permite conexión automática
  para conectores personalizados sin OAuth) y en el espacio de ChatGPT de
  LIDE (instalado para todo el espacio).
- **Actualizar:** `git pull` en `~/EcuDataMCP`, `uv sync --no-dev` y
  `sudo systemctl restart ecuador-mcp`.

La instancia anterior en Render (plan gratuito, Oregon,
`https://ecuador-mcp-lb0s.onrender.com/mcp`) se suspendía tras unos 15
minutos sin tráfico y no tenía disco persistente.

**Alcance por origen (2026-11-04 y 2026-11-09).** Se probaron 57 URLs de
fuentes, una petición por URL y por origen. Cuenta como respuesta cualquier
código HTTP salvo 403. Resultados:

| Origen | URLs que respondieron (de 57) |
|---|---|
| VPN con salida en Ecuador | 52 |
| Render Oregon | 47 |
| Oracle Cloud Bogotá (2026-11-09) | 46 |
| Azure, las nueve regiones de EE. UU. | 44-45 |
| Azure Mexico Central y Chile Central | 44 |
| Conexión residencial en Canadá (Shaw, Edmonton) | 41 |
| Azure Canada Central y Canada East | 38-39 |
| Azure Brazil South | 34 |

Hallazgos:

- **Oracle Bogotá frente a Render y Canadá:** llega a las dos apps de
  Supercías, ANDA, `censoecuador.gob.ec`, SERCOP, EERSSA y a INEVAL BI (que
  falla desde todos los demás orígenes). No llega al CKAN de Cuenca,
  infoMIES, SEPS, el Ministerio del Trabajo, MINEDEC ni `www.sri.gob.ec`
  (conexión reiniciada), y CNE devuelve 403 como a Azure.
- **Render frente a Azure EE. UU.:** Render llega además a
  `www.igepn.edu.ec` y CNE, que devuelven 403 a todas las regiones de Azure.
- **IP de Canadá, residencial o de centro de datos:** no llegan a Supercías,
  SERCOP, SIGTIERRAS, el Ministerio del Trabajo ni el CKAN de Cuenca.
- **IP de Latinoamérica:** solo Mexico y Chile (y la VPN) llegan a ANDA y a
  `censoecuador.gob.ec`, pero desde ahí no responden el Ministerio del Trabajo
  ni el CKAN de Cuenca, y Emelnorte devuelve 418.
- **Brazil South** es el peor origen: además no llega a `www.gob.ec`, MSP, la
  SGR, ARCSA, MEF/MDEP, Ambiente y Energía ni CNIG.
- **Solo desde la VPN:** infoMIES, SEPS y MINEDEC. Hace falta
  `ECUADOR_MCP_GEO_PROXY` con salida en Ecuador.
- **Fallan desde todos los orígenes:** `reportes.arconel.gob.ec` responde
  "Error en runtime" (500) o no responde.

Una instancia en Azure Container Apps (Brazil South, luego East US) funcionó
el 2026-11-04 y se retiró el mismo día. Costaba unos 25-40 USD al mes y no
llegaba a más fuentes que Render.
