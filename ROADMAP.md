# Roadmap

Pendientes definidos para `EcuDataMCP`, reconstruidos de sesiones previas de
diseño e instalación (no existía este archivo hasta ahora).

Leyenda de estado: **[ ]** sin empezar · **[~]** parcial · **[x]** hecho

**Estado actual (revisado 2026-08-15):** 9 hechos · 7 parciales (6 de ellos —
Registro Civil, Salud, Interior, INAMHI, Energía/Minas, SENAE — ya
reachable hoy sin código nuevo, vía los tools CKAN genéricos) · el resto sin
empezar. Ver [Completado recientemente](#completado-recientemente) para el
detalle.

---

## Nuevas conexiones de datos

- [ ] **Página de datasets del SRI** (`https://www.sri.gob.ec/datasets`) — 131
      enlaces directos a archivos (93 CSV, 24 ZIP, 13 XLSX) más diccionarios
      `*_DD.xlsx`, en una sola página estable. Mejor relación valor/esfuerzo de
      la lista: el SRI hoy solo aparece parcialmente vía el portal CKAN
      genérico. Reafirmado por `Relevancia_Datos_Abiertos_2023.pdf` (ver
      subsección de abajo), que lo repite tres veces como fuente prioritaria.
- [ ] **Ecuador en Cifras / portal BI del INEC** — sin investigar todavía.
- [~] **Registro Civil** — pedido explícitamente por Daniel. **Revisado
      2026-08-15: ya reachable hoy, sin código nuevo,** vía los tools CKAN
      genéricos (`search_organizations`/`get_organization_info`/
      `search_datasets` con `organization="registro-civil"` en
      `datosabiertos.gob.ec`) — 6 datasets: transacciones de cedulación,
      pasaportes electrónicos, copias de actas registrales, certificado de
      firma electrónica, catálogo de agencias. **Ojo:** son conteos de
      transacciones de servicios, no las estadísticas vitales
      (nacimientos/matrimonios/defunciones) que se esperaban — esas sí
      existen pero via INEC/ANDA (`search_anda`; ej. "Estadística de
      Defunciones Generales" por año, ya indexado). Portal propio
      `registrocivil.gob.ec/datos-abiertos/` sin revisar — puede tener más
      que el CKAN. La distinción datos-agregados-vs-consulta-individual del
      pedido original sigue aplicando: nada de esto expone identidad
      individual, es agregado por diseño.
- [~] **Ministerio de Salud Pública** — **no pedido explícitamente, agregado
      2026-08-15 tras pregunta de Daniel sobre cobertura de ministerios.**
      Ya reachable hoy vía CKAN genérico
      (`organization="ministerio-de-salud-publica"`) — 8 datasets: MSP_Nutrición,
      MSP_Vacunas, Anestesias e Intervenciones Quirúrgicas, Exámenes de
      laboratorio, Emergencias, Vacuna COVID-19, Casos COVID, Consulta
      Externa. La plataforma propia "Salud en Cifras"
      (`salud.gob.ec/salud-en-cifras`) puede tener series más largas o
      geolocalizadas — sin revisar si vale la pena una conexión dedicada
      aparte del CKAN.
- [~] **Ministerio del Interior** — **no pedido explícitamente, agregado
      2026-08-15 tras pregunta de Daniel.** Ya reachable hoy vía CKAN
      genérico (`organization="ministerio-del-interior"`) — 6 datasets:
      Homicidios Intencionales, Personas Detenidas y Aprehendidas, Personas
      Desaparecidas, Armas Ilícitas, Sustancias Catalogadas, Trata de
      Personas y Tráfico Ilícito de Migrantes. Cubre lo que el ítem de "ECU
      911" de abajo probablemente NO cubre (seguridad/criminalidad vs.
      emergencias 911).
- [~] **INAMHI (meteorología e hidrología)** — **no pedido explícitamente,
      agregado 2026-08-15 al buscar nuevas fuentes candidatas.** Ya
      reachable hoy vía CKAN genérico
      (`organization="instituto-nacional-de-meteorologia-e-hidrologia-inamhi"`)
      — 4 datasets: Temperatura Máxima/Mínima Absoluta, Temperatura Media
      Mensual, Precipitación Total Mensual. Solo la punta del iceberg: INAMHI
      tiene un geoportal propio (`geoservicios.inamhi.gob.ec`) con red
      hidrológica, calidad de agua y zonas de riesgo de inundación, más
      pronósticos hidrometeorológicos en `inamhi.geoglows.org` — ninguno de
      los dos investigado todavía. Clima/tiempo es un tipo de dato muy
      pedido en general; vale la pena evaluar una conexión dedicada más
      allá de los 4 datasets del CKAN.
- [~] **Ministerio de Energía y Minas (hidrocarburos)** — **no pedido
      explícitamente, agregado 2026-08-15.** Ya reachable hoy vía CKAN
      genérico (`organization="ministerio-de-energia"`) — 14 datasets:
      precios teóricos de crudo, perforación de pozos petroleros (series
      mensuales). El "Banco de Información Petrolera del Ecuador" (BIPE,
      ~13,000 GB, ~74,000 documentos) es un repositorio mucho más grande y
      completo, sin investigar si expone algo consultable
      programáticamente o es solo un archivo documental. Dado el peso del
      petróleo en la economía ecuatoriana, este es un candidato de alto
      valor si BIPE resulta consultable.
- [~] **SENAE (aduanas / comercio exterior)** — **no pedido explícitamente,
      agregado 2026-08-15.** Ya reachable hoy vía CKAN genérico
      (`organization="senae"`) — 3 datasets: recaudaciones de tributos de
      comercio exterior, importaciones aduaneras (régimen general y
      simplificado). El sistema "ECX" (BCE + SENAE, consultable por país,
      producto y período) puede tener más detalle que estos 3 datasets —
      sin investigar si expone API propia o solo interfaz web.
- [ ] **Superintendencia de Bancos** — **no pedido explícitamente, agregado
      2026-08-15.** Distinta de Supercías (que regula compañías, no
      bancos) — sin organización en el CKAN (`organization_show` da 404
      para `superintendencia-de-bancos`). **Investigado a fondo
      2026-08-15: NO tiene una API REST como BCE (ver ítem de arriba) —
      contrario a lo que sugerían resultados de búsqueda genéricos.**
      Confirmado inspeccionando el tráfico de red real de
      `superbancos.gob.ec/estadisticas/portalestudios/`: es un sitio
      WordPress corriente (Elementor + TablePress), sin ningún plugin tipo
      `bcedata-grid`. Los "Boletines de Series" (ej. página "Bancos
      Privados", series históricas desde diciembre 2002 — balances,
      P&G, cartera de crédito por línea, matrices de riesgo, número de
      depositantes) se navegan con un widget de explorador de
      carpetas en JS (plugin de compartición de OneDrive/SharePoint,
      `admin-ajax.php` con acción propia, no una API REST versionada) que
      resuelve a archivos `.zip` con series en Excel alojados en OneDrive
      (ej. `Total Series Bancos Privados JULIO 2026.zip`, ~7 MB, URL
      firmada con `account_id`/`drive_id`/`listtoken`). Integrarlo sería
      más parecido a lo que ya hicimos para el directorio de Supercías
      (descargar y parsear Excel) que a una API real, pero con el paso
      extra de primero resolver la URL del ZIP del mes vigente — sea
      replicando la llamada AJAX del widget, sea con un browser headless
      corriendo periódicamente. Más esfuerzo que BCE para una prioridad
      similar; si se hace alguno de los dos primero, empezar por BCE.
- [ ] **SEPS (economía popular y solidaria)** — **no pedido explícitamente,
      agregado 2026-08-15.** Cooperativas, cajas y bancos comunales — sin
      organización en el CKAN. Portal propio
      (`estadisticas.seps.gob.ec`, "Data SEPS" portal interactivo) con
      número de organizaciones/socios y balances anuales (17,415
      organizaciones activas al 2026-03). Sin API documentada encontrada
      todavía.
- [ ] **ARCERNNR/ARCONEL (regulación eléctrica)** — **no pedido
      explícitamente, agregado 2026-08-15.** Distinto del ítem "CENACE y
      sector eléctrico" de abajo: CENACE opera generación/despacho,
      mientras que ARCERNNR (antes ARCONEL) es el regulador — estadísticas
      de generación/transmisión/distribución/alumbrado público. Sin
      organización en el CKAN, pero **sí aparece en ANDA** (catálogos
      "Estadística del Sector Eléctrico Ecuatoriano 2022/2023/2024",
      `anda.inec.gob.ec/anda/index.php/catalog/1080` y similares) — antes
      de diseñar una conexión dedicada, confirmar si `search_anda` ya los
      encuentra. También tienen un geoportal propio, GeoSISDAT.
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
      Ver también el ítem separado de ARCERNNR/ARCONEL arriba (el
      regulador, no el operador) — probablemente se resuelven juntos si se
      diseña una conexión al sector eléctrico.
- [ ] **SENESCYT** — pedido explícitamente por Daniel. Datos de educación
      superior, becas, registro de títulos. Sin investigar disponibilidad ni
      si expone API propia.
- [ ] **Ministerio de Educación** — pedido explícitamente por Daniel. El
      portal CKAN ya publica algo de MINEDUC (ver ejemplo "Registro de
      Matrícula" en el manual de usuarios del portal), pero sin confirmar
      cobertura completa. Falta verificar qué falta fuera del CKAN genérico.
- [ ] **Ministerio de Gobierno** — pedido explícitamente por Daniel.
      **Revisado 2026-08-15:** el slug `ministerio-de-gobierno` no existe en
      el CKAN (`organization_show` da 404) — a diferencia de Salud e
      Interior, este no tiene organización propia en el portal. Puede que
      sus funciones estén repartidas entre Interior y otras carteras
      (reorganización institucional) o que simplemente no publique ahí;
      falta confirmar si el ministerio existe como entidad separada hoy y,
      si es así, dónde publica.
- [ ] **Fiscalía General del Estado** — pedido explícitamente por Daniel.
      **Revisado 2026-08-15:** no tiene organización en el CKAN (`fiscalia`,
      `fiscalia-general-del-estado` dan 404). Sí existe un catálogo propio
      en ANDA (`anda.inec.gob.ec/anda/index.php/catalog/FGE/about`,
      repositorio `FGE`), pero búsquedas de prueba vía `search_anda` con
      "Fiscalía General" y términos relacionados no lo encontraron —
      confirmar si el repositorio FGE tiene contenido real o está vacío/casi
      vacío antes de invertir en esto. Aparte, la Fiscalía atiende pedidos de
      estadística por trámite formal (`fiscalia.gob.ec/estadisticas-fge/`),
      no vía API — la restricción de privacidad de causas penales
      individuales sigue aplicando igual que antes.
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

- [x] **Revisar renovación del certificado TLS** de `www.datosabiertos.gob.ec`
      (había vencido 2026-07-28). Verificado 2026-08-13: el gobierno ya lo
      renovó — válido del 7 de agosto al 5 de noviembre de 2026
      (`CN=datosabiertos.gob.ec`). **Hecho:** `CKAN_INSECURE_TLS` ahora
      defaultea a `"0"` en `helpers/tls.py` (antes `"1"`) — el fallback
      inseguro solo se activa si se pone la variable explícitamente.
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
- [ ] **`get_financials`/`search_ranking` — buscar en todos los años
      fiscales, no solo los últimos 5** — pedido explícitamente por Daniel.
      Decisión original (ver plan de la sesión que lo diseñó): recortar
      `bi_ranking.csv` a los últimos 5 años fiscales al construir el SQLite,
      autoajustable pero fijo en el build. La fuente real
      (`bi_ranking.csv`) cubre 2008-presente (~9M filas sin recortar) — el
      histórico completo existe, solo no se carga. Para exponerlo hay que
      decidir: (a) cargar el histórico completo en el mismo SQLite (~9M
      filas sin recorte, mucho más grande que los ~660k filas actuales de 5
      años — revisar tamaño resultante en disco antes de decidir), o (b) un
      parámetro opcional (ej. `anio_desde`) que dispare una carga bajo
      demanda de años fuera del rango cacheado, o (c) un segundo build
      "histórico completo" aparte del recortado, seleccionable por
      variable de entorno. Sin diseño todavía — empezar por confirmar el
      tamaño en disco de la opción (a), que es la más simple de implementar
      si el tamaño no es un problema real.

---

## Calidad de búsqueda y detección de series

- [ ] **Búsqueda semántica** — `search_datasets` pasa directo a búsqueda por
      palabra clave de CKAN, que es débil frente al catálogo completo (ejemplo
      real contra el mismo portal: "cacao" devuelve muy pocos resultados).
      Falta una capa de similitud/embeddings que mejore el recall sin
      reemplazar la búsqueda en vivo. **Precedente técnico concreto
      (2026-08-15):** [opendata.fyi](https://www.opendata.fyi/#how) (MCP
      equivalente para datos públicos de Canadá) resuelve esto indexando
      metadata de sus fuentes como vectores de 384 dimensiones en DuckDB, y
      combina esa búsqueda semántica con consultas en vivo a sus catálogos
      CKAN mediante Reciprocal Rank Fusion (RRF) — un solo ranking unificado
      de ambas señales en vez de elegir una u otra. DuckDB ya es liviano y
      embebible (mismo perfil que SQLite, que este repo ya usa para
      `supercias_financials.py`), así que no es una dependencia de
      infraestructura pesada si se decide seguir este camino.
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
- [ ] **Sitio web propio para el MCP** — pedido explícitamente por Daniel.
      **Referencia concreta (2026-08-15): [opendata.fyi](https://www.opendata.fyi/#how)
      es el tipo de sitio que quiere construir**, no solo una referencia de
      diseño visual — es un MCP casi idéntico en propósito (ayuda a
      asistentes de IA a descubrir/consultar datos públicos abiertos,
      federal/provincial en su caso, Canadá) con una landing page que
      explica:
      - **Un flujo de 4 pasos** (Discover → Inspect → Query → Cite):
        descubrimiento semántico del catálogo, validación de metadata antes
        de traer datos, filtrado server-side al consultar, y enlace directo
        a la fuente oficial para trazabilidad/cita.
      - **Privacidad por defecto** ("telemetry off by default") como
        argumento de venta explícito en la landing.
      - **Instalación simple** documentada en la página misma, no solo en
        el README del repo.
      - **Credibilidad open-source** vía link directo a GitHub.
      Aplicable directo a este MCP: landing page que explique qué hace el
      servidor, liste fuentes/tools, muestre el mismo tipo de flujo
      (buscar → inspeccionar → consultar → citar la fuente oficial) y
      facilite la conexión (copiar config por cliente MCP) — hoy esa info
      solo vive en el README. Sin diseño ni stack decidido todavía. Ver
      también la nota técnica de opendata.fyi sobre búsqueda semántica en
      "Búsqueda semántica" abajo — su arquitectura de discovery es
      relevante para ese ítem también, no solo para el sitio.

---

## Completado recientemente

- [x] **Banco Central del Ecuador (BCE) — catálogo estadístico (BCEData)**
      — PR [dsanchezp18/EcuDataMCP#10](https://github.com/dsanchezp18/EcuDataMCP/pull/10)
      (2026-08-15, rama `feature/bce-indicadores`, abierto). El portal CKAN
      solo publicaba 4 datasets del BCE; investigando a fondo apareció
      **BCEData**, la app de consulta estadística del propio BCE
      (`contenido.bce.fin.ec/bcedata/`), que resultó tener una REST API
      pública sin autenticación bajo `/wp-json/bcedata/v1/` — no
      documentada oficialmente, encontrada inspeccionando el tráfico de
      red de la app y confirmada con `curl` plano. Nuevos tools
      `search_indicadores_bce`/`get_indicador_bce` en
      `helpers/bce_client.py`, sobre `/tree` (catálogo completo, ~98
      nodos, cacheado 24h), `/bundle/{id_grupo}` (metadata: frecuencias,
      unidades, rango de fechas) y `/grid` (la serie de tiempo). Cubre
      Estadísticas Monetarias y Financieras, Finanzas Públicas, Sector
      Externo (comercio exterior) y Sector Real (PIB, inflación,
      desempleo, confianza del consumidor). Verificado en vivo:
      `search_indicadores_bce("producto interno bruto")` → 7 resultados;
      `get_indicador_bce(id_grupo=82, ...)` → serie mensual real del
      índice de confianza del consumidor.
- [x] **Superintendencia de Compañías (Supercías) — directorio de compañías**
      — PR [dsanchezp18/EcuDataMCP#5](https://github.com/dsanchezp18/EcuDataMCP/pull/5)
      (2026-08-13, rama `feature/supercias-directorio`), **mergeado a `main`
      del fork el 2026-08-14.** Link encontrado por Daniel
      (`mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx`)
      resultó ser un Excel estático descargable de una sola vez (226,289
      compañías, sin auth ni paginación), no había que scrapear el JSF.
      Nuevos tools `search_companias`/`get_compania_info` en
      `helpers/supercias_client.py`, con parseo propio vía
      `ElementTree.iterparse` (el `<dimension>` del archivo viene mal
      declarado y rompe el modo `read_only` de openpyxl) y caché de 6h.
      Verificado contra el archivo real del portal.
- [x] **Superintendencia de Compañías (Supercías) — ranking financiero**
      — PR [dsanchezp18/EcuDataMCP#6](https://github.com/dsanchezp18/EcuDataMCP/pull/6)
      (2026-08-15), **mergeado a `main` del fork.** Segundo dataset de
      Supercías (`bi_ranking.csv`, ~356 MB / ~9M filas) — ingresos, activos,
      patrimonio y ~38 ratios financieros por compañía y año fiscal, desde
      balances reales. Nuevos tools `get_financials`/`search_ranking` sobre
      un SQLite local (`scripts/build_supercias_financials_db.py`, recortado
      a los últimos 5 años fiscales, autoajustable). Requiere
      `legacy_cipher_context()` nuevo en `helpers/tls.py` para el handshake
      TLS de `appscvsmovil.supercias.gob.ec` (mecanismo separado del de
      certificados vencidos). Extendido después con dos rondas de
      endurecimiento producto de un review externo:
      - PR [dsanchezp18/EcuDataMCP#7](https://github.com/dsanchezp18/EcuDataMCP/pull/7)
        (abierto): bug real en `get_financials` (lookup de nombre/RUC fallaba
        en silencio), refresh no atómico del build, event loop bloqueado por
        el parseo XLSX del directorio, `uv.lock` committeado + CI en
        3.11/3.12/3.13, fixes de Dockerfile/`.dockerignore`/`docker-compose.yml`.
      - PR [dsanchezp18/EcuDataMCP#8](https://github.com/dsanchezp18/EcuDataMCP/pull/8)
        (abierto, sobre el #7): guardia SSRF centralizada
        (`helpers/safe_download.py`) para descargas con URL de metadata
        externa no confiable, y desacople de `helpers/supercias_financials.py`
        respecto al directorio — la DB financiera ahora tiene su propia
        tabla `companias` cargada de `bi_compania.csv`.
      Todo esto también se mandó a upstream: PR
      [DweskZ/EcuDataMCP#6](https://github.com/DweskZ/EcuDataMCP/pull/6)
      (abierto, acumulativo — incluye directorio + financiero + las dos
      rondas de endurecimiento + auditores externos, ver abajo).
- [x] **Superintendencia de Compañías (Supercías) — registro de auditores
      externos** — PR [dsanchezp18/EcuDataMCP#9](https://github.com/dsanchezp18/EcuDataMCP/pull/9)
      (2026-08-15, abierto). Tercer dataset de Supercías, encontrado por
      Daniel (`mercadodevalores.supercias.gob.ec/reportes/auditoresExternos.jsf`),
      mismo host y mismo patrón que el directorio (export Excel estático,
      sin auth, actualizado a diario) pero mucho más chico: 1,447 filas /
      ~190 KB. Nuevos tools `search_auditores`/`get_auditor_info`.
      `_parse_xlsx` generalizado para aceptar `header_markers`
      configurables (este export usa `IDENTIFICACION` como columna de
      identificación, no `RUC`). También mandado a upstream, agregado al
      mismo PR [DweskZ/EcuDataMCP#6](https://github.com/DweskZ/EcuDataMCP/pull/6)
      acumulativo.
- [x] **Instituto Geofísico (IG-EPN)** — hecho antes de este archivo, via
      `search_sismos` + `helpers/igepn_client.py` (CHANGELOG 0.5.0,
      2026-08-10), con caché y tests (`tests/test_igepn_client.py`). PR a
      *upstream* [DweskZ/EcuDataMCP#4](https://github.com/DweskZ/EcuDataMCP/pull/4)
      **mergeado el 2026-08-12** — ya vive en ambos repos.
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
corregido en el repo. (No confundir con el bloqueo
geográfico real que sí sigue pendiente, ver "Burlar el bloqueo geográfico del
portal" arriba.)
