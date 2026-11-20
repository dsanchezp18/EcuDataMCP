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

## Estado y mantenimiento (2026-11-17)

Lo que sigue describe cómo está la VM hoy y cómo reconstruirla. Las cifras salen
de mediciones del 2026-11-17 (hechas en la propia VM, o desde Render y Canadá
donde se indica).

### Parches y reinicios

- `unattended-upgrades` está activo, pero sin `Automatic-Reboot`: tras un
  parche de kernel o de `libc6` el servicio sigue con la versión vieja hasta que
  alguien reinicia. Revisar con
  `[ -f /var/run/reboot-required ] && cat /var/run/reboot-required.pkgs`.
- Reinicio: `sudo systemctl reboot`. El corte fue de unos 35 s el 2026-11-17.
  Antes de reiniciar hay que comprobar que `ssh.socket`, `ecuador-mcp`, `caddy`
  y `netfilter-persistent` están `enabled` y que las reglas guardadas en
  `/etc/iptables/rules.v4` incluyen 22, 80 y 443 (si no, los puertos 80 y 443
  desaparecen tras el reinicio). Después: `systemctl --failed` vacío y `/health`
  en `ok`.
- Último reinicio: 2026-11-17, kernel `7.0.0-1016-oracle`.

### Acceso SSH

- Solo con clave (`PasswordAuthentication no`). En los 7 días anteriores al
  2026-11-17 hubo 18 928 intentos fallidos desde Internet.
- `fail2ban` instalado el 2026-11-17 con la jaula `sshd` por defecto (5 fallos,
  bloqueo de 10 min): `sudo fail2ban-client status sshd`.

### Aislamiento del servicio (systemd)

El servicio corre como `ubuntu` y escribe solo en `~/EcuDataMCP/data` (base de
Supercías, `usage.jsonl`, estado y bloqueo de la reconstrucción). Los drop-ins
de `/etc/systemd/system/ecuador-mcp.service.d/`:

- `10-hardening.conf`: `NoNewPrivileges`, `PrivateTmp`, `PrivateDevices`,
  `ProtectSystem=strict`, `ProtectHome=read-only` con
  `ReadWritePaths=/home/ubuntu/EcuDataMCP/data`, `ProtectKernel*`,
  `ProtectControlGroups`, `ProtectClock`, `ProtectHostname`, `RestrictSUIDSGID`,
  `RestrictRealtime`, `RestrictNamespaces`, `LockPersonality`,
  `RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX`,
  `SystemCallArchitectures=native`, `SystemCallFilter=@system-service`,
  `CapabilityBoundingSet=` (vacío), `UMask=0027`.
- `20-hide-tools.conf`: `Environment=ECUADOR_MCP_HIDE_TOOLS=...` (ver más abajo).

`systemd-analyze security ecuador-mcp` pasó de 9.2 UNSAFE a 1.8 OK. Antes de
aplicarlo se probó con una unidad transitoria con las mismas propiedades: el
servidor, las llamadas a la red, la lectura de SQLite, la escritura del registro
de uso y la reconstrucción completa de la base de Supercías (3 min 44 s)
funcionan dentro. Si una versión futura necesita escribir en otra ruta, hay que
añadirla a `ReadWritePaths`. Para volver atrás: borrar los dos archivos y ejecutar
`sudo systemctl daemon-reload && sudo systemctl restart ecuador-mcp`.

### Cabeceras de Caddy

`Strict-Transport-Security`, `X-Content-Type-Options: nosniff`,
`Referrer-Policy: no-referrer` y sin cabecera `Server`. La copia anterior está
en `/etc/caddy/Caddyfile.bak-20261117`. Validar siempre como el usuario del
servicio (como `ubuntu` falla al abrir el registro):
`sudo -u caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`
y recargar con `sudo systemctl reload caddy`.

### Herramientas ocultas y fuentes que esta VM no alcanza

`20-hide-tools.conf` oculta `search_contratos`, `get_contrato_info`,
`get_resumen_compras`, `search_infomies_bases_mensuales` y
`search_infomies_boletines_zonales` (80 tools en vez de 85): SERCOP e infoMIES no
responden desde Oracle Bogotá, así que esas tools solo podían fallar.

Medido el 2026-11-17 desde esta VM:

| Fuente | Resultado |
|---|---|
| CKAN nacional (`www.datosabiertos.gob.ec`) | 403 de CloudFront para cualquier cliente fuera de Ecuador: igual con `www` o apex, cualquier User-Agent, cabeceras o versión de HTTP; también desde Render, GitHub Actions y Azure |
| CKAN `iadb` y `latacunga` | funcionan |
| CKAN `cuenca` | no conecta desde Bogotá (sí desde Render) |
| ANDA, Supercías, IESS | funcionan |
| SERCOP, infoMIES, MINEDEC | no responden |
| SRI (`www.sri.gob.ec`) | conexión reiniciada (también desde Canadá) |

La única salida para el CKAN nacional es un egress en Ecuador
(`ECUADOR_MCP_GEO_PROXY`, ver `docs/GEOBLOCK_PLAN.md`).

### Riesgo: recuperación por inactividad

Oracle puede recuperar una instancia Always Free inactiva. Según su
[página oficial](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm),
una instancia se considera inactiva si, durante 7 días, el percentil 95 de CPU,
la red y (solo en A1) la memoria están todos por debajo del 20 %. Esta VM está
muy por debajo: CPU p95 de 0.71 % y memoria de 5.6 %. La página no menciona un
plazo de aviso ni una exención para cuentas de pago por uso (Pay As You Go); lo
segundo solo lo afirma un blog de terceros y no está verificado. Qué hacer:
vigilar el correo de la cuenta de Oracle, tener un chequeo externo de `/health` y,
si pasa, reconstruir con la lista siguiente. Como el nombre `sslip.io` lleva la
IP, una VM nueva cambia la URL y cada conector (Claude, ChatGPT) tendría que
volver a conectarse; con un dominio propio bastaría cambiar un registro A.

#### Temporizador `keep-active` (2026-11-20)

Para que Oracle no clasifique la VM como inactiva hay un temporizador de systemd,
`keep-active.timer`, que cada hora (más un retraso aleatorio de hasta 10 minutos)
lanza `keep-active.service`: un bucle ocupado por núcleo (2) durante 10 minutos.
Oracle solo la marca como inactiva si CPU, red y memoria están **todas** bajo el
20 % en el percentil 95 de 7 días, así que basta con superar una. Con 10 minutos
por hora (cerca del 17 % del tiempo al 100 %) el p95 de CPU queda muy por encima.

- Corre con `Nice=19`, `CPUSchedulingPolicy=idle`, `IOSchedulingClass=idle` y
  `DynamicUser`, así que el servicio MCP siempre tiene prioridad. Comprobado el
  2026-11-20 con la unidad real: durante la ráfaga la CPU marcó 100 % y `/health`
  siguió respondiendo en 0,1 s, igual que sin ella.
- Quitarlo: `sudo systemctl disable --now keep-active.timer && sudo rm
  /etc/systemd/system/keep-active.service /etc/systemd/system/keep-active.timer
  /usr/local/bin/keep-active.sh && sudo systemctl daemon-reload`.
- Límites: no hay forma de consultar cómo clasifica Oracle la instancia, así que
  no se ha visto aún su efecto; es una zona gris de los términos de Oracle y la
  decisión la tomó la persona titular de la cuenta. No sustituye el chequeo
  externo de `/health` ni vigilar el correo.

`/usr/local/bin/keep-active.sh` (modo 755):

```sh
#!/bin/sh
# Keeps the instance from looking idle to Oracle's Always Free reclaim check.
# Runs one busy loop per core for the given number of seconds (default 600).
# keep-active.timer starts it at idle priority, so the real service always wins.
seconds="${1:-600}"
for _ in $(seq "$(nproc)"); do
    timeout "$seconds" sh -c 'while :; do :; done' &
done
wait
exit 0
```

`/etc/systemd/system/keep-active.service`:

```ini
[Unit]
Description=CPU burst so the instance is not idle for Oracle's reclaim check

[Service]
Type=oneshot
ExecStart=/usr/local/bin/keep-active.sh 600
Nice=19
CPUSchedulingPolicy=idle
IOSchedulingClass=idle
DynamicUser=yes
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
TimeoutStartSec=15min
```

`/etc/systemd/system/keep-active.timer`:

```ini
[Unit]
Description=Hourly CPU burst so the instance is not idle (see docs/ORACLE_INSTANCE.md)

[Timer]
OnCalendar=hourly
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
```

Para instalarlo: copiar los tres archivos, `sudo systemctl daemon-reload` y
`sudo systemctl enable --now keep-active.timer`.

### Reconstruir la VM desde cero

1. Región `sa-bogota-1`, forma `VM.Standard.A1.Flex` (2 OCPU, 12 GB), Ubuntu
   24.04, 100 GB de disco, IP pública. Abrir 22, 80 y 443 en la lista de
   seguridad de la VCN.
2. En la VM: abrir 22, 80 y 443 en `iptables` con regla final `REJECT` y
   guardarlas (`sudo netfilter-persistent save`).
3. `sudo apt-get install -y git caddy fail2ban` e instalar `uv`
   (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
4. Clonar el fork y sincronizar:
   `git clone https://github.com/dsanchezp18/EcuDataMCP.git ~/EcuDataMCP`, luego
   `cd ~/EcuDataMCP && ~/.local/bin/uv sync --no-dev`. Crear también
   `mkdir -p ~/EcuDataMCP/data`: un clon nuevo no lo trae, y el drop-in de
   aislamiento lo lista en `ReadWritePaths`, así que systemd no arranca el
   servicio si no existe.
5. `/etc/systemd/system/ecuador-mcp.service`:

```ini
[Unit]
Description=EcuDataMCP (streamable HTTP)
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/EcuDataMCP
Environment=MCP_TRANSPORT=http
Environment=MCP_HOST=0.0.0.0
Environment=MCP_PORT=8000
Environment=MCP_PROFILE=public
Environment=MCP_REQUIRE_AUTH=0
Environment=MCP_MAX_CONCURRENT_REQUESTS=8
Environment=MCP_RATE_LIMIT_REQUESTS=120
Environment=MCP_RATE_LIMIT_WINDOW_SECONDS=60
Environment=FORWARDED_ALLOW_IPS=127.0.0.1
Environment=LOG_LEVEL=INFO
Environment=ECUADOR_MCP_USAGE_LOG=1
ExecStart=/home/ubuntu/EcuDataMCP/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

6. Los dos drop-ins descritos arriba y `/etc/caddy/Caddyfile` (cambiar el nombre
   por `<IP con guiones>.sslip.io`):

```caddyfile
129-38-110-203.sslip.io {
	encode gzip
	header {
		Strict-Transport-Security "max-age=31536000"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "no-referrer"
		-Server
	}
	log {
		output file /var/log/caddy/ecudatamcp-access.log {
			roll_size 50MiB
			roll_keep 10
			roll_keep_for 2160h
		}
		format json
	}
	@allowed path /mcp /mcp/* /health /usage
	handle @allowed {
		reverse_proxy 127.0.0.1:8000
	}
	handle {
		respond "EcuDataMCP: use /mcp (MCP endpoint), /health or /usage" 404
	}
}
```

7. `sudo systemctl daemon-reload && sudo systemctl enable --now ecuador-mcp
   caddy fail2ban`. La base de Supercías se reconstruye sola al arrancar (unos
   4 minutos, descarga de ~356 MB); `/health` muestra `construccion_en_curso`.
8. Comprobar desde fuera: solo 22, 80 y 443 abiertos, `/health` en `ok` y
   `tools/list` con 80 tools.
9. Reinstalar el temporizador `keep-active` (sección "Riesgo: recuperación por
   inactividad"), o una VM nueva volverá a quedar bajo el umbral de inactividad.

### Actualizar, con comprobación y vuelta atrás

```bash
cd ~/EcuDataMCP && git rev-parse --short HEAD     # anotar: punto de vuelta atrás
git pull --ff-only && ~/.local/bin/uv sync --no-dev
.venv/bin/python -c "import main"                  # debe terminar sin error
sudo systemctl restart ecuador-mcp
curl -s http://127.0.0.1:8000/health               # status ok
```

Si falla: `git reset --hard <commit anotado>`, `uv sync --no-dev` y reiniciar. La
reconstrucción de la base se dispara sola cuando cambia la versión del esquema.
