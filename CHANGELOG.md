# Changelog

## 0.8.1 — 2026-08-15

### Added
- Integración con el Banco Central del Ecuador vía BCEData
  (`contenido.bce.fin.ec/wp-json/bcedata/v1/`): API REST pública y sin
  autenticación, no documentada oficialmente pero descubierta inspeccionando
  el tráfico de red de la app JS del propio BCE (`contenido.bce.fin.ec/bcedata/`)
  y verificada con `curl` plano. Nuevos tools `search_indicadores_bce` (busca
  en el catálogo de ~78 grupos de indicadores: monetario/financiero, finanzas
  públicas, sector externo, sector real) y `get_indicador_bce` (serie de
  tiempo de un grupo, con frecuencia/unidad/rango configurables y defaults
  tomados de la metadata propia del grupo).
- `helpers/bce_client.py`: cachea el árbol completo del catálogo en memoria
  (~98 nodos, TTL 24h — es efectivamente estático) y cada bundle de metadata
  por grupo consultado; la serie de tiempo en sí no se cachea, se pide fresca
  cada vez.

## 0.8.0 — 2026-08-14

### Added
- Integración del ranking financiero de Supercías (dataset distinto del
  directorio): tools `search_ranking` y `get_financials` sobre indicadores
  derivados de balances reales — ingresos, activos, patrimonio, utilidad,
  empleados y ~38 ratios financieros (liquidez, endeudamiento, rentabilidad)
  por compañía y año fiscal
- `helpers/supercias_financials.py`: capa de consulta contra un SQLite local
  (`data/supercias_financials.sqlite3`, gitignored) construido de antemano
  por `scripts/build_supercias_financials_db.py` — la fuente
  (`bi_ranking.csv`) pesa ~356 MB / ~9M filas, demasiado grande para cachear
  en memoria como el directorio; el script la recorta a los últimos 5 años
  fiscales disponibles (autoajustable, no hardcodeado) al construir la DB
- `scripts/build_supercias_financials_db.py`: script aparte (no se corre
  perezosamente dentro de un tool call — tarda varios minutos) que descarga
  `bi_ranking.csv`, `bi_segmento.csv`, `bi_ciiu.csv` e `indicadores_sector.csv`
  y arma la base SQLite con índices. Reutiliza el directorio ya cacheado
  (`helpers/supercias_client.py`) para resolver nombre/RUC en vez de
  duplicar `bi_compania.csv`, que tiene los mismos campos
- `helpers/tls.py`: `legacy_cipher_context()`, mecanismo nuevo y separado del
  fallback de certificados vencidos — `appscvsmovil.supercias.gob.ec` (host
  distinto del directorio) falla el handshake TLS bajo la configuración por
  defecto de OpenSSL 3 (cifrados legados); este sigue verificando el
  certificado, solo baja el mínimo de fuerza de cifrado aceptado
- Fuente `supercias-financials` en `ecuador://fuentes`

## 0.7.0 — 2026-08-14

### Changed
- Reconcilia este fork con `upstream/main` tras dos PRs desarrolladas en
  paralelo: `housekeeping` (0.5.1, mergeada upstream) y la integración de
  Supercías (0.6.0, mergeada solo en este fork). Sin esto, este fork se
  hubiera quedado sin los fixes de housekeeping (TLS, WKT/decimales, aviso
  de series periódicas, `source_url`/`extras`) al haberse cortado la rama de
  Supercías antes de que housekeeping se mergeara upstream.

## 0.6.0 — 2026-08-13

### Added
- Integración Superintendencia de Compañías (Supercías): tools
  `search_companias` y `get_compania_info` sobre el directorio nacional de
  compañías (226k+, actualizado a diario) — situación legal, representante
  legal, capital suscrito, CIIU, dirección
- `helpers/supercias_client.py` con parseo propio del export Excel del
  directorio (bypassea openpyxl `read_only`, cuyo modo streaming se rompe con
  este archivo por un `<dimension>` mal declarado en el XML) y caché en
  memoria de 6h (el archivo se actualiza a diario y pesa ~35 MB / 226k filas)
- Fuente `supercias` en `ecuador://fuentes`

### Fixed
- Post-review sobre la integración de Supercías (`helpers/supercias_client.py`):
  - RUCs duplicados en el export (8 confirmados en el archivo real) ya no se
    pierden en silencio: se loguea un aviso con el conteo
  - Retry con TLS inseguro ante fallo de certificado (mismo mecanismo que
    CKAN), con el host de Supercías agregado al allowlist en `helpers/tls.py`
  - La hoja del workbook se resuelve vía `xl/workbook.xml` en vez de asumir
    `sheet1.xml`
  - Lock para evitar que llamadas concurrentes descarguen y parseen el
    archivo (~35 MB) por duplicado tras expirar el caché
  - Si el encabezado detectado tiene menos columnas que los datos reales,
    ahora falla con un error claro en vez de truncar filas en silencio
  - `provincia`/`situacion_legal` se normalizan una sola vez por refresco de
    caché en lugar de en cada búsqueda filtrada
  - `search_companias`/`get_compania_info`: los errores devueltos incluyen el
    parámetro de búsqueda/RUC que los originó, y quedan logueados en el
    servidor antes de convertirse en el mensaje al usuario
  - `search_companias` ya no muestra "Tipo:" / "Provincia:" en blanco cuando
    esos campos vienen vacíos
  - El índice por RUC se construye de forma perezosa (antes se calculaba en
    cada refresco de caché aunque `search_companias` nunca lo usa)

## 0.5.1 — 2026-08-13

### Added
- `created` y `last_modified` por recurso en `list_dataset_resources`, para
  poder identificar el archivo más reciente de un dataset con archivos
  periódicos sin tener que llamar a `get_resource_info` por cada uno
- `get_dataset_info` ahora incluye `source_url` (el campo "Fuente" del
  dataset: link a donde la entidad publicadora mantiene el dato original,
  fuera del portal) y `extras` (metadatos personalizados que la entidad haya
  agregado más allá del esquema estándar)
- `preview_resource_data` (CSV) ahora descarta columnas de geometría/WKT
  (`geom`, `wkt`, polígonos detectados por contenido) para no inundar el
  preview con coordenadas, y convierte columnas en formato decimal europeo
  (`7.760,2` → `7760.2`) a notación estándar. El mismo descarte de columnas
  de geometría aplica también al preview de JSON plano (arrays de objetos)
- `list_dataset_resources` ahora avisa cuando 3+ recursos de un dataset
  parecen ser una serie periódica (nombres casi idénticos, solo cambian
  números/fechas), para que quien consulte revise si cada archivo nuevo
  reemplaza a los anteriores o los complementa antes de sumar valores

### Changed
- `CKAN_INSECURE_TLS` ahora es `0` (desactivado) por defecto — el
  certificado de `www.datosabiertos.gob.ec` que expiró el 2026-07-28 fue
  renovado el 2026-08-07 (válido hasta 2026-11-05). Seguía activado por
  defecto desde que se agregó el fallback; poner `CKAN_INSECURE_TLS=1` solo
  si el certificado del portal vuelve a fallar

## 0.5.0 — 2026-08-10

### Added
- Integración Instituto Geofísico EPN (IG-EPN): tool `search_sismos` sobre el
  catálogo sísmico público (`portal/eventos/www/events.csv`) con filtros por
  texto, magnitud mínima y días, hora local (UTC-5) + UTC, y enlace al detalle
  de cada evento
- `helpers/igepn_client.py` con caché TTL (~2 min) y parseo tolerante del CSV
  (cabecera opcional, comas sin comillas en `place`)
- Fuente `igepn` en `ecuador://fuentes`; paso de sismos en el prompt
  `monitorear_riesgos`

## 0.4.4 — 2026-08-04

### Added
- `format=json` en tools restantes: `get_resource_info`, `get_organization_info`, `search_organizations`, `list_categories`, `get_category_info`, `list_instituciones`, `get_institucion_info`, `get_contrato_info`

## 0.4.3 — 2026-08-04

### Added
- DPA parroquias offline (~1040) + `lookup_ubicacion` con `nivel=parroquia`
- Resource MCP `ecuador://parroquias`
- Script `scripts/fetch_parroquias.py` (fuente ArcGIS Parroquias_del_Ecuador)
- `format=json` en `get_dataset_info`, `list_dataset_resources`, `preview_resource_data`, `query_resource_data`

## 0.4.2 — 2026-08-04

### Added / Improved
- SERCOP: cooldown + negative cache + `SercopRateLimitError` con mensaje claro
- Caché SERCOP ampliada a 30 min; respeta `Retry-After` cuando existe
- `format=json` en `search_tramites`, `search_regulaciones`, `get_tramite_info`, `get_regulacion_info`

## 0.4.1 — 2026-08-04

### Added
- `list_recent_datasets` (CKAN ordenado por `metadata_modified`)
- Smoke e2e `scripts/smoke_e2e.py`
- Más keywords auto-mapeadas en `search_tramites`
- `format=json` en `search_datasets`

## 0.4.0 — 2026-08-04

### Added
- DPA cantones offline (224) + `lookup_ubicacion` con `nivel=provincia|canton|auto`
- Resource MCP `ecuador://cantones`
- Integración SGR: `search_eventos_riesgo` (COE2) y `list_sat_tsunami`
- Prompt MCP `monitorear_riesgos`
- Parámetro `format=text|json` en tools clave (`list_capabilities`, `lookup_ubicacion`, `search_contratos`, eventos/SAT)
- Caché TTL (10 min) para búsquedas SERCOP

### Changed
- `search_contratos` corrige fallback de años cuando `year=0`
- README y capabilities actualizados (23 tools)

## 0.3.2 — 2026-08-04

- `list_capabilities`, `lookup_ubicacion` (provincias), resources `ecuador://*`

## 0.3.1 — 2026-08-04

- Prompts MCP, vínculo trámite→regulaciones, fallback de años SERCOP

## 0.3.0 — 2026-08-04

- Búsqueda unificada, DataStore, preview JSON/XLSX, regulaciones gob.ec, contratos SERCOP, CI/tests
