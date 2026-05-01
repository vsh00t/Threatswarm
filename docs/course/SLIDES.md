# Taller: Uso de Agentes de IA para Pentest Autónomo

**Ironcybersec — Contenido de Presentación**

> **Formato:** 8 horas | 4 asistentes | 80% demos en vivo, 20% teoría
> **Plataformas:** VS Code + GitHub Copilot (principal) · OpenCode + Z.AI (terminal) · Claude (limitado) · ThreatSwarm v2.0
> **Instructor:** Jorge Moya (@vSh00t) — Ironcybersec
> **Fecha:** [INSERTAR FECHA]
> **Licencia:** Contenido confidencial de Ironcybersec. No redistribuir sin autorización.

---

## Sección 1: Apertura

---

### Slide 1: Título

**Speaker Notes:**

Bienvenidos. Este no es un taller de teoría sobre IA en seguridad — es un taller donde vamos a *romper cosas* con IA. Ocho horas, mayoría en vivo, usando las mismas herramientas que estamos usando en engagements reales. Si esperaban slides con definiciones de "qué es una red neuronal", se equivocaron de taller.

Presentarme: Jorge Moya, 15+ años en ofensiva, fundador de Ironcybersec. Hoy no vengo a venderles humo — vengo a mostrarles qué funciona, qué no, y qué todavía es experimental.

Regla del taller: todo lo que hagan aquí es en entornos controlados. Las herramientas que vamos a usar son de doble filo. La responsabilidad es suya.

**Visual:** Logo de Ironcybersec centrado. Título grande. Foto o avatar del instructor. Fondo oscuro profesional.

**Content:**
- **Taller: Uso de Agentes de IA para Pentest Autónomo**
- Ironcybersec | Formación Especializada
- Instructor: Jorge Moya — @vSh00t
- 8 horas | Demos en vivo | Entornos controlados

---

### Slide 2: Agenda

**Speaker Notes:**

Ocho bloques. Cero relleno. Cada bloque tiene un objetivo claro. Vamos a arrancar con contexto — dónde está la industria en abril 2026 — y luego caer directo a MCP, que es el protocolo que hace posible todo esto. De ahí saltamos a ThreatSwarm, la herramienta que vamos a usar, y pasamos el resto del día rompiendo cosas.

Bloques 4-6 son puro demo. Van a ver pentest web completo, análisis de apps móviles con Frida, y un engagement end-to-end. Bloques 7-8 son suyos — laboratorio práctico donde ustedes operan.

Preguntas en cualquier momento. Si algo no queda claro en la demo, lo repetimos. Pero si es teoría que pueden googlear, la googlean.

**Visual:** Tabla de 8 bloques con horarios y descripciones de 1 línea cada una.

**Content:**
- **Bloque 1 (09:00–09:45):** El landscape 2026 — IA para seguridad ofensiva
- **Bloque 2 (09:45–10:45):** MCP Fundamentos — El protocolo que conecta todo
- **Bloque 3 (10:45–11:00):** Break
- **Bloque 4 (11:00–12:30):** ThreatSwarm — Arquitectura multi-agente y kill-chain con IA
- **Bloque 5 (12:30–13:30):** Almuerzo
- **Bloque 6 (13:30–15:00):** Demos en vivo — Web, Mobile, Engagement completo
- **Bloque 7 (15:00–16:30):** Hands-on — Laboratorio y ejercicios prácticos
- **Bloque 8 (16:30–17:00):** Limitaciones, roadmap y cierre

---

### Slide 3: El Landscape 2026 — Agentes de IA para Seguridad

**Speaker Notes:**

Abril 2026. El ecosistema de agentes de IA para seguridad cambió drásticamente en los últimos 6 meses. Vean lo que pasó:

GitHub Copilot evolucionó de autocompletar código a tener agentes autónomos que pueden ejecutar pentests completos, con soporte nativo para MCP servers directamente en VS Code — esta es la plataforma principal que usaremos hoy.

Anthropic lanzó Claude Code, y su propio Frontier Red Team publicó resultados usando Claude para recon autónoma, explotación en CTFs, y análisis de vulnerabilidades. Claude sigue siendo una opción válida, pero con rate limits más restrictivos que lo hacen menos práctico para sesiones largas de pentest.

OpenCode (opencode.ai, migrado a charmbracelet/crush) emergió como alternativa terminal open source — soporta múltiples proveedores incluyendo Z.AI como LLM. Es la base de frameworks como pentest-ai-agents de 0xSteph (28 subagentes especializados) y ThreatSwarm, que vamos a usar hoy como alternativa en terminal.

PortSwigger lanzó su MCP Server oficial para Burp Suite. Ahora Claude Code o cualquier cliente MCP puede hablar con Burp directamente — escaneo pasivo/activo, análisis de requests, todo via JSON-RPC. Esto es *huge*.

En la comunidad: burp-ai-agent de six2dez (53+ herramientas MCP, 62 clases de vulnerabilidad), Pentest-Swarm-AI de Armur, pentagi de vxcontrol — todos compitiendo en el mismo espacio. El momentum es real, no hype.

Pero no todo es color de rosa: White House bloqueó la expansión de Mythos (Anthropic) por riesgos nacionales de seguridad — una señal clara de que los gobiernos están asustados de lo que la IA ofensiva puede hacer.

**Visual:** Timeline vertical con logos/marcas. Flechas mostrando evolución: Claude Code (Oct 2025) → Burp MCP Server (Feb 2026) → pentest-ai-agents trending (Abr 2026) → Mythos bloqueada (Abr 2026).

**Content:**
- **VS Code + GitHub Copilot** (Microsoft/GitHub, 2025-2026) — Plataforma principal; agentes autónomos con MCP nativo, terminal integrado, Copilot Chat
- **OpenCode + Z.AI** (opencode.ai / charmbracelet/crush) — Alternativa terminal open source, Z.AI como proveedor LLM, compatible con MCP
- **Claude** (Anthropic) — Disponible pero con rate limits restrictivos; ideal para razonamiento complejo puntual
- **Burp Suite MCP Server** (PortSwigger, Feb 2026) — Integración oficial Burp ↔ AI via MCP
- **ThreatSwarm v2.0** (github.com/vsh00t/ThreatSwarm) — 32 agentes, kill-chain completo, VS Code Copilot + OpenCode + Z.AI
- **pentest-ai-agents** (0xSteph, Abr 2026) — 28 subagentes Claude Code, trending en r/cybersecurity
- **Mythos** (Anthropic) — Modelo de ciberseguridad avanzada; bloqueado por White House (Abr 2026)
- **Ecosistema MCP** — Protocolo estándar de facto para tool-calling en agentes de seguridad

---

## Sección 2: MCP Fundamentos

---

### Slide 4: ¿Qué es MCP?

**Speaker Notes:**

MCP significa Model Context Protocol. Es un protocolo abierto creado por Anthropic, y en 2026 es el estándar *de facto* para que los modelos de IA hablen con herramientas externas. Piensen en MCP como USB-C para IA — un conector universal.

La arquitectura es simple: tienes un **host** (VS Code + Copilot, OpenCode, Claude Desktop, cualquier cliente MCP) que se conecta a uno o más **servers** vía JSON-RPC 2.0. VS Code + Copilot soporta MCP servers de forma nativa desde su configuración — no requiere proxy externo. El transporte puede ser stdio (el más común — el host lanza el server como proceso hijo) o SSE (Server-Sent Events, para conexiones remotas vía HTTP).

Cada MCP server expone tres tipos de primitivas:
- **Tools:** Funciones que el agente puede ejecutar. Ejemplo: `nmap_scan`, `sqlmap_exploit`, `frida_instrument`.
- **Resources:** Datos estáticos que el agente puede leer. Ejemplo: scope files, configuraciones, diccionarios.
- **Prompts:** Plantillas de prompts predefinidos para tareas específicas.

El flujo real: el usuario le dice a Copilot en VS Code "escanea esta red". Copilot decide que necesita usar Nmap. Busca un MCP server que tenga la tool `nmap_scan`. La invoca con los parámetros correctos. El server ejecuta Nmap localmente. Devuelve los resultados. Copilot los interpreta y sugiere los siguientes pasos.

Esto es diferente a simple function calling porque MCP es *descubrible* — el agente puede listar qué tools tiene disponibles y decidir dinámicamente cuál usar. No está hardcodeado. En VS Code, Copilot descubre automáticamente los MCP servers configurados en `settings.json` o `.vscode/mcp.json`.

**Visual:** Diagrama ASCII proyectado:

```
┌─────────────────────────────────────────────────────────┐
│                     AI HOST                            │
│  (VS Code Copilot / OpenCode / Claude Desktop / etc.)  │
│                                                         │
│  User Prompt → LLM Reasoning → Tool Selection           │
└──────────┬──────────┬──────────┬───────────────────────┘
           │          │          │
      JSON-RPC 2.0  (stdio / SSE)
           │          │          │
    ┌──────▼──┐ ┌────▼────┐ ┌───▼───────┐
    │ Nmap    │ │ Burp    │ │ Frida     │
    │ MCP     │ │ MCP     │ │ MCP       │
    │ Server  │ │ Server  │ │ Server    │
    └─────────┘ └─────────┘ └───────────┘
    Tools:      Tools:      Tools:
    - scan      - proxy     - hook
    - enumerate - scan      - bypass
    - vuln      - exploit   - extract
```

**Content:**
- **MCP (Model Context Protocol)** — Protocolo abierto de Anthropic para tool-calling en IA
- **JSON-RPC 2.0** sobre stdio (local) o SSE (remoto via HTTP)
- **Tres primitivas:** Tools (ejecutar), Resources (leer), Prompts (plantillas)
- **Descubrimiento dinámico:** El agente consulta qué tools tiene disponibles
- **Múltiples servers:** Un host se conecta a N servers simultáneamente
- **Transporte stdio:** El host lanza el server como proceso hijo — más seguro, sin exposición de red
- **Transporte SSE:** Para servers remotos, expuestos via HTTP — mayor flexibilidad pero mayor superficie de ataque

---

### Slide 5: MCP en la Práctica — Ecosistema Real

**Speaker Notes:**

Ahora veamos MCP en la práctica. Esto no es teoría — son herramientas que están en producción y que vamos a usar hoy.

**Burp Suite MCP Server (PortSwigger):** En febrero 2026, PortSwigger lanzó su MCP server oficial. Es una extensión de Burp que expone tools para que cualquier cliente MCP pueda interactuar con Burp — enviar requests, analizar respuestas, ejecutar scans pasivos/activos, consultar la base de datos de Burp. Se instala como BApp, se configura el endpoint, y cualquier cliente MCP — VS Code Copilot, OpenCode, Claude — puede dirigir Burp.

**VS Code + Copilot como host MCP:** Desde 2026, VS Code soporta MCP servers de forma nativa. Puedes configurar Burp MCP, Frida MCP, o cualquier server directamente en la configuración de Copilot. El agente de Copilot descubre las tools automáticamente y puede orquestar flujos de pentest sin salir del editor. Esta es la configuración principal que usaremos en el taller.

Pero hay algo más interesante: **burp-ai-agent** de six2dez. No es solo un MCP proxy — es una extensión completa que añade 53+ tools MCP, 62 clases de vulnerabilidad con scanning pasivo y activo asistido por IA, y tres modos de privacidad (STRICT/BALANCED/OFF) que redactan datos sensibles antes de salir de Burp. Tiene audit logging con hashing SHA-256 para compliance.

**Frida MCP:** Múltiples implementaciones. FuzzySecurity publicó kahlo-mcp que expone Frida como servidor MCP para instrumentación dinámica. También existe frida-c2-mcp que permite controlar instrumentación Frida de forma remota (estilo C2). Y dnakov/frida que se enfoca en Android — SSL pinning bypass, extracción de credenciales, hook de APIs. Esto es lo que vamos a usar en la demo de mobile.

**Otros servers relevantes:** Nmap MCP (varias implementaciones comunitarias), nuclei-mcp para escaneo de templates, sqlmap-mcp para explotación SQL injection, y los tres MCP servers propios de ThreatSwarm: scope-mcp (validación de alcance), evidence-mcp (captura de evidencia), y report-mcp (generación de informes).

**Visual:** Capturas de pantalla de: (1) PortSwigger/mcp-server en GitHub, (2) burp-ai-agent de six2dez mostrando las 53 tools, (3) kahlo-mcp CLI en acción.

**Content:**
- **PortSwigger/mcp-server** (oficial, Feb 2026)
  - Extensión BApp para Burp Suite
  - Exposición de Burp via MCP (SSE + stdio proxy incluido)
  - Compatible con VS Code Copilot, Claude Desktop, OpenCode, cualquier cliente MCP
  - Repo: `github.com/PortSwigger/mcp-server`

- **VS Code Copilot como host MCP** (Microsoft, 2026)
  - Soporte nativo de MCP servers en VS Code
  - Configuración vía `settings.json` o `.vscode/mcp.json`
  - Copilot Chat descubre tools automáticamente
  - Terminal integrada para ejecución de comandos

- **burp-ai-agent** (six2dez, 2026)
  - 53+ herramientas MCP, 62 clases de vulnerabilidad
  - Scanning pasivo/activo asistido por IA
  - Modos de privacidad: STRICT / BALANCED / OFF
  - Audit logging con hashing SHA-256
  - Repo: `github.com/six2dez/burp-ai-agent`

- **Frida MCP** (ecosistema)
  - kahlo-mcp (FuzzySecurity) — instrumentación dinámica via MCP
  - frida-c2-mcp — control remoto de instrumentación Frida
  - dnakov/frida — enfoque en Android: SSL pinning bypass, credential extraction

- **ThreatSwarm MCP Servers:**
  - `scope-mcp` — validación de alcance antes de cualquier test
  - `evidence-mcp` — captura y cadena de custodia de evidencia
  - `report-mcp` — generación de informes desde hallazgos

---

### Slide 6: Seguridad del Protocolo MCP — Atacando al Conector

**Speaker Notes:**

Todo lo que conecta, también puede ser atacado. MCP no es la excepción.

Primero, el problema de la superficie de ataque: cuando un agente de IA ejecuta una tool MCP, está corriendo código en tu máquina. Si el MCP server tiene una vulnerabilidad, o si un prompt injection logra que el agente invoque tools con parámetros maliciosos, tienes un problema de seguridad real.

El incidente de **oh-my-opencode** (Feb 2026) lo ilustra perfectamente. oh-my-opencode es un harness de configuración para OpenCode que injecta prompts de sistema, AGENTS.md, y reglas contextuales. Un investigador de Cisco CX demostró que un repositorio malicioso con un README.md manipulado podía inyectar instrucciones en el prompt del agente, logrando ejecución de comandos arbitrarios. No era un bug de OpenCode — era el patrón de "leer archivos del repo y confiar en su contenido" que todos los harnesses usan. El repo ahora se llama oh-my-openagent y tiene mitigaciones, pero el vector sigue existiendo en cualquier sistema que auto-inyecte contexto de archivos no confiables.

Luego tenemos los hallazgos de **novee.security** (Abr 2026): dos vulnerabilidades críticas en agentes de IA coding.
- **CVE-2026-26268:** Cursor IDE — ejecución de código arbitraria vía git hooks. Un repositorio clonado puede ejecutar código antes de que el usuario interactúe con nada.
- **Gemini CLI CVSS 10.0:** Google Gemini CLI aceptaba contenido controlado por atacante como configuración del agente y lo ejecutaba *antes* de que el sandbox estuviera activo. Sin prompt injection, sin decisión del modelo — simplemente contenido aceptado como config.

¿Cómo auditamos MCP servers? Hay dos enfoques:

1. **appsecco/mcp-client-and-proxy** — Un proxy MCP que intercepta tráfico MCP y lo envía a Burp Suite o ZAP para análisis. Puedes inspeccionar y modificar requests/responses MCP en vuelo.

2. **MCPwned** — Extensión de Burp Suite específicamente diseñada para auditar MCP servers. Fuzzing de tools, análisis de parámetros, detección de command injection en inputs.

La lección: MCP es poderoso, pero la cadena de confianza LLM → MCP server → herramienta → sistema operativo tiene múltiples puntos de falla. El scope enforcement (que ThreatSwarm implementa) no es opcional — es esencial.

**Visual:** Diagrama de ataque: Repositorio malicioso → README.md inyectado → OpenCode lee → Prompt injection → Agente invoca tool MCP → Ejecución en host. Luego diagrama de defensa: scope-mcp como gatekeeper.

**Content:**
- **Superficie de ataque MCP:**
  - El agente ejecuta código en tu máquina via tools MCP
  - Inputs del LLM pueden ser manipulados por prompt injection
  - MCP servers comunitarios sin auditoría = riesgo real

- **oh-my-opencode incidente (Cisco CX, Feb 2026):**
  - Harness de OpenCode inyectaba contexto de archivos del repo
  - README.md manipulado → instrucciones inyectadas en el prompt
  - Ejecución de comandos arbitrarios sin interacción del usuario
  - Patrón afecta a CUALQUIER sistema que auto-injecte contexto de archivos no confiables

- **novee.security — CVEs en AI coding agents (Abr 2026):**
  - CVE-2026-26268: Cursor IDE — RCE vía git hooks en repos clonados
  - Gemini CLI CVSS 10.0 — Contenido atacante aceptado como config, ejecutado antes del sandbox

- **Auditoría de MCP servers:**
  - `appsecco/mcp-client-and-proxy` — Proxy interceptador para Burp/ZAP
  - MCPwned — Extensión de Burp para fuzzing y análisis de MCP servers

- **Mitigaciones clave:**
  - Scope enforcement obligatorio antes de cualquier tool invocation
  - Sandboxing de MCP servers (contenedores, usuarios dedicados)
  - Auditoría de prompts del sistema y auto-injected context
  - Validación estricta de parámetros en cada tool

---

## Sección 3: Agentes de Pentesting

---

### Slide 7: Arquitectura Multi-Agente — ThreatSwarm v2.0

**Speaker Notes:**

ThreatSwarm v2.0 es un framework de 32 agentes especializados para seguridad ofensiva, defensiva y recon. Funciona como plugin de VS Code + Copilot, o via OpenCode con Z.AI, o via OpenClaw. El adapter de GitHub Copilot (`adapters/github-copilot/`) existe pero es minimal — se recomienda usar la integración MCP nativa de VS Code. El diseño es simple: cada agente es un system prompt que sabe herramientas, técnicas y procedimientos específicos. El framework maneja scope enforcement, captura de evidencia, generación de reportes, y deployment multi-plataforma.

La distribución: 21 ofensivos, 7 defensivos, 2 de recon, 1 colaborativo (Purple Team), 1 de reportes. Cada uno mapeado a técnicas MITRE ATT&CK — hay 754 skills mapeadas en total.

El principio fundamental: **el agente sugiere comandos y explica trade-offs. Tú decides qué ejecutar. Nada se ejecuta sin tu aprobación.** Esto no es un bot que rompe cosas solo — es un asistente experto que acelera tu flujo de trabajo.

La arquitectura multi-agente funciona así: tienes un agente principal (el "coordinator") que recibe tu objetivo. Dependiendo del objetivo, delega a agentes especializados. El agente de recon descubre superficies de ataque. El agente de explotación evalúa vectores. El agente de post-explotación busca escalation paths. Todo con scope enforcement en cada paso — scope-mcp valida cada target antes de cualquier acción.

Los tres MCP servers nativos son clave:
- **scope-mcp:** `validate_target`, `check_scope`, `add_scope`, `list_scope`, `import_scope`
- **evidence-mcp:** `capture_evidence`, `get_evidence`, `list_evidence`, `export_evidence`
- **report-mcp:** `create_report`, `add_finding`, `generate_report`, `get_template`

El pipeline de reportes tiene 4 templates: executive_summary, technical_finding, remediation_roadmap, y client (el deliverable completo).

**Visual:** Diagrama de jerarquía de agentes:

```
                    ┌──────────────┐
                    │  COORDINATOR  │
                    │  (VS Code /   │
                    │  Copilot /    │
                    │  OpenCode)    │
                    └──────┬───────┘
                           │ delega
            ┌──────┬───────┼───────┬──────┐
            ▼      ▼       ▼       ▼      ▼
      ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐
      │ RECON   │ │ WEB     │ │ MOBILE ││ NETWORK  │
      │Specialist│ │Attacker │ │Attacker││Operator  │
      └────┬────┘ └────┬────┘ └───┬────┘ └────┬─────┘
           │           │          │           │
      ┌────▼────┐ ┌────▼────┐ ┌──▼─────┐ ┌───▼──────┐
      │ Nmap    │ │ SQLMap  │ │ Frida  │ │ Metasploit│
      │ Subfinder│ │ Burp    │ │ MobSF  │ │ SMB/Relay│
      │ Amass   │ │ Nuclei  │ │ SSL    │ │ ARP      │
      └─────────┘ └─────────┘ └────────┘ └──────────┘
                            │
                    ┌───────▼───────┐
                    │ scope-mcp     │ ← Gatekeeper
                    │ evidence-mcp  │ ← Evidence chain
                    │ report-mcp    │ ← Auto-reports
                    └───────────────┘
```

**Content:**
- **ThreatSwarm v2.0** — github.com/vsh00t/ThreatSwarm
- **32 agentes:** 21 ofensivos, 7 defensivos, 2 recon, 1 purple team, 1 reporting
- **754 skills** mapeadas a MITRE ATT&CK
- **Principio:** El agente sugiere, tú decides. Nada ejecuta sin aprobación.
- **MCP servers nativos:**
  - `scope-mcp` — 5 tools: validate, check, add, list, import scope
  - `evidence-mcp` — 4 tools: capture, get, list, export evidence
  - `report-mcp` — 4 tools: create, add finding, generate, get template
- **Multi-plataforma:** VS Code + Copilot (principal), OpenCode + Z.AI (terminal), Claude (limitado), OpenClaw (SKILL.md)
- **Pipeline de reportes:** 4 templates — executive, technical, remediation, client deliverable
- **Integraciones:** n8n workflows, OpenProject sync

---

### Slide 8: El Ciclo Kill-Chain con IA — De Recon a Report

**Speaker Notes:**

Aquí es donde la IA cambia las reglas del juego. Tradicionalmente, un pentester manual pasa por estas fases:

1. **Recon (2-4 horas):** Nmap, subfinder, amass, dnsenum, búsqueda manual de subdominios, revisión de DNS, WHOIS, etc. Mucha repetición, mucho copy-paste de resultados.

2. **Análisis (1-2 horas):** Clasificar puertos, identificar servicios, priorizar objetivos. Aquí es donde la experiencia marca la diferencia — un senior sabe qué mirar primero.

3. **Explotación (2-6 horas):** Probar vectores. SQLi, XSS, SSRF, RCE. Muchos intentos fallidos, muchos false positives.

4. **Post-explotación (1-3 horas):** Escalation, lateral movement, pivoting. Si hay AD, BloodHound, Kerberoasting, etc.

5. **Reporte (3-5 horas):** Documentar todo. CVSS scoring, evidencia, remediación, executive summary. La parte que nadie quiere hacer.

Total manual: **9-20 horas** para un engagement web estándar.

Con agentes de IA:

1. **Recon (15-30 min):** El agente ejecuta nmap, subfinder, amass automáticamente. Analiza resultados, clasifica servicios, prioriza. No se cansa, no se distrae.

2. **Análisis (5-10 min):** Claude analiza los resultados de recon y cruza con su conocimiento de vulnerabilidades comunes por servicio/versione. Sugiere vectores prioritarios.

3. **Explotación (30-90 min):** El agente corre nuclei con templates relevantes, SQLMap si detecta inputs, busca exploits con searchsploit. Sugiere payloads. Tú validas y ejecutas.

4. **Post-ex (15-45 min):** Si hay acceso, sugiere escalation paths basados en el OS y servicios detectados. BloodHound si hay AD.

5. **Reporte (automático):** evidence-mcp captura screenshots y outputs. report-mcp genera el informe con CVSS scoring y remediación.

Total asistido: **1.5-3 horas**. Factor de aceleración: **5-8x**. Y la calidad del reporte es consistente porque el template está estandarizado.

La clave: la IA no reemplaza tu criterio. Reemplaza las tareas repetitivas para que tu criterio se enfoque en lo que importa — la explotación manual y el análisis de complejidad.

**Visual:** Tabla comparativa lado a lado: Manual vs IA-Assisted. Tiempos por fase. Barra visual de aceleración.

```
FASE          MANUAL      IA-ASSISTED   SPEEDUP
─────────────────────────────────────────────────
Recon         2-4 hrs     15-30 min     5-8x
Análisis      1-2 hrs     5-10 min      8-12x
Explotación   2-6 hrs     30-90 min     3-6x
Post-ex       1-3 hrs     15-45 min     3-5x
Reporte       3-5 hrs     5-10 min      20-30x
─────────────────────────────────────────────────
TOTAL         9-20 hrs    1.5-3 hrs     5-8x
```

**Content:**
- **Kill-chain con IA — Comparativa de tiempos:**
  - Recon: 2-4h manual → 15-30 min asistido
  - Análisis: 1-2h → 5-10 min
  - Explotación: 2-6h → 30-90 min
  - Post-ex: 1-3h → 15-45 min
  - Reporte: 3-5h → 5-10 min (auto-generado)
  - **Total: 9-20h → 1.5-3h (factor 5-8x)**

- **Qué hace la IA mejor que el humano:**
  - Ejecución paralela de herramientas de recon
  - Análisis de grandes volúmenes de output (nmap -A produce cientos de líneas)
  - Cruce de datos: servicio + versión + CVE conocido
  - Generación consistente de reportes con CVSS y evidencia

- **Qué sigue requiriendo criterio humano:**
  - Decisión de explotar o reportar
  - Análisis de complejidad (business logic flaws)
  - Explotación manual de vectores no estándar
  - Evaluación de impacto real en el contexto del cliente
  - Comunicación de hallazgos al cliente

---

### Slide 9: Estado del Arte — Quién Lidera

**Speaker Notes:**

Un tour rápido por el estado del arte en abril 2026.

**Anthropic Frontier Red Team:** El equipo de seguridad interno de Anthropic publicó (Feb 2026) cómo usan Claude para tareas de red team. Claude 4.6 ejecuta recon autónoma, resuelve CTFs, analiza vulnerabilidades en código fuente, y genera PoCs. Esto no es marketing — es su propio equipo de seguridad usándolo internamente. La implicación: si Anthropic confía en Claude para su propio red team, la madurez es real.

**pentest-ai-agents (0xSteph):** 28 subagentes de Claude Code especializados en pentesting. Tendó en r/cybersecurity hace días. Lo interesante: es compatible con OpenCode — puedes correr los 28 agentes con modelos locales via Ollama. Incluye un MCP server compañero (pentest-ai) con 150+ tool wrappers y chaining automático de exploits. Repo: `github.com/0xSteph/pentest-ai-agents`.

**Semgrep AI Detection:** Semgrep lanzó detección con IA en beta (Mar 2026). Identifica IDORs y broken authorization — vulnerabilidades de lógica de negocio que los scanners tradicionales no detectan. Reportan 96% de alineación con decisiones de triaje humano. Pero aquí viene el "but": la consistencia no es perfecta. Misma vulnerabilidad, mismo código, correr Semgrep dos veces puede dar resultados diferentes. Eso es problemático si dependes de eso para compliance.

**Mythos por Anthropic:** Modelo de ciberseguridad avanzada. La White House bloqueó su expansión a 70+ empresas adicionales (Abr 2026, reportado por Bloomberg, Reuters, TNW). Razón: riesgos de seguridad nacional. Interpretación: Anthropic creó algo tan poderoso para ciberseguridad ofensiva que el gobierno dijo "no, no para todos". Esto es tanto una validación de la capacidad como una señal de advertencia sobre lo que viene.

**Pentest-Swarm-AI (Armur):** Framework alternativo con razonamiento ReAct, soporte para bug bounty, CTF, y monitoreo continuo. Go + Claude API + 7+ herramientas nativas.

**pentagi (vxcontrol):** Sistema completamente autónomo con múltiples agentes para tareas de pentesting complejas.

El mensaje: no estamos en "los primeros experimentos". Estamos en la fase de competencia y diferenciación. La pregunta ya no es "¿puede la IA hacer pentesting?" sino "¿cuál framework es el mejor para mi caso de uso?"

**Visual:** Logos de cada proyecto/herramienta mencionada, organizados por categoría: Agentes (ThreatSwarm, pentest-ai-agents, Pentest-Swarm-AI, pentagi), Integraciones (Burp MCP, Frida MCP), Investigación (Anthropic Frontier Red Team, Semgrep AI), Política (Mythos/White House).

**Content:**
- **Anthropic Frontier Red Team (Feb 2026):**
  - Claude 4.6 para recon autónoma, CTFs, análisis de vulnerabilidades
  - Uso interno — el equipo de seguridad de Anthropic confía en Claude para su propio red team

- **pentest-ai-agents (0xSteph, Abr 2026):**
  - 28 subagentes Claude Code para pentesting
  - Compatible con OpenCode + Ollama (modelos locales)
  - MCP server compañero: 150+ tool wrappers, exploit chaining automático
  - Repo: `github.com/0xSteph/pentest-ai-agents`

- **Semgrep AI Detection (Mar 2026):**
  - Detección de IDOR y broken authorization con IA
  - 96% alineación con triaje humano
  - Limitación: inconsistencia entre runs — mismo código, resultados diferentes

- **Mythos (Anthropic) — Bloqueado por White House (Abr 2026):**
  - Modelo avanzado de ciberseguridad ofensiva
  - Expansión a 70+ empresas bloqueada por riesgos nacionales
  - Señal: la IA ofensiva es tan capaz que preocupa a gobiernos

- **Otros frameworks notables:**
  - Pentest-Swarm-AI (Armur) — ReAct reasoning, Go + Claude API
  - pentagi (vxcontrol) — Sistema completamente autónomo
  - burp-ai-agent (six2dez) — 53+ MCP tools para Burp

---

## Sección 4: Demos en Vivo

---

### Slide 10: Demo 1 — Pentest Web Completo con VS Code + Copilot + ThreatSwarm

**Speaker Notes:**

Primera demo. Un pentest web completo contra DVWA (Damn Vulnerable Web Application) ejecutándose localmente. DVWA es deliberadamente vulnerable — perfecto para demostrar sin riesgos.

Vamos a ver el flujo completo: Nmap → Nuclei → SQLMap → Reporte automático. Todo orquestado por OpenCode con los agentes de ThreatSwarm.

Paso 1: Configuramos el scope en scope-mcp. `add_scope --target 192.168.1.100 --range dvwa.local`. El agente no puede tocar nada fuera de este scope. Es hardcoded.

Paso 2: Invocamos al agente de Recon. OpenCode recibe el prompt y delega al Recon Specialist. El agente ejecuta:
- `nmap -sV -sC -p- 192.168.1.100` — enumeración completa
- `nmap --script vuln 192.168.1.100` — scripts de vulnerabilidades
- Analiza resultados, clasifica servicios, sugiere siguientes pasos

Paso 3: Invocamos al agente Web Attacker. El agente:
- Corre Nuclei con templates para las tecnologías detectadas
- Detecta inputs y ejecuta SQLMap contra los formularios de DVWA
- Identifica SQL injection en el módulo de login (DVWA es literalmente eso)
- Sugiere payloads para confirmar

Paso 4: El agente captura evidencia via evidence-mcp. Screenshots de los payloads exitosos, outputs de SQLMap con la DB dump.

Paso 5: report-mcp genera el informe HTML con CVSS scores, evidencia adjunta, y recomendaciones de remediación.

Todo esto en menos de 30 minutos. Comparen con el flujo manual: al menos 4-6 horas.

**Importante:** Muestro la terminal completa. Cada comando, cada output. Nada es smoke and mirrors — si algo falla en vivo, lo debuggamos en vivo. Es parte del taller.

**Visual:** VS Code con Copilot Chat a la derecha, terminal integrada abajo, DVWA en navegador secundario.

**Content:**
- **Target:** DVWA (Damn Vulnerable Web Application) en Docker local
- **Plataforma:** VS Code + GitHub Copilot + ThreatSwarm v2.0
- **Flujo de la demo:**
  1. `scope-mcp`: `add_scope --target 192.168.1.100 --range dvwa.local`
  2. **Recon Specialist:** Nmap (-sV -sC -p-), clasificación de servicios
  3. **Web Attacker:** Nuclei templates → SQLMap → confirmación de SQLi
  4. **evidence-mcp:** Captura de screenshots y outputs
  5. **report-mcp:** Generación de informe HTML con CVSS
- **Tiempo estimado:** 20-30 minutos en vivo
- **Lo que van a ver:**
  - VS Code con Copilot Chat ejecutando comandos en tiempo real
  - Cada comando ejecutado y su resultado
  - Navegador con DVWA mostrando la explotación
  - Reporte HTML generado automáticamente

---

### Slide 11: Demo 2 — Pentest Mobile con Frida MCP

**Speaker Notes:**

Segunda demo. Pentest de una aplicación Android usando Frida MCP. Vamos a hacer las cosas que normalmente toman horas en minutos.

El setup: una app Android deliberadamente vulnerable (InsecureBankv2 o similar) corriendo en un emulator. Frida server en el device.

Con kahlo-mcp o dnakov/frida, exponemos Frida como MCP server. El agente Mobile Attacker de ThreatSwarm puede entonces:

1. **Enumerar la app:** Listar activities, services, receivers, providers. Identificar entry points.

2. **SSL Pinning Bypass:** Frida hook que intercepta las validaciones SSL y las neutraliza. En un pentest real, esto te permite inspeccionar tráfico HTTPS con Burp. En la demo, lo veremos en vivo.

3. **Extracción de credenciales:** Hook de SharedPreferences para interceptar passwords almacenados en claro. Hook de Keystore para intentar extraer claves.

4. **Root Detection Bypass:** Si la app detecta root, Frida lo bypassea. Esto es esencial para muchos pentests mobile.

5. **Hook de APIs sensibles:** Intercepta calls a crypto APIs, key storage, y network calls para capturar datos en tránsito.

Lo importante aquí: Frida por sí solo requiere escribir JavaScript hooks manualmente. Con el MCP server, el agente genera los hooks basándose en el análisis estático de la APK (que puede hacer con MobSF u apktool, también disponibles via MCP). El flujo es: analizar APK → identificar objetivos → generar hooks → inyectar → capturar evidencia.

frida-c2-mcp añade otro ángulo: control remoto de instrumentación. En un engagement real, puedes tener el device en la red del cliente y controlar la instrumentación desde tu máquina.

**Visual:** VS Code con Copilot Chat, emulador Android, terminal con Frida hooks. Burp Suite mostrando tráfico HTTPS descifrado. MobSF report en navegador.

**Content:**
- **Target:** App Android vulnerable (InsecureBankv2 o similar) en emulator
- **Plataforma:** VS Code + Copilot con Frida MCP integrado
- **Herramientas:** Frida MCP (kahlo-mcp / dnakov/frida) + ThreatSwarm Mobile Attacker
- **Flujo de la demo:**
  1. **Enumeración:** Listar activities, services, entry points de la APK
  2. **Análisis estático:** MobSF / apktool via MCP
  3. **SSL Pinning Bypass:** Frida hook para neutralizar validación SSL
  4. **Credential Extraction:** Hook de SharedPreferences y Keystore
  5. **Root Detection Bypass:** Neutralizar checks de root
  6. **API Hooking:** Intercept crypto, key storage, network calls
- **frida-c2-mcp:** Control remoto de instrumentación para engagements distribuidos
- **Tiempo estimado:** 20-25 minutos en vivo

---

### Slide 12: Demo 3 — Engagement Completo con /engage (OpenCode + Z.AI)

**Speaker Notes:**

Tercera demo. El flujo completo de engagement — de la inicialización a la entrega del informe al cliente. Para esta demo usaremos OpenCode con Z.AI como proveedor LLM, mostrando la alternativa terminal para engagements donde no necesitas la GUI de VS Code.

ThreatSwarm tiene un workflow `/engage` que orquesta todo el engagement:
1. Inicializa el proyecto con nombre del cliente
2. Importa scope (file, CIDR, URLs)
3. Ejecuta la kill-chain completa
4. Captura evidencia con chain of custody
5. Genera el reporte listo para entregar

Vamos a ejecutar `/engage` contra un lab que tiene múltiples vulnerabilidades: DVWA + una app con APIs + un servicio con credenciales débiles.

Verán cómo:
- El agente coordina automáticamente entre los especialistas
- scope-mcp valida cada target antes de cualquier acción
- evidence-mcp captura y hashea cada evidencia
- report-mcp genera un informe multi-sección (executive summary + technical findings + remediation roadmap)
- El reporte incluye CVSS scores, descripciones, pasos de reproducción, evidencia adjunta, y recomendaciones priorizadas

El output final: un archivo HTML profesional que puedes entregar directamente al cliente. No es perfecto — todavía requiere revisión humana — pero cubre el 80% del trabajo de documentación.

Después de la demo, vamos a abrir el reporte generado y analizarlo. Van a ver la estructura, el nivel de detalle, y dónde pueden necesitar ajustar manualmente.

**Visual:** OpenCode en terminal ejecutando `/engage` con Z.AI como backend. Terminal mostrando progreso por fases. Navegador con el reporte HTML final.

**Content:**
- **Workflow `/engage`** — Orquestación automática de engagement completo
- **Plataforma:** OpenCode + Z.AI (alternativa terminal)
- **Target:** Lab multi-servicio (web app + API + servicio con credenciales débiles)
- **Flujo automático:**
  1. Inicialización del proyecto
  2. Import de scope (file/CIDR/URLs)
  3. Kill-chain completa (recon → exploit → post-ex)
  4. Captura de evidencia con chain of custody (SHA-256)
  5. Generación de reporte multi-sección
- **Reporte generado:**
  - Executive Summary para C-suite
  - Technical Findings con CVSS y pasos de reproducción
  - Remediation Roadmap priorizada
  - Evidencia adjunta (screenshots, outputs)
- **Revisión:** Análisis del reporte generado — qué es bueno, qué necesita ajuste manual
- **Tiempo estimado:** 25-30 minutos en vivo

---

### Slide 13: Código Detrás — Cómo Funciona por Dentro

**Speaker Notes:**

Vamos a levantar la tapa. Quiero que entiendan cómo funciona esto por dentro, no solo cómo se usa.

Primero, un agente de ThreatSwarm. Voy a mostrar el system prompt real del Web Attacker. Verán:
- Instrucciones de herramientas disponibles (SQLMap, Nuclei, Burp, etc.)
- Instrucciones de procedimiento (qué hacer cuando encuentra una vulnerabilidad, cómo clasificar severidad)
- Reglas de scope enforcement (validar con scope-mcp antes de cualquier acción)
- Formato de output (cómo reportar hallazgos al coordinator)

Segundo, un MCP server real. Voy a mostrar el código de scope-mcp — probablemente el MCP server más simple pero más importante del framework. Van a ver:
- Definición de la tool `validate_target` con input schema
- La lógica de validación (CIDR matching, domain matching, port ranges)
- Cómo devuelve el resultado al host via JSON-RPC

Tercero, el flujo de delegación. Cómo funciona cuando el coordinator decide que necesita el agente de explotación:
1. El LLM recibe el contexto del engagement + resultados de recon
2. Genera un prompt específico para el Exploitation Specialist
3. El nuevo agente tiene acceso a las tools de explotación
4. Ejecuta, reporta hallazgos, y devuelve control al coordinator

La arquitectura es elegante porque cada agente es *stateless* — no mantiene estado entre llamadas. Todo el contexto pasa por el prompt. Esto es por diseño: evita que un agente "se vaya por la tangente" y facilite la auditoría.

**Visual:** Editor de código con tres paneles: (1) system prompt del Web Attacker, (2) código de scope-mcp server.py, (3) diagrama de flujo de delegación.

**Content:**
- **System prompt de un agente real:**
  - Definición de rol, herramientas disponibles, procedimientos
  - Reglas de scope enforcement integradas
  - Formato estandarizado de reporte de hallazgos

- **MCP Server code (scope-mcp):**
  ```python
  # Definición de tool
  @server.tool()
  def validate_target(target: str, scope_file: str = "scope.txt") -> dict:
      """Valida si un target está dentro del scope autorizado"""
      scope = load_scope(scope_file)
      is_valid = check_cidr_match(target, scope)
      return {"target": target, "in_scope": is_valid, "scope": scope}
  ```

- **Flujo de delegación:**
  - Coordinator → analiza contexto → selecciona agente → genera prompt
  - Agente especializado → ejecuta tools → reporta hallazgos
  - Resultado vuelve al coordinator para siguiente paso
  - Cada agente es stateless — todo el contexto via prompt

- **Principios de diseño:**
  - Agente sugiere, humano aprueba
  - Scope enforcement en CADA tool invocation
  - Evidencia capturada automáticamente con hash SHA-256
  - Audit trail completo de todas las acciones

---

## Sección 5: Hands-on

---

### Slide 14: Laboratorio — Setup Paso a Paso

**Speaker Notes:**

Ahora es su turno. Vamos a configurar todo desde cero. Si algo no funciona, lo resolvemos juntos.

**Prerrequisitos (que ya deberían tener):**
- Python 3.10+
- Node.js 18+
- Docker (para los labs)
- Git
- Un editor de código (VS Code)

**Paso 1: Clonar e instalar ThreatSwarm**
```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
pip install -r requirements.txt
```

**Paso 2: Configurar VS Code + GitHub Copilot**
1. Instala VS Code (code.visualstudio.com)
2. Instala la extensión GitHub Copilot
3. Configura MCP servers en `.vscode/mcp.json`:
```json
{
  "servers": {
    "scope-mcp": {
      "command": "uvx",
      "args": ["--from", "integrations/mcp/scope-mcp", "scope-mcp"]
    },
    "evidence-mcp": {
      "command": "uvx",
      "args": ["--from", "integrations/mcp/evidence-mcp", "evidence-mcp"]
    },
    "report-mcp": {
      "command": "uvx",
      "args": ["--from", "integrations/mcp/report-mcp", "report-mcp"]
    }
  }
}
```
4. Copilot descubre automáticamente los MCP servers al abrir el workspace

**Paso 3: Instalar OpenCode (alternativa terminal)**
```bash
# Via Go
GO111MODULE=on go install github.com/opencode-ai/opencode@latest
# O via npm
npm install -g opencode
```

**Paso 4: Configurar OpenCode con Z.AI**
```bash
opencode init
# Configurar Z.AI como proveedor LLM:
# Z.AI API key desde z.ai
# O usar Anthropic Claude (rate limits restrictivos)
```

**Paso 4: Generar los adapters de ThreatSwarm para OpenCode**
```bash
python3 scripts/build.py --adapter opencode
# Genera adapters/opencode/ con instructions.md y opencode.json
```

**Paso 5: Levantar los MCP servers**
```bash
uvx --from integrations/mcp/scope-mcp scope-mcp &
uvx --from integrations/mcp/evidence-mcp evidence-mcp &
uvx --from integrations/mcp/report-mcp report-mcp &
```

**Paso 6: Levantar el lab**
```bash
docker compose up -d dvwa
# DVWA disponible en http://localhost:8080
```

**Paso 7: Configurar scope**
```bash
# Escribir scope.txt
echo "192.168.1.0/24" > scope.txt
echo "localhost" >> scope.txt
echo "dvwa.local" >> scope.txt
```

**Paso 8: Primer scan**
```
# En OpenCode, ejecutar:
/recon --target localhost --port 8080
```

Si llegaron hasta aquí sin errores, están listos para los ejercicios. Si hay errores, levanten la mano — los resolvemos en vivo.

**Visual:** Terminal con los 8 pasos. Cada paso ejecutado en secuencia. Código de copia-pegar proyectado.

**Content:**
- **Prerrequisitos:** Python 3.10+, Node.js 18+, Docker, Git, VS Code
- **Paso 1:** `git clone https://github.com/vsh00t/ThreatSwarm.git && pip install -r requirements.txt`
- **Paso 2:** Instalar VS Code + Copilot, configurar MCP servers en `.vscode/mcp.json`
- **Paso 3:** Instalar OpenCode (`go install github.com/opencode-ai/opencode@latest`) como alternativa terminal
- **Paso 4:** `opencode init` — Configurar provider (Z.AI API o Claude API)
- **Paso 5:** `python3 scripts/build.py --adapter opencode` — Generar adapters
- **Paso 6:** Levantar MCP servers (scope-mcp, evidence-mcp, report-mcp)
- **Paso 7:** `docker compose up -d dvwa` — Levantar lab objetivo
- **Paso 8:** Configurar scope.txt con IPs/domains autorizados
- **Paso 9:** Primer scan — VS Code Copilot Chat o `/recon` en OpenCode

---

### Slide 15: Ejercicios Prácticos — Tres Niveles

**Speaker Notes:**

Tienen 90 minutos. Tres ejercicios, progresivos. Si completan los tres, excelente. Si solo llegan al segundo, está bien. El objetivo es que *entiendan* el flujo, no que completen todo mecánicamente.

**Ejercicio 1: Recon Scan (30 min)**
- Objetivo: Ejecutar un scan de recon completo contra el lab
- Tareas:
  1. Configurar scope con las IPs del lab
  2. Invocar al Recon Specialist
  3. Obtener: puertos abiertos, servicios, versiones
  4. Documentar los hallazgos con evidence-mcp
- Criterio de éxito: Listado completo de puertos y servicios con clasificación

**Ejercicio 2: Descubrimiento de Vulnerabilidades Web (30 min)**
- Objetivo: Encontrar y confirmar al menos 3 vulnerabilidades en DVWA
- Tareas:
  1. Invocar al Web Attacker
  2. Ejecutar Nuclei contra los servicios web detectados
  3. Confirmar SQL injection con SQLMap
  4. Capturar evidencia de cada hallazgo (screenshot + output)
- Criterio de éxito: 3 vulnerabilidades confirmadas con evidencia

**Ejercicio 3: Engagement Completo (30 min)**
- Objetivo: Ejecutar un engagement completo usando `/engage`
- Tareas:
  1. Inicializar engagement con nombre ficticio
  2. Importar scope
  3. Ejecutar kill-chain completa
  4. Revisar y ajustar el reporte generado
  5. Exportar el reporte final
- Criterio de éxito: Reporte HTML entregable con hallazgos, CVSS, y remediación

Regla: si se traban más de 10 minutos en algo, pidan ayuda. No vale quedarse 90 minutos debuggeando un path de Python.

**Visual:** Slide dividida en 3 columnas, una por ejercicio. Cada una con: objetivo, tareas checkbox, y criterio de éxito.

**Content:**
- **Ejercicio 1: Recon Scan (30 min)**
  - [ ] Configurar scope con IPs del lab
  - [ ] Invocar Recon Specialist
  - [ ] Obtener puertos, servicios, versiones
  - [ ] Capturar hallazgos con evidence-mcp
  - ✅ *Criterio: Listado completo de superficie de ataque*

- **Ejercicio 2: Vulnerabilidades Web (30 min)**
  - [ ] Invocar Web Attacker
  - [ ] Nuclei scan contra servicios detectados
  - [ ] Confirmar SQL injection con SQLMap
  - [ ] Capturar evidencia (screenshots + outputs)
  - ✅ *Criterio: 3 vulnerabilidades confirmadas con evidencia*

- **Ejercicio 3: Engagement Completo (30 min)**
  - [ ] Inicializar engagement (`/engage`)
  - [ ] Importar scope
  - [ ] Ejecutar kill-chain completa
  - [ ] Revisar y ajustar reporte generado
  - [ ] Exportar reporte HTML final
  - ✅ *Criterio: Reporte entregable con hallazgos, CVSS, remediación*

---

## Sección 6: Cierre

---

### Slide 16: Limitaciones y Riesgos — La Realidad

**Speaker Notes:**

No todo es genial. Necesitan saber dónde falla esto y cuáles son los riesgos reales.

**Hallucinaciones en seguridad:** El LLM puede inventar CVEs que no existen, sugerir exploits que no funcionan, o reportar vulnerabilidades falsas. En un pentest, un falso negativo es malo (te perdiste algo), pero un falso positivo es peor (le dices al cliente que algo está roto cuando no lo está, pierdes credibilidad). *Nunca* confíen en un hallazgo de la IA sin validación manual.

**Consistencia de Semgrep:** El research de Semgrep muestra 96% de alineación con triaje humano, pero la inconsistencia entre runs es un problema real. Misma app, mismo scanner, dos resultados diferentes. En un pentest esto significa que podrías reportar vulnerabilidades que no son consistentes — un auditor externo podría cuestionar la metodología.

**RCEs en AI agents (novee.security):** Cursor IDE tiene CVE-2026-26268 (RCE via git hooks). Gemini CLI tiene un CVSS 10.0 (ejecución antes del sandbox). Si estas herramientas que usamos todos los días tienen vulnerabilidades críticas, imagine qué puede pasar con MCP servers comunitarios sin auditoría. Cada MCP server que instalan es código que corre con sus permisos.

**Excessive agency:** El riesgo definido por OWASP LLM Top 10. Si el agente tiene demasiada autonomía, puede tomar decisiones que no你应该. En el contexto de pentesting: si scope-mcp falla o tiene un bug, el agente podría escanear targets fuera de scope. ThreatSwarm mitiga esto con validación en cada step, pero es una capa de defensa, no una garantía.

**Dependencia del modelo:** Si Anthropic cambia la API, sube precios, o deprecia funcionalidad, tu framework se rompe. Los modelos locales (Ollama) mitigan esto, pero la calidad de los modelos locales para tareas de seguridad todavía no es comparable a Claude 4.6.

**El framing legal:** Usar agentes de IA para pentesting es legal si tienes autorización. El problema es que el agente puede ser más agresivo de lo que un humano sería — podría escanear más rápido, probar más vectores, y generar más tráfico. En un engagement autorizado esto no es problema, pero si el scope no está claro, la IA puede salirse del bounds.

**Visual:** Iconos de advertencia. Lista de riesgos con severidad (crítico/alto/medio). Color coding.

**Content:**
- **Hallucinaciones de seguridad:**
  - LLM puede inventar CVEs, exploits falsos, o reportar vulnerabilidades inexistentes
  - Falsos positivos destruyen credibilidad con el cliente
  - *Mitigación:* Validación manual obligatoria de cada hallazgo

- **Inconsistencia (Semgrep research):**
  - 96% alineación con triaje humano, pero resultados variables entre runs
  - Problemático para compliance y auditorías externas
  - *Mitigación:* Runs múltiples, correlación con otras herramientas

- **Vulnerabilidades en AI agents (novee.security, Abr 2026):**
  - CVE-2026-26268: Cursor IDE — RCE via git hooks
  - Gemini CLI CVSS 10.0 — Ejecución antes del sandbox
  - *Mitigación:* Auditoría de MCP servers, sandboxing, usuarios dedicados

- **Excessive agency (OWASP LLM Top 10):**
  - Demasiada autonomía = decisiones fuera de bounds
  - Si scope enforcement falla, el agente escanea fuera de scope
  - *Mitigación:* Validación multi-capa, human-in-the-loop

- **Dependencia del modelo:**
  - Cambios de API/precios/deprecación rompen el framework
  - Modelos locales (Ollama) mitigan pero calidad inferior
  - *Mitigación:* Multi-provider support, abstracción de capa de modelo

- **Rate limits de Claude (Anthropic):**
  - Anthropic tiene los rate limits más restrictivos entre los proveedores principales
  - En sesiones largas de pentest (4+ horas), es fácil golpear los límites
  - *Mitigación:* Usar VS Code Copilot o Z.AI como proveedor principal, Claude solo para tareas puntuales de razonamiento complejo

---

### Slide 17: Roadmap 2026-2027 — Qué Viene

**Speaker Notes:**

Dónde está esto yendo en los próximos 12-18 meses.

**Corto plazo (2026 H2):**
- **Modelos locales competitivos:** Ollama ya corre Llama 4, Qwen 3, y Gemma 3. La brecha con Claude/GPT se cierra. En 6-12 meses, los modelos locales van a ser viables para tareas de pentesting sin sacrificar mucha calidad. ThreatSwarm ya soporta Ollama.
- **MCP como estándar:** El ecosistema MCP va a seguir creciendo. Más herramientas de seguridad expondrán interfaces MCP. Nmap, Metasploit, BloodHound — todos van a tener MCP servers oficiales o comunitarios.
- **CI/CD integration:** pentest-ai-agents ya tiene CI/CD integration. Esperen ver pentests automatizados que corran en cada deploy — shift-left ofensivo real.

**Mediano plazo (2027):**
- **Red team autónomo:** Un coordinator que pueda ejecutar un red team engagement completo con mínima supervisión humana. Ya es técnicamente posible — la barrera es la confianza y el framework legal.
- **Agentes multi-modelo:** Un framework que puede cambiar entre Claude, GPT, modelos locales, y modelos especializados según la tarea. El agente de crypto usa un modelo diferente al de web. Optimización de costos y calidad.
- **Evidencia con cadena de custodia digital:** Blockchain o signed logs para la evidencia capturada por agentes. Necesario si los hallazgos van a tribunal.

**Largo plazo (2027+):**
- **Modelos de ciberseguridad especializados:** Mythos (Anthropic) es el primer ejemplo. El bloqueo de la White House muestra que los gobiernos temen esto. Cuando se liberen, van a cambiar el landscape completamente.
- **Regulación:** Es inevitable. La UE ya está trabajando en AI Act enforcement para sistemas de seguridad. Estados Unidos va a seguir. El pentesting con IA va a necesitar marcos regulatorios claros.
- **Economía:** Los precios de agentes de IA van a bajar. Los costos de un pentest van a reducirse. La diferenciación va a estar en el *juicio humano*, no en la ejecución de herramientas.

**Mi predicción personal:** En 3 años, el pentesting sin IA va a ser como hacer pentesting sin Nmap — técnicamente posible, pero competitivamente inviable.

**Visual:** Timeline horizontal: 2026 H2 → 2027 → 2027+. Hitos clave marcados.

**Content:**
- **2026 H2 — Corto plazo:**
  - Modelos locales competitivos (Llama 4, Qwen 3) via Ollama
  - Ecosistema MCP explota — más herramientas con interfaces MCP
  - CI/CD pentesting automatizado (shift-left ofensivo)

- **2027 — Mediano plazo:**
  - Red team autónomo con mínima supervisión humana
  - Agentes multi-modelo (diferente modelo por tarea)
  - Evidencia con cadena de custodia digital (blockchain/signed logs)

- **2027+ — Largo plazo:**
  - Modelos de ciberseguridad especializados (post-Mythos)
  - Regulación de IA en seguridad (EU AI Act, US frameworks)
  - Diferenciación por juicio humano, no por ejecución de herramientas

- **Predicción:** En 3 años, pentesting sin IA = pentesting sin Nmap

---

### Slide 18: Recursos y Cierre

**Speaker Notes:**

Última slide. Aquí tienen todo lo que necesitan para seguir después del taller.

**Repositorios clave:**
- ThreatSwarm: `github.com/vsh00t/ThreatSwarm` — El framework que usamos hoy
- pentest-ai-agents: `github.com/0xSteph/pentest-ai-agents` — 28 subagentes Claude Code
- PortSwigger MCP: `github.com/PortSwigger/mcp-server` — MCP oficial de Burp Suite
- burp-ai-agent: `github.com/six2dez/burp-ai-agent` — 53+ tools MCP para Burp
- Pentest-Swarm-AI: `github.com/Armur-Ai/Pentest-Swarm-AI` — Alternativa con ReAct
- pentagi: `github.com/vxcontrol/pentagi` — Sistema autónomo multi-agente
- appsecco/mcp-client-and-proxy — Proxy MCP para auditoría con Burp/ZAP

- **Documentación:**
  - `modelcontextprotocol.io` — MCP Spec oficial
  - `code.visualstudio.com/docs/copilot` — VS Code Copilot + MCP docs
  - `opencode.ai/docs` — OpenCode docs y ecosystem
  - `z.ai` — Z.AI LLM provider (proveedor para OpenCode)
  - `docs.anthropic.com/claude-code` — Claude Code reference (limitado por rate limits)

**Lectura recomendada:**
- Anthropic Frontier Red Team blog (Feb 2026) — Uso de Claude para security testing
- Semgrep AI Detection research (Mar 2026) — 96% accuracy, consistency issues
- novee.security advisories — CVE-2026-26268 (Cursor), Gemini CLI CVSS 10.0
- OWASP LLM Top 10 (2025) — Excessive agency, prompt injection, supply chain
- MITRE ATLAS — Framework de adversarial ML para seguridad

**Comunidades:**
- r/cybersecurity — Pentest AI agents trending
- r/AnthropicAI — Claude Code tips y tricks
- Discord OpenCode — Soporte y discusión

**Cierre:**

El pentesting con IA no es el futuro — es el presente. La pregunta no es si van a usar agentes de IA en sus engagements, sino cuándo y con qué framework. Hoy vieron cómo ThreatSwarm puede acelerar un pentest 5-8x. Pero recuerden: la herramienta es tan buena como el operador. La IA no reemplaza su criterio — lo amplifica.

Ahora, preguntas. Tienen el resto de la sesión y mis contactos.

**Visual:** Slide limpia con links organizados por categoría. Logo de Ironcybersec. QR code con los repos.

**Content:**
- **Repositorios:**
  - `github.com/vsh00t/ThreatSwarm` — Framework principal (este taller)
  - `github.com/0xSteph/pentest-ai-agents` — 28 subagentes Claude Code
  - `github.com/PortSwigger/mcp-server` — Burp Suite MCP oficial
  - `github.com/six2dez/burp-ai-agent` — 53+ tools MCP para Burp
  - `github.com/Armur-Ai/Pentest-Swarm-AI` — ReAct reasoning framework
  - `github.com/vxcontrol/pentagi` — Sistema autónomo multi-agente
  - `github.com/appsecco/mcp-client-and-proxy` — MCP audit proxy

- **Documentación:**
  - `modelcontextprotocol.io` — MCP Spec oficial
  - `code.visualstudio.com/docs/copilot` — VS Code Copilot + MCP
  - `opencode.ai/docs` — OpenCode docs y ecosystem
  - `z.ai` — Z.AI LLM provider
  - `docs.anthropic.com/claude-code` — Claude Code reference

- **Lectura:**
  - Anthropic Frontier Red Team blog (Feb 2026)
  - Semgrep AI Detection research (Mar 2026)
  - novee.security advisories (CVE-2026-26268, Gemini CLI)
  - OWASP LLM Top 10 (2025) — MITRE ATLAS

- **Contacto:**
  - Jorge Moya — @vSh00t
  - Ironcybersec — `ironcybersec.com`
  - `jorge@ironcybersec.com`

---

## Notas del Instructor (no proyectar)

### Preparación del Entorno

- [ ] Docker con DVWA levantado y verificado (`docker compose up -d`)
- [ ] VS Code con GitHub Copilot instalado y configurado
- [ ] OpenCode instalado con Z.AI API key (alternativa terminal)
- [ ] Claude API key disponible (uso limitado, rate limits restrictivos)
- [ ] ThreatSwarm clonado, dependencias instaladas, adapters generados
- [ ] MCP servers levantados (scope, evidence, report)
- [ ] Emulador Android con InsecureBankv2 (para demo mobile)
- [ ] Frida server corriendo en el emulator
- [ ] Proyector con resolución suficiente para terminal
- [ ] Backup de todo el entorno en caso de fallas

### Timing

- Bloques de demo son flexibles — si algo falla, adaptar en vivo
- Breaks: uno oficial (10:45-11:00), otro implícito en el almuerzo
- Q&A integrado — no esperar al final
- Si se acaba el tiempo, priorizar: Demos > Hands-on > Teoría

### Fallbacks

- Si VS Code Copilot falla → OpenCode + Z.AI en terminal
- Si OpenCode falla → Claude Code CLI directo (rate limits limitan sesiones largas)
- Si Z.AI tiene problemas → Claude API (limitado) o Ollama local (Llama 4 o Qwen 3)
- Si Docker falla → VMs preconfiguradas
- Si la red falla → Todo es local, no debería ser problema

### Material Post-Taller

- Repo de ThreatSwarm con notas del taller en docs/course/
- Screenshots de las demos
- Ejercicios resueltos
- Reportes generados como ejemplo
