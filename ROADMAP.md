# Roadmap

Pendientes definidos para `EcuDataMCP`, reconstruidos de sesiones previas de
diseño e instalación (no existía este archivo hasta ahora).

Leyenda de estado: **[ ]** sin empezar · **[~]** parcial · **[x]** hecho

**Estado actual:** 8 hechos recientemente · 2 parciales · el resto sin empezar.
Ver [Completado recientemente](#completado-recientemente) para el detalle.

---

## Nuevas conexiones de datos

- [ ] **Página de datasets del SRI** (`https://www.sri.gob.ec/datasets`) — 131
      enlaces directos a archivos (93 CSV, 24 ZIP, 13 XLSX) más diccionarios
      `*_DD.xlsx`, en una sola página estable. Mejor relación valor/esfuerzo de
      la lista: el SRI hoy solo aparece parcialmente vía el portal CKAN
      genérico. Reafirmado por `Relevancia_Datos_Abiertos_2023.pdf` (ver
      subsección de abajo), que lo repite tres veces como fuente prioritaria.
- [ ] **Banco Central del Ecuador (BCE)** — el portal CKAN solo publica 4
      datasets del BCE; su data real vive en su propio sistema de
      estadísticas. Requiere un diseño de conexión aparte (API/sistema propio
      del BCE, no CKAN).
- [ ] **Ecuador en Cifras / portal BI del INEC** — sin investigar todavía.
- [ ] **Registro Civil** — pedido explícitamente por Daniel. Sin investigar:
      hay que distinguir entre datos agregados publicables (ej. estadísticas
      de nacimientos/matrimonios/defunciones por provincia y año) y consultas
      individuales de identidad, que son datos personales y no deberían
      exponerse vía este MCP. Portal propio (`registrocivil.gob.ec`) sin
      revisar todavía.
- [ ] **Cuenca en Datos** (`https://cuencaendatos.cuenca.gob.ec`) — CKAN 2.9.6,
      92 datasets, portal municipal independiente del nacional. Sin probar.
- [ ] **Sitios de ministerios individuales** — sin alcance definido; falta
      decidir cuáles justifican una conexión propia en vez de depender del
      portal CKAN central.
- [ ] **Asamblea Nacional — datos legislativos** — leyes, proyectos de ley y
      votaciones por asambleísta. Pedido explícitamente por Daniel. Portal
      propio sin investigar; verificar si expone API o solo HTML/PDF.
- [ ] **Concejos municipales / GADs — actas y resoluciones** — pedido
      explícitamente por Daniel. Sin alcance definido: empezar por Quito y
      Guayaquil o generalizar desde el arranque; sin investigar disponibilidad
      de datos abiertos a nivel de concejo.
- [ ] **Datos de votaciones** — pedido explícitamente por Daniel. Dos fuentes
      distintas a diferenciar: (a) votaciones electorales, cubierto por el
      ítem de CNE abajo; (b) registro de cómo vota cada asambleísta, que
      depende del ítem de datos legislativos de arriba y no tiene fuente
      identificada todavía.
- [ ] **CENACE y sector eléctrico** — pedido explícitamente por Daniel.
      Corporación Eléctrica del Ecuador (generación/despacho) y datos afines
      del sector (demanda, tarifas, cobertura). Portal(es) propio(s) sin
      investigar; no queda claro si CENACE publica algo fuera de reportes
      operativos internos — verificar alcance real antes de diseñar nada.
- [ ] **SENESCYT** — pedido explícitamente por Daniel. Datos de educación
      superior, becas, registro de títulos. Sin investigar disponibilidad ni
      si expone API propia.
- [ ] **Ministerio de Educación** — pedido explícitamente por Daniel. El
      portal CKAN ya publica algo de MINEDUC (ver ejemplo "Registro de
      Matrícula" en el manual de usuarios del portal), pero sin confirmar
      cobertura completa. Falta verificar qué falta fuera del CKAN genérico.
- [ ] **Ministerio de Gobierno** — pedido explícitamente por Daniel. Sin
      alcance definido ni portal identificado; falta investigar qué publica
      y si vale la pena una conexión dedicada en vez de depender del CKAN
      central.
- [ ] **Fiscalía General del Estado** — pedido explícitamente por Daniel.
      Sin investigar; datos de causas penales probablemente tienen
      restricciones de acceso/privacidad más estrictas que otros datasets
      del portal — confirmar qué es realmente publicable como dato abierto
      antes de diseñar una conexión.
- [ ] **ECU 911 (Servicio Integrado de Seguridad)** — pedido explícitamente
      por Daniel. Estadísticas de incidentes/emergencias atendidas,
      tiempos de respuesta, cobertura territorial. Verificar solapamiento
      con `search_eventos_riesgo`/SGR (ya integrado, eventos del COE) antes
      de diseñar nada — puede que ECU 911 sea una fuente distinta
      (seguridad ciudadana/emergencias 911) del SGR (gestión de riesgos de
      desastres), no redundante, pero hay que confirmarlo. Portal propio sin
      investigar.

### Datasets anticorrupción

Fuente: `Relevancia_Datos_Abiertos_2023.pdf` (GIZ/MINTEL/SENPLAN, ene. 2023),
Tabla 5 — lista los datasets de mayor valor para la lucha anticorrupción en
Ecuador. Los que ya cubre el portal CKAN genérico no se repiten aquí; estos
son los que viven en portales propios o no están mapeados a ningún tool
todavía:

- [ ] **SERCOP — beneficiario final de contratos públicos**
      (`https://portal.compraspublicas.gob.ec/sercop/beneficiario-final/`) —
      **ojo, esto NO está cubierto todavía**, a pesar de que SERCOP en
      general sí lo está. `search_contratos`/`get_contrato_info` ya
      consultan la API OCDS de SERCOP
      (`datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/`), que es un
      sistema distinto al portal de beneficiario final — ese sigue sin
      conexión.
- [ ] **Consejo Nacional Electoral — bases de datos estadísticas**
      (`https://www.cne.gob.ec/estadisticas/bases-de-datos/`) — resultados
      electorales y votaciones (formato SPSS mencionado en el estudio).
- [ ] **Registro Oficial** (`https://www.registroficial.gob.ec/`) — compilado
      de leyes y publicaciones oficiales; sin conexión hoy.
- [ ] **Contraloría General del Estado — declaraciones juradas**
      (`https://www.contraloria.gob.ec/Consultas/DeclaracionesJuradas`) —
      declaraciones de bienes y rentas / conflictos de interés de
      funcionarios públicos.
- [ ] **UAFE (Unidad de Análisis Financiero y Económico) — registro de
      Personas Expuestas Políticamente (PEP)** — sin portal identificado
      todavía; pendiente investigar disponibilidad.

---

## Cabos operativos sueltos

- [~] **Revisar renovación del certificado TLS** de `www.datosabiertos.gob.ec`
      (había vencido 2026-07-28). **Verificado 2026-08-13: el gobierno ya lo
      renovó** — el certificado vigente es válido desde el 7 de agosto hasta
      el 5 de noviembre de 2026 (`CN=datosabiertos.gob.ec`). Falta el paso de
      código: `helpers/tls.py` tiene `CKAN_INSECURE_TLS` en `"1"` (fallback
      inseguro activado) por defecto — apagarlo (default `"0"`) ahora que el
      cert es válido, para no dejar ese fallback abierto más tiempo del
      necesario. Pendiente de confirmación antes de tocar el default.
- [ ] **Burlar el bloqueo geográfico del portal** — pedido explícitamente por
      Daniel. `www.datosabiertos.gob.ec` a veces rechaza conexiones que vienen
      de fuera de Latinoamérica con 403 (documentado en el README, afecta a
      `search_datasets`, `search_organizations`, `get_organization_info`,
      `get_dataset_info`, `list_dataset_resources`, `get_resource_info`,
      `preview_resource_data`, `query_resource_data`, `list_recent_datasets`,
      `list_categories` y `get_category_info`). Esto es distinto del bug de
      vhost ya corregido (ver [Notas](#notas)) — es bloqueo real por
      geografía del origen de la conexión, no un bug del servidor. Opciones a
      evaluar: (a) salida saliente vía proxy/relay alojado en la región, (b)
      documentar claramente el workaround de VPN con salida LatAm para quien
      hostea el MCP fuera de la región, (c) retry automático contra un mirror
      o vía un proxy configurable por variable de entorno. Sin diseño
      todavía.

---

## Calidad de búsqueda y detección de series

- [ ] **Búsqueda semántica** — `search_datasets` pasa directo a búsqueda por
      palabra clave de CKAN, que es débil frente al catálogo completo (ejemplo
      real contra el mismo portal: "cacao" devuelve muy pocos resultados).
      Falta una capa de similitud/embeddings que mejore el recall sin
      reemplazar la búsqueda en vivo.
- [ ] **Expansión de siglas/acrónimos en la consulta** — los usuarios escriben
      "ENEMDU", "ENSANUT", "RUC"; el catálogo los tiene deletreados completos
      en los metadatos. Falta expandir la consulta antes de buscar (por
      keyword o por embeddings).
- [~] **Detección real acumulado-vs-incremental** entre archivos de un mismo
      dataset — cuando un dataset publica un archivo por período (ej. precios
      semanales de cacao del MPCEIP), falta distinguir si cada archivo nuevo
      reemplaza a los anteriores (acumulado, solo hay que leer el más
      reciente) o los complementa (incremental, hay que sumarlos todos).
      Confundirlo trunca o duplica una serie silenciosamente. **Parcial:** el
      prerrequisito de datos (`created`/`last_modified` por recurso en
      `list_dataset_resources`) ya está resuelto (PR #5, ver
      [Completado recientemente](#completado-recientemente)); todavía falta
      la heurística que decide acumulado-vs-incremental usando esas fechas.
      **Revisado 2026-08-13:** si es acumulado o incremental depende de la
      semántica del dataset (ej. "contribuyentes activos" es un acumulado
      que se reemplaza; "precios semanales de cacao" es incremental y hay
      que sumar todas las semanas) — no es algo que se pueda inferir de
      forma confiable solo con patrones de nombre/fecha de archivo. Antes de
      construir una heurística en código (con riesgo real de acertar mal y
      producir el mismo error silencioso que se quiere evitar), vale más
      asegurarse de que `list_dataset_resources` exponga nombre, descripción
      y fechas de cada recurso con suficiente detalle para que el modelo
      razone caso por caso — que es, en gran parte, lo que el PR #5 ya
      habilita. Una heurística de código valdría la pena solo como aviso
      liviano (ej. "estos N recursos parecen ser una serie periódica,
      revisa si se complementan o se reemplazan"), no como una decisión
      automática de sumar o no.

---

## Formatos y tipos de recursos

- [ ] **Tool `read_pdf(url, pages)`** — no hay soporte para leer PDFs del
      portal. Pocos casos hoy, pero es el desbloqueo para fuentes curadas más
      adelante.
- [ ] **Prompts de flujo de trabajo adicionales** (`@mcp.prompt()`) — hoy solo
      hay uno; falta al menos un segundo prompt guiado para exploración
      temática (ej. "explorar_tema").
- [ ] **Soporte `.rar`** — decisión pendiente: implementarlo (necesita binario
      `unrar`) o documentar el rechazo como definitivo.
- [ ] **Recursos sin extensión** — requieren sniffing de content-type; sin
      implementar ni probar.
- [ ] **Soporte `.xls` legacy** — hoy `preview_resource_data` lo rechaza
      explícitamente; decidir si vale la pena soportarlo.

---

## Verificación end-to-end pendiente

Cifras de referencia contra el mismo portal (`www.datosabiertos.gob.ec`),
para confirmar que los tools devuelven los números correctos, no solo que no
truenan:

- [ ] **SRI** `contribuyentes-activos-catastro-2025` → 2,904,355
      contribuyentes en el mes más reciente vía `sum(TOTAL)`, **no**
      `count(*)` (que da 405,794).
- [ ] **IESS** `base-de-datos-seguro-desempleo`, junio 2026 → 2,561
      beneficiarios, USD 836,716.99, excluyendo la fila `TOTAL:` embebida en
      el archivo (incluirla da exactamente el doble).
- [ ] **MPCEIP** cacao → junio 2026, Grado 1 semanal: 174.77 / 168.15 /
      166.28 / 188.07, usando solo el archivo más reciente.
- [ ] Cobertura real de formatos: `.xls`, `.zip`, `.rar` y una URL sin
      extensión, probados de punta a punta.
- [ ] Degradación cuando el portal no responde — confirmar que el error que
      recibe el modelo es accionable (indica el host correcto), no genérico.

---

## Arquitectura, más adelante

- [ ] **Salidas estructuradas vía `outputSchema` de MCP** — hoy todos los
      tools devuelven texto o un string JSON; falta usar salida estructurada
      real del protocolo donde aplique.
- [ ] **Manejo geoespacial de recursos** — sin diseñar.
- [ ] **Tool `research` de una sola llamada** que encadene
      descubrimiento → selección → consulta en un solo round trip, para
      reducir la cantidad de llamadas que necesita el modelo en una
      exploración típica.

---

## Distribución y visibilidad

- [ ] **Hostear el MCP públicamente** — pedido explícitamente por Daniel.
      Hoy el README solo documenta correrlo local (Docker o `uv run`) contra
      `localhost:8000`; falta un despliegue público real (dominio propio,
      HTTPS, hosting que lo mantenga corriendo) para que alguien lo use sin
      clonar el repo. Sin decidir proveedor ni diseño todavía.
- [ ] **Publicarlo en registries de MCP** — pedido explícitamente por
      Daniel. Registrar el servidor en directorios públicos de servidores
      MCP (el registry oficial de Anthropic/MCP, y alternativas como
      Smithery, PulseMCP, mcp.so, Glama) para que aparezca en búsquedas.
      Depende de tener el hosting público del ítem de arriba resuelto
      primero — la mayoría de registries piden una URL viva, no solo
      instrucciones de instalación local.
- [ ] **Sitio web propio para el MCP** — pedido explícitamente por Daniel,
      con [opendata.fyi](https://opendata.fyi) como referencia de qué tan
      cuidado debería verse. Landing page que explique qué hace el servidor,
      liste las fuentes de datos y tools, y facilite la conexión (copiar
      config para cada cliente MCP) — hoy esa información solo vive en el
      README. Sin diseño ni stack decidido todavía.

---

## Completado recientemente

- [x] **Superintendencia de Compañías (Supercías) — directorio de compañías**
      — PR [dsanchezp18/EcuDataMCP#5](https://github.com/dsanchezp18/EcuDataMCP/pull/5)
      (2026-08-13, rama `feature/supercias-directorio`, sin mergear
      todavía). Link encontrado por Daniel
      (`mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx`)
      resultó ser un Excel estático descargable de una sola vez (226,289
      compañías, sin auth ni paginación), no había que scrapear el JSF.
      Nuevos tools `search_companias`/`get_compania_info` en
      `helpers/supercias_client.py`, con parseo propio vía
      `ElementTree.iterparse` (el `<dimension>` del archivo viene mal
      declarado y rompe el modo `read_only` de openpyxl) y caché de 6h.
      Verificado contra el archivo real del portal.
- [x] **Instituto Geofísico (IG-EPN)** — hecho antes de este archivo, via
      `search_sismos` + `helpers/igepn_client.py` (CHANGELOG 0.5.0,
      2026-08-10), con caché y tests (`tests/test_igepn_client.py`). El PR a
      *upstream* (`DweskZ/EcuDataMCP` [#4](https://github.com/DweskZ/EcuDataMCP/pull/4))
      sigue abierto — el tool ya funciona en este fork, falta que lo
      mergeen aguas arriba.
- [x] **Housekeeping de tools de lectura — PR [#5](https://github.com/DweskZ/EcuDataMCP/pull/5)
      a upstream** (2026-08-13, rama `housekeeping`):
    - `list_dataset_resources` incluye `created`/`last_modified` por recurso
      (desbloquea la detección acumulado-vs-incremental de arriba).
    - `get_dataset_info` incluye `source_url` (campo "Fuente" del publicador)
      y `extras` (metadatos personalizados por dataset).
    - `preview_resource_data` descarta columnas de geometría/WKT (por nombre
      o contenido, en CSV y JSON plano) y normaliza decimales en formato
      europeo (`7.760,2` → `7760.2`) en CSV.
- [x] **Borrar ramas ya mergeadas** (local y en el fork) — hecho el
      2026-08-13: `feature/anda-search`, `fix/ckan-403-latam-note`,
      `fix/ckan-domain-and-readme`, `claude/project-overview-woxgte` y sus
      equivalentes en `origin` (más `claude/fork-verification-h1938e`,
      `claude/instituto-geofisico-integration-gk66de`,
      `sync-anda-403-upstream`) ya no existen. El intento automático de borrar
      en `origin` fue bloqueado por el classifier de seguridad — Daniel lo
      hizo manualmente. `origin/igepn-upstream-pr` se mantiene: respalda el PR
      #4 abierto en upstream (`DweskZ/EcuDataMCP`) y le faltan dos commits de
      main (`f7ae515`, `0835f9b`) antes de que se pueda mergear.
      `fork-only/reference-docs` se mantiene aparte a propósito (ver README de
      esa carpeta).
- [x] **Decidir sobre los dos `Manual de Usuarios Portal.pdf` duplicados** en
      `reference-docs/` — resuelto el 2026-08-13: no son duplicados. El de
      395 KB es la versión vigente republicada por el gobierno (screenshots y
      cifras de 2024, URLs reales). El de 2.5 MB es el entregable original de
      2021 ("Entregable 5") de Datasketch, la consultora que rediseñó el
      portal, con links placeholder y referencias cruzadas rotas. Mismo
      contenido, dos épocas — el de 2.5 MB solo aporta procedencia histórica;
      se puede borrar si se quiere aligerar la carpeta.

---

## Notas

**Corrección de diagnóstico (2026-08-13):** el 403 de CKAN que se creía un
bloqueo geográfico/upstream era en realidad un bug de vhost — el apex
`datosabiertos.gob.ec` y el subdominio `presidencia` resuelven a la misma IP
pero devuelven 403; solo `www.datosabiertos.gob.ec` está conectado. Ya
corregido en el repo; los 27 tools funcionan. (No confundir con el bloqueo
geográfico real que sí sigue pendiente, ver "Burlar el bloqueo geográfico del
portal" arriba.)
