# ThreatSwarm v2.0 — Guía de Configuración y Uso con OpenCode

> **Versión 2.0** · Multi-Agent Pentesting Framework · 32 agentes especializados

---

## Tabla de Contenidos

- [1. Introducción](#1-introducción)
  - [1.1 Qué es ThreatSwarm v2.0](#11-qué-es-threatswarm-v20)
  - [1.2 Qué es OpenCode](#12-qué-es-opencode)
  - [1.3 Arquitectura del framework](#13-arquitectura-del-framework)
  - [1.4 Requisitos previos](#14-requisitos-previos)
- [2. Instalación desde Cero](#2-instalación-desde-cero)
  - [2.1 Instalar OpenCode](#21-instalar-opencode)
  - [2.2 Clonar ThreatSwarm](#22-clonar-threatswarm)
  - [2.3 Configurar API Keys](#23-configurar-api-keys)
  - [2.4 Generar adaptadores](#24-generar-adaptadores)
  - [2.5 Configurar MCP Servers](#25-configurar-mcp-servers)
  - [2.6 Verificar instalación](#26-verificar-instalación)
- [3. Configuración Detallada de OpenCode](#3-configuración-detallada-de-opencode)
  - [3.1 Archivo .opencode.json](#31-archivo-opencodejson)
  - [3.2 INSTRUCTIONS.md](#32-instructionsmd)
  - [3.3 Selección de modelo](#33-selección-de-modelo)
  - [3.4 Session Management](#34-session-management)
  - [3.5 Non-interactive Mode](#35-non-interactive-mode)
- [4. Uso Operativo — Manual de Uso](#4-uso-operativo--manual-de-uso)
  - [4.1 Comandos disponibles](#41-comandos-disponibles)
  - [4.2 Delegación a agentes especialistas](#42-delegación-a-agentes-especialistas)
  - [4.3 Gestión de scope](#43-gestión-de-scope)
  - [4.4 Captura de evidencia](#44-captura-de-evidencia)
  - [4.5 Generación de reportes](#45-generación-de-reportes)
  - [4.6 Flujo de trabajo completo](#46-flujo-de-trabajo-completo)
- [5. Casos de Uso](#5-casos-de-uso)
  - [5.1 Pentesting web — OWASP Top 10](#51-pentesting-web--owasp-top-10)
  - [5.2 Active Directory — Red Team](#52-active-directory--red-team)
  - [5.3 Infraestructura Cloud (AWS)](#53-infraestructura-cloud-aws)
  - [5.4 Respuesta a incidentes](#54-respuesta-a-incidentes)
  - [5.5 Wireless Assessment](#55-wireless-assessment)
  - [5.6 Mobile Application Testing](#56-mobile-application-testing)
  - [5.7 Compliance Scanning](#57-compliance-scanning)
  - [5.8 Integración con n8n](#58-integración-con-n8n)
- [6. Referencia Rápida](#6-referencia-rápida)
  - [6.1 Comandos slash](#61-comandos-slash)
  - [6.2 Agentes por categoría](#62-agentes-por-categoría)
  - [6.3 Herramientas CLI del framework](#63-herramientas-cli-del-framework)
  - [6.4 MCP Server Tools](#64-mcp-server-tools)
- [7. Solución de Problemas](#7-solución-de-problemas)
- [8. Changelog y Versión](#8-changelog-y-versión)

---

## 1. Introducción

### 1.1 Qué es ThreatSwarm v2.0

ThreatSwarm es un framework de pentesting multi-agente que provee a agentes de IA (coding assistants) conocimiento ofensivo, defensivo y de recon el nivel de un pentester profesional. Cada agente es un prompt de sistema especializado que conoce herramientas, técnicas y metodología específica de seguridad ofensiva.

**Principio fundamental:** El agente sugiere comandos y explica alternativas. Tú decides qué ejecutar. Nada se ejecuta sin tu aprobación.

**Distribución de agentes (32 total):**

| Tipo | Cantidad |
|------|----------|
| Ofensivos | 21 |
| Defensivos | 7 |
| Reconocimiento | 2 |
| Colaborativos | 1 |
| Reportes | 1 |

### 1.2 Qué es OpenCode

[OpenCode](https://github.com/opencode-ai/opencode) es un agente de IA para terminal, escrito en Go, que soporta múltiples modelos (Anthropic Claude, OpenAI GPT, Google Gemini, Ollama para modelos locales) mediante un sistema de proveedores configurable. A diferencia de Claude Code, OpenCode es agnóstico al proveedor y permite alternar modelos en runtime.

**Ventajas de usar OpenCode con ThreatSwarm:**

- **Agnosticismo de modelo:** Usa Claude Sonnet/Opus para tareas complejas, Haiku/GPT-4o-mini para enumeración rápida, o modelos locales vía Ollama
- **MCP Servers:** Protocolo Model Context Protocol para herramientas especializadas (scope, evidencia, reportes)
- **Sesiones persistentes:** Mantiene contexto entre sesiones con auto-compact
- **Modo no-interactivo:** Ideal para scripts y CI/CD pipelines
- **Zero Docker:** No requiere contenedores, corre directamente con Python stdlib

### 1.3 Arquitectura del framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OpenCode (Runtime)                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  instructions.md (System Prompt)             │    │
│  │  32 agentes especializados · Workflow de engagement          │    │
│  │  Reglas OPSEC · Formato de evidencia · Anti-patrones        │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         │                                           │
│            ┌────────────┼────────────┐                              │
│            ▼            ▼            ▼                              │
│  ┌──────────────┐ ┌──────────┐ ┌───────────┐                      │
│  │  scope-mcp   │ │ evidence │ │ report-mcp│  ← MCP Servers        │
│  │  (validación)│ │   -mcp   │ │ (reportes)│      (stdio)         │
│  │              │ │(evidencia)│ │           │                       │
│  └──────┬───────┘ └────┬─────┘ └─────┬─────┘                      │
│         │              │             │                              │
│  ───────┴──────────────┴─────────────┴──────                       │
│         │          Sistema de Archivos                             │
│         ▼                                                           │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐    │
│  │scope.txt │  │ evidence/  │  │ reports/ │  │core/agents/  │    │
│  │          │  │YYYYMMDD/   │  │          │  │32 .md files  │    │
│  │IP/CIDR/  │  │  TARGET/   │  │*.md/html │  │+ _registry   │    │
│  │domain    │  │  findings  │  │          │  │              │    │
│  └──────────┘  └────────────┘  └──────────┘  └──────────────┘    │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                    .opencode.json (Config)                          │
│  providers · agents · mcpServers · shell · autoCompact              │
└─────────────────────────────────────────────────────────────────────┘

          │
          ▼
   Model Provider API
   (Anthropic / OpenAI / Google / Ollama)
```

**Estructura de directorios del proyecto:**

```
ThreatSwarm/
├── core/                        # Definiciones de agentes y lógica compartida
│   ├── agents/                  # 32 archivos .md de agentes + _registry.json
│   ├── scripts/                 # Utilidades Python (report_generate, scope_validate)
│   ├── hooks/                   # Captura de evidencia, validación de scope
│   ├── templates/               # Plantillas de reporte (exec, technical, remediation)
│   └── lib/                     # Librerías compartidas (scope_lib, etc.)
├── adapters/                    # Salida por plataforma (generado por build.py)
│   ├── claude-code/             # Adaptador Claude Code
│   ├── github-copilot/          # Adaptador GitHub Copilot
│   ├── opencode/                # ★ Adaptador OpenCode (esta guía)
│   │   ├── instructions.md      # System prompt principal
│   │   ├── .opencode.json       # Configuración de OpenCode
│   │   ├── .opencode.json.template  # Template para nueva instalación
│   │   ├── opencode.json        # Metadata del adaptador
│   │   └── setup.sh             # Script de instalación automática
│   └── openclaw/                # Adaptador OpenClaw
├── integrations/                # Integraciones con herramientas externas
│   ├── mcp/                     # MCP servers (scope, evidence, report)
│   │   ├── scope-mcp/server.py
│   │   ├── evidence-mcp/server.py
│   │   └── report-mcp/server.py
│   ├── n8n/                     # Templates de workflow
│   └── openproject/             # Sync con gestión de proyectos
├── scripts/
│   ├── build.py                 # Sistema de build de adaptadores
│   └── smoke_test.sh            # Suite de verificación
├── reports/                     # Reportes generados
├── evidence/                    # Evidencia capturada por engagement
├── scope.txt                    # Scope del engagement activo
├── instructions.md              # (copiado del adapter) System prompt
└── .opencode.json               # (copiado del adapter) Configuración
```

### 1.4 Requisitos previos

| Requisito | Versión mínima | Notas |
|-----------|---------------|-------|
| **Python** | 3.9+ | Para scripts de build, MCP servers, reportes |
| **OpenCode** | latest | Instalado via Homebrew o Go |
| **Git** | 2.30+ | Para clonar el repositorio |
| **API Key** | — | Anthropic, OpenAI, o Google (al menos una) |
| **Herramientas de pentesting** | varias | Instaladas según necesidad (Nmap, SQLMap, etc.) |
| **uvx** | opcional | Para ejecutar MCP servers via `uv` |

**Herramientas de pentesting referencedas por los agentes (instalar según necesidad):**

```bash
# Reconocimiento
nmap, subfinder, amass, httpx, feroxbuster, nuclei

# Explotación web
sqlmap, burpsuite, nikto, whatweb

# Active Directory
impacket, bloodhound-python, netexec, responder

# Post-explotación
metasploit (msfconsole, msfvenom), sliver-client, hashcat, hydra

# Análisis
ghidra, frida, mobsf

# Red
bettercap, tshark

# Cloud
pacu, prowler, scoutsuite
```

> **Nota:** ThreatSwarm no instala estas herramientas automáticamente. Son externas al framework y se instalan por separado según el tipo de engagement.

---

## 2. Instalación desde Cero

### 2.1 Instalar OpenCode

**Opción 1: Homebrew (macOS/Linux)**

```bash
brew install opencode-ai/tap/opencode
```

**Opción 2: Go install (cualquier plataforma con Go)**

```bash
go install github.com/opencode-ai/opencode@latest
```

**Opción 3: Script de instalación oficial**

```bash
curl -fsSL https://opencode.ai/install | bash
```

**Verificar instalación:**

```bash
opencode --version
# Salida esperada: opencode v0.x.x (o similar)
```

### 2.2 Clonar ThreatSwarm

```bash
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
```

**Estructura verificada:**

```bash
# Verificar estructura del repositorio
ls -la
# Salida esperada:
# CLAUDE.md  CONTRIBUTING.md  LICENSE  README.md
# adapters/  core/  evidence/  integrations/  reports/
# scripts/  scope.txt

# Contar agentes
ls core/agents/*.md | grep -v _registry | wc -l
# Salida esperada: 32
```

### 2.3 Configurar API Keys

OpenCode lee las API keys desde variables de entorno. Configura al menos un proveedor:

**Anthropic (Claude):**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**OpenAI (GPT):**

```bash
export OPENAI_API_KEY="sk-..."
```

**Google (Gemini):**

```bash
export GOOGLE_API_KEY="AIza..."
```

**Para persistencia, agregar a tu shell:**

```bash
# Agregar a ~/.zshrc o ~/.bashrc
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

**Configuración de proveedores en .opencode.json:**

```json
{
  "providers": {
    "anthropic": {
      "disabled": false
    },
    "openai": {
      "disabled": false
    }
  }
}
```

Para deshabilitar un proveedor, cambia `"disabled"` a `true`.

### 2.4 Generar adaptadores

El script de build lee `core/agents/` y genera la salida específica para cada plataforma:

```bash
# Generar TODOS los adaptadores (incluye sync a directorios raíz)
python3 scripts/build.py --all

# Generar solo el adaptador de OpenCode
python3 scripts/build.py --adapter opencode

# Listar adaptadores disponibles
python3 scripts/build.py --list
```

**Qué genera `--all`:**

```
✅ Claude Code    → .claude/agents/ (32 archivos con frontmatter)
✅ GitHub Copilot  → threatswarm-plugin/agents/ (32 archivos)
✅ OpenCode        → (instructions.md ya existe, se sincroniza)
✅ OpenClaw        → adapters/openclaw/skills/ (32 SKILL.md)
✅ Sync root       → Copia CLAUDE.md → .claude/CLAUDE.md
```

### 2.5 Configurar MCP Servers

Los tres MCP servers proveen herramientas especializadas que OpenCode consume via protocolo stdio:

```
┌──────────────┐     JSON-RPC 2.0 (stdio)     ┌──────────────┐
│   OpenCode   │ ◄────────────────────────────► │  scope-mcp   │
│              │                                │  evidence-mcp│
│              │                                │  report-mcp  │
└──────────────┘                                └──────────────┘
```

**Método 1: Configuración automática (recomendado)**

```bash
bash adapters/opencode/setup.sh
```

Este script:
1. Verifica que OpenCode esté instalado
2. Verifica Python 3
3. Compila los tres MCP servers
4. Crea `.opencode.json` desde el template
5. Crea `instructions.md` desde el adaptador

**Método 2: Configuración manual**

Copia los archivos del adaptador al raíz del proyecto:

```bash
# Copiar configuración de OpenCode
cp adapters/opencode/.opencode.json.template .opencode.json
cp adapters/opencode/instructions.md ./
```

La configuración MCP en `.opencode.json` queda así:

```json
{
  "mcpServers": {
    "threatswarm-scope": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/scope-mcp/server.py"],
      "env": []
    },
    "threatswarm-evidence": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/evidence-mcp/server.py"],
      "env": []
    },
    "threatswarm-report": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/report-mcp/server.py"],
      "env": []
    }
  }
}
```

**Verificar MCP servers individualmente:**

```bash
# Compilar cada servidor para verificar que no hay errores de sintaxis
python3 -c "import py_compile; py_compile.compile('integrations/mcp/scope-mcp/server.py', doraise=True)"
python3 -c "import py_compile; py_compile.compile('integrations/mcp/evidence-mcp/server.py', doraise=True)"
python3 -c "import py_compile; py_compile.compile('integrations/mcp/report-mcp/server.py', doraise=True)"
# Salida esperada: sin errores (silencio = éxito)
```

**Probar scope-mcp (envío manual de JSON-RPC):**

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"scope_list","arguments":{}}}' \
  | python3 integrations/mcp/scope-mcp/server.py 2>/dev/null
```

### 2.6 Verificar instalación

Ejecuta la suite de verificación completa:

```bash
bash scripts/smoke_test.sh
```

**Salida esperada:**

```
╔══════════════════════════════════════════════════╗
║     ThreatSwarm v2.0 — Smoke Test Suite          ║
╚══════════════════════════════════════════════════╝

── Core Agents (32) ──
  ✅ 32 agent files in core/agents/
  ✅ 32 agent files in .claude/agents/
  ✅ 32 agent files in threatswarm-plugin/agents/
  ✅ All agents have valid frontmatter

── Build System ──
  ✅ build.py --list works
  ✅ build.py --all works

── Python Scripts ──
  ✅ core/hooks/evidence_capture.py compiles
  ✅ core/hooks/findings_sync.py compiles
  ✅ core/hooks/scope_check.py compiles
  ✅ core/scripts/report_generate.py compiles
  ✅ core/scripts/scope_validate.py compiles

── MCP Servers ──
  ✅ scope-mcp compiles
  ✅ evidence-mcp compiles
  ✅ report-mcp compiles

── Hooks ──
  ✅ scope_check blocks out-of-scope
  ✅ scope_check allows in-scope (exit 0)

── Report Pipeline ──
  ✅ report_generate.py produces CRITICAL (not INFO)
```

**Si algún check falla**, revisa la sección [7. Solución de Problemas](#7-solución-de-problemas).

**Primer comando en OpenCode:**

```bash
opencode
# Dentro de OpenCode, escribe:
# "Verifica que scope.txt está configurado correctamente"
# → OpenCode debería leer scope.txt y reportar los targets activos
```

---

## 3. Configuración Detallada de OpenCode

### 3.1 Archivo .opencode.json

El archivo `.opencode.json` en la raíz del proyecto controla toda la configuración de OpenCode para ese workspace. Aquí la explicación de cada campo:

> **Nota:** Los bloques de código siguientes usan formato JSONC (JSON con comentarios `//`) para facilitar la lectura. Al crear tu archivo `.opencode.json` real, **elimina los comentarios** o usa un parser que los soporte.

```jsonc
{
  // ── Proveedores de modelo ──────────────────────────────────────
  "providers": {
    "anthropic": {
      "disabled": false       // Habilita Claude (Sonnet, Opus, Haiku)
    },
    "openai": {
      "disabled": false       // Habilita GPT-4o, GPT-4o-mini
    }
    // Para Gemini u Ollama, agregar sección correspondiente
    // "google": { "disabled": false },
    // "ollama": { "disabled": false }
  },

  // ── Configuración de agentes internos ──────────────────────────
  "agents": {
    "coder": {
      "model": "claude-sonnet-4-20250514",  // Modelo para tareas de coding
      "maxTokens": 8000                      // Tokens máximos por respuesta
    },
    "task": {
      "model": "claude-sonnet-4-20250514",  // Modelo para tareas generales
      "maxTokens": 8000
    }
  },

  // ── Shell ──────────────────────────────────────────────────────
  "shell": {
    "path": "/bin/bash",        // Shell para ejecutar comandos
    "args": ["-l"]              // Argumentos (-l = login shell, carga .bash_profile)
  },

  // ── MCP Servers ────────────────────────────────────────────────
  "mcpServers": {
    "threatswarm-scope": {
      "type": "stdio",                                  // Transporte: stdio
      "command": "python3",                              // Comando ejecutable
      "args": ["integrations/mcp/scope-mcp/server.py"],  // Argumentos
      "env": []                                          // Variables de entorno adicionales
    },
    "threatswarm-evidence": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/evidence-mcp/server.py"],
      "env": []
    },
    "threatswarm-report": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/report-mcp/server.py"],
      "env": []
    }
  },

  // ── Auto-compactación ─────────────────────────────────────────
  "autoCompact": true   // Compacta automáticamente el contexto cuando se llena
}
```

**Ejemplo con proveedor adicional (Google Gemini):**

```jsonc
{
  "providers": {
    "anthropic": { "disabled": false },
    "openai": { "disabled": false },
    "google": { "disabled": false }
  },
  "agents": {
    "coder": { "model": "claude-sonnet-4-20250514", "maxTokens": 8000 },
    "task": { "model": "gemini-2.5-pro", "maxTokens": 8000 }
  },
  "shell": { "path": "/bin/bash", "args": ["-l"] },
  "mcpServers": {
    "threatswarm-scope": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/scope-mcp/server.py"],
      "env": []
    },
    "threatswarm-evidence": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/evidence-mcp/server.py"],
      "env": []
    },
    "threatswarm-report": {
      "type": "stdio",
      "command": "python3",
      "args": ["integrations/mcp/report-mcp/server.py"],
      "env": []
    }
  },
  "autoCompact": true
}
```

### 3.2 INSTRUCTIONS.md

El archivo `instructions.md` es el system prompt principal que OpenCode carga automáticamente al iniciar en el directorio del proyecto. Contiene:

- **Identidad del framework:** ThreatSwarm como operador multi-capabilidad
- **Reglas de scope:** Verificación obligatoria antes de cualquier comando de red
- **Workflow de ataque:** 5 fases (Setup → Recon → Attack → Post-Ex → Report)
- **Delegación a agentes:** Tabla de ruteo por categoría de ataque
- **Reglas OPSEC:** Proxychains, timing, manejo de evidencia
- **Anti-patrones:** Lista de cosas que NUNCA debe hacer el agente
- **Instrucciones de compactación:** Qué preservar cuando el contexto se compacta

**Cómo OpenCode carga las instrucciones:**

1. Al iniciar (`opencode`), lee `instructions.md` del directorio actual
2. Lo inyecta como system prompt del modelo
3. El modelo usa esta información para todas las decisiones subsiguientes
4. Cuando el contexto se compacta, las instrucciones de compactación indican qué preservar

**Ubicación:** El archivo se copia desde `adapters/opencode/instructions.md` a la raíz del proyecto durante la instalación.

### 3.3 Selección de modelo

ThreatSwarm recomienda diferentes modelos según el tipo de tarea:

| Tarea | Modelo recomendado | Razón |
|-------|-------------------|-------|
| Reconocimiento, enumeración, OSINT | Haiku / GPT-4o-mini | Rápido, económico, suficiente para tareas repetitivas |
| Análisis ofensivo/defensivo, orquestación | Sonnet | Balance entre velocidad y razonamiento |
| Explotación, evasión, reverse engineering | Opus | Máximo razonamiento para tareas complejas |
| Generación de reportes | Haiku / Sonnet | Formato y estructura, no requiere razonamiento profundo |

**Configurar modelo por defecto en .opencode.json:**

```jsonc
{
  "agents": {
    "coder": {
      "model": "claude-sonnet-4-20250514",   // Claude Sonnet para coding
      "maxTokens": 8000
    },
    "task": {
      "model": "claude-sonnet-4-20250514",   // Claude Sonnet para tareas
      "maxTokens": 8000
    }
  }
}
```

**Cambiar modelo en runtime:**

Dentro de OpenCode, puedes solicitar el cambio de modelo directamente en la conversación:

```
> Usa Opus para esta tarea de explotación
> Cambia a Haiku para la enumeración rápida
```

O usar el comando `/model` de OpenCode (si está disponible en tu versión).

### 3.4 Session Management

OpenCode mantiene sesiones persistentes que preservan contexto entre ejecuciones:

```bash
# Iniciar OpenCode (crea o retoma sesión)
opencode

# Listar sesiones disponibles (dentro de OpenCode)
/sessions

# Cambiar a otra sesión
/session switch <session-id>

# Crear nueva sesión
/session new

# Renombrar sesión actual
/session rename "engagement-cliente-x"
```

**Auto-compact:**

Cuando el contexto de conversación se acerca al límite de tokens del modelo, OpenCode compacta automáticamente (si `autoCompact: true` está habilitado en `.opencode.json`). ThreatSwarm incluye instrucciones específicas para que la compactación preserve:

- Lista de targets y scope entries
- Hallazgos abiertos con su severidad
- Rutas de archivos de evidencia (no el contenido crudo)
- Fase actual del engagement (recon/exploit/post-ex/report)
- Sesiones activas y niveles de acceso obtenidos

### 3.5 Non-interactive Mode

OpenCode soporta ejecución no-interactiva para integración con scripts y pipelines de CI/CD:

```bash
# Ejecutar un prompt y obtener la respuesta directamente
opencode -p "Escanea el target 192.168.1.100 con nmap -sS -T4"

# Redirigir salida a archivo
opencode -p "Genera resumen ejecutivo del engagement" > report_summary.txt

# Usar en un script de bash
#!/bin/bash
opencode -p "Valida que 10.0.0.50 esté en scope" 2>&1 | grep -q "in scope" && \
  echo "Target autorizado" || echo "Target fuera de scope"
```

**Ejemplo de integración con CI/CD:**

```bash
#!/bin/bash
# Pipeline de CI/CD para verificación de scope y reporte
set -euo pipefail

cd /path/to/ThreatSwarm

# 1. Validar scope
echo "Validando scope..."
python3 core/scripts/scope_validate.py --scope-file scope.txt

# 2. Ejecutar reconocimiento via OpenCode (non-interactive)
echo "Ejecutando reconocimiento..."
opencode -p "Ejecuta reconocimiento completo contra los targets en scope.txt con nmap -sS -T4"

# 3. Generar reporte
echo "Generando reporte..."
python3 core/scripts/report_generate.py generate \
  --type full \
  --evidence-dir ./evidence \
  --output ./reports \
  --format markdown

echo "Pipeline completado. Reporte en ./reports/"
```

---

## 4. Uso Operativo — Manual de Uso

### 4.1 Comandos disponibles

ThreatSwarm define un conjunto de comandos de alto nivel que activan workflows específicos. Dentro de OpenCode, escribe el comando como un mensaje natural:

#### `/engage` — Iniciar Engagement

Activa la fase de preparación del engagement:

```
> /engage cliente-banco-central
```

**Acciones automáticas:**
1. Lee y valida `scope.txt`
2. Crea directorio de evidencia: `evidence/20260430/TARGET/`
3. Inicializa `findings.md` en el directorio de evidencia
4. Configura variables de entorno (`LHOST`, `LPORT`, `DOMAIN`, `DC_IP`)
5. Comienza fase de reconocimiento

**Ejemplo de conversación:**

```
> /engage cliente-banco-central scope: 10.0.0.0/24, dc01.banco.local

ThreatSwarm: Engagement iniciado.
─────────────────────────────────
Scope verificado:
  • 10.0.0.0/24 (256 hosts)
  • dc01.banco.local

Evidencia: evidence/20260430/
Variables: LHOST=10.10.14.1, LPORT=4444

Iniciando reconocimiento...

¿Proceder con escaneo SYN (-sS -T4) contra 10.0.0.0/24?
```

#### `/attack` — Ejecutar Vector de Ataque

Activa la fase de explotación según hallazgos de recon:

```
> /attack web sqli en app.banco.local:8080
```

**Delegación automática según el vector:**

| Vector | Agente activado |
|--------|----------------|
| SQL injection, XSS, SSRF | `web-attacker` |
| AD, Kerberos, BloodHound | `active-directory` |
| SMB, RDP, SSH exploits | `exploit` |
| APIs REST/GraphQL | `api-attacker` |
| Contenedores Docker/K8s | `container-attacker` |
| Cloud AWS/Azure/GCP | `cloud-attacker` |

**Ejemplo:**

```
> /attack web-attacker explota SQL injection en /api/v1/users?id=1

ThreatSwarm → web-attacker: Objetivo identificado.
─────────────────────────────────────────────────
Parámetro vulnerable: id (GET, /api/v1/users)
Técnica sugerida: SQLMap con tamper scripts para WAF

Comando propuesto:
  sqlmap -u "http://app.banco.local:8080/api/v1/users?id=1" \
    --batch --risk=2 --level=3 \
    --tamper=space2comment,between \
    --dbs

¿Ejecutar? (sí/no/Modificar)
```

#### `/hunt` — Threat Hunting

Activa el agente de threat hunting para análisis de detección:

```
> /hunt beacon detection en segmento 10.0.5.0/24
```

**Ejemplo:**

```
> /hunt búsqueda de beacons Cobalt Strike en logs de firewall

ThreatSwarm → threat-hunter: Iniciando hunt.
──────────────────────────────────────────────
Hipótesis: Existen beacons de C2 activos en la red interna

Queries Splunk sugeridas:
  index=firewall (dest_port=443 OR dest_port=8443) 
    | bin _time span=1m 
    | stats avg(bytes_out) as avg_out, stdev(bytes_out) as std_out by src_ip 
    | where avg_out > 500 AND std_out < 50
    | sort -avg_out

Técnicas ATT&CK: T1071.001 (Application Layer Protocol: Web Protocols)

¿Ejecutar queries contra Splunk?
```

#### `/ir` — Respuesta a Incidentes

Activa el analista DFIR para respuesta a incidentes:

```
> /ir posible ransomware en workstation WS-0042
```

**Ejemplo:**

```
> /ir ransomware detectado en 10.0.3.42, usuario jsmith

ThreatSwarm → dfir: Incidente declarado.
─────────────────────────────────────────
IR-20260430-001 | Severidad: CRITICAL
Host: 10.0.3.42 (WS-0042) | Usuario: jsmith

Acciones inmediatas:
  1. Aislar host de la red (¿autorizado?)
  2. Capturar memoria: 
     python3 vol.py -f /tmp/memdump WS-0042.mem --profile Win10x64_19041 pslist
  3. Identificar proceso de ransomware
  4. Preservar artefactos para análisis

¿Aislar el host? (esto requiere autorización del cliente)
```

#### `/pwned` — Post-Explotación

Activa la fase post-explotación después de obtener acceso:

```
> /pwned shell en 10.0.1.50 como www-data
```

**Ejemplo:**

```
> /pwned acceso inicial obtenido via SQLi, shell como www-data en 10.0.1.50

ThreatSwarm → post-ex: Access confirmed.
──────────────────────────────────────────
Host: 10.0.1.50 | User: www-data | Via: SQLi → RCE

Objetivos post-explotación:
  1. Escalada de privilegios (Linux kernel 5.4 → CVE-2021-4034?)
  2. Enumeración de credenciales (LaZagne)
  3. Movimiento lateral (pivot a 10.0.0.0/24)
  4. Persistencia

Comandos sugeridos:
  # Enumeración local
  id && whoami && uname -a
  sudo -l
  
  # Escalada
  linpeas.sh
  python3 -c 'import pty; pty.spawn("/bin/bash")'

¿Continuar con enumeración de privilegios?
```

#### `/report` — Generación de Reportes

Activa el generador de reportes con las evidencias capturadas:

```
> /report ejecutivo para cliente-banco-central
```

**Ejemplo:**

```
> /report full engagement cliente-banco-central

ThreatSwarm → report-writer: Generando reporte completo.
────────────────────────────────────────────────────────
Engagement: cliente-banco-central
Fecha: 2026-04-30
Tipo: full (ejecutivo + técnico + remediación)

Hallazgos consolidados:
  CRITICAL: 2 | HIGH: 5 | MEDIUM: 8 | LOW: 3

Generando con:
  python3 core/scripts/report_generate.py generate \
    --type full \
    --evidence-dir ./evidence \
    --output ./reports \
    --format markdown

¿Proceder? (sí/cambiar formato a HTML/PDF)
```

### 4.2 Delegación a Agentes Especialistas

ThreatSwarm enruta automáticamente a los 32 agentes según el contexto de la conversación. También puedes invocar agentes explícitamente:

```
> [active-directory] Enumerar usuarios del dominio via LDAP
> [web-attacker] Probar IDOR en /api/orders/{id}
> [exploit] Buscar exploits para Apache 2.4.49 en ExploitDB
```

#### Agentes Ofensivos (21)

| Agente | Comando de invocación | Especialidad |
|--------|----------------------|-------------|
| **active-directory** | `[active-directory]` | BloodHound, Kerberoasting, DCSync, AD-CS ESC1-8, GPO |
| **api-attacker** | `[api-attacker]` | REST/GraphQL, IDOR, BOLA/BFLA, mass assignment |
| **c2-operator** | `[c2-operator]` | Sliver, Havoc, Cobalt Strike profiles, redirectors |
| **cloud-attacker** | `[cloud-attacker]` | AWS/Azure/GCP, Pacu, S3, IAM escalation |
| **cloud-postex** | `[cloud-postex]` | IAM persistence, cloud exfil, cross-account abuse |
| **container-attacker** | `[container-attacker]` | Docker escape, K8s RBAC, Trivy, pod privesc |
| **crypto-attacker** | `[crypto-attacker]` | TLS analysis, JWT confusion, padding oracle |
| **evasion** | `[evasion]` | AMSI bypass, process injection, LOLBins, obfuscation |
| **exploit** | `[exploit]` | Metasploit, RCE, SQLi, buffer overflows, exploit chains |
| **iot-attacker** | `[iot-attacker]` | Firmware, UART/JTAG, SCADA, MQTT, QEMU |
| **mobile-attacker** | `[mobile-attacker]` | Android/iOS, Frida, SSL pinning bypass, MobSF |
| **network-ops** | `[network-ops]` | ARP spoofing, SMB relay, VLAN hopping, LLMNR |
| **password-attacks** | `[password-attacks]` | Hashcat, credential stuffing, password spraying |
| **post-ex** | `[post-ex]` | Privesc, lateral movement, golden tickets, persistence |
| **red-infra** | `[red-infra]` | C2 deployment, redirector chains, phishing infra |
| **reverse-engineer** | `[reverse-engineer]` | Ghidra, dnSpy, shellcode, decompilation |
| **segmentation-tester** | `[segmentation-tester]` | Cross-segment access, firewall rules, VLAN |
| **social-engineer** | `[social-engineer]` | GoPhish, spear phishing, pretexting, vishing |
| **vuln-researcher** | `[vuln-researcher]` | CVE analysis, PoC development, patch diffing |
| **web-attacker** | `[web-attacker]` | SQLMap, XSS, SSRF, OWASP Top 10, Burp Suite |
| **wireless-attacker** | `[wireless-attacker]` | WPA/WPA3, PMKID, evil twin, BLE, Bluetooth |

#### Agentes Defensivos (7)

| Agente | Comando de invocación | Especialidad |
|--------|----------------------|-------------|
| **blue-team** | `[blue-team]` | Sigma rules, CIS hardening, SIEM, EDR |
| **compliance-scanner** | `[compliance-scanner]` | CIS, PCI-DSS, NIST CSF, SOC 2, Prowler |
| **dfir** | `[dfir]` | Volatility3, disk forensics, timeline analysis |
| **log-analyst** | `[log-analyst]` | Splunk, audit logs, anomaly detection |
| **malware-analyst** | `[malware-analyst]` | ELF/PE, YARA, sandbox, VirusTotal |
| **threat-hunter** | `[threat-hunter]` | Hypothesis-driven hunts, beacon detection |
| **vuln-management** | `[vuln-management]` | Nuclei, Nessus, CVSS, remediation tracking |

#### Agentes de Reconocimiento (2)

| Agente | Comando de invocación | Especialidad |
|--------|----------------------|-------------|
| **osint** | `[osint]` | SpiderFoot, DNS, subdomains, footprinting |
| **recon** | `[recon]` | Nmap, Subfinder, Amass, service enumeration |

#### Otros (2)

| Agente | Comando de invocación | Especialidad |
|--------|----------------------|-------------|
| **purple-team** | `[purple-team]` | MITRE ATT&CK mapping, detection gaps |
| **report-writer** | `[report-writer]` | Executive summaries, CVSS, remediation |

**Ejemplos de conversación por categoría:**

```
# Red
> [network-ops] Verifica si hay LLMNR poisoning en la red 10.0.0.0/24
> Responder activo, capturando hashes NTLMv2

# Web
> [web-attacker] Prueba SSRF en la funcionalidad de export PDF
> Payload: http://169.254.169.254/latest/meta-data/ (AWS metadata)

# AD
> [active-directory] AS-REP roasting contra usuarios con preauth disabled
> Comando: GetNPUsers.py domain.local/ -usersfile users.txt -format hashcat -outputfile hashes.asrep

# Cloud
> [cloud-attacker] Enumera buckets S3 públicos en la cuenta AWS
> Comando: aws s3 ls --no-sign-request --recursive s3://target-bucket/

# Mobile
> [mobile-attacker] Análisis estático del APK target_app.apk con MobSF
> URL: http://localhost:8000/api/v1/upload (MobSF API)
```

### 4.3 Gestión de Scope

El archivo `scope.txt` en la raíz del proyecto define los targets autorizados. **Todos los agentes verifican scope antes de ejecutar cualquier comando de red.**

#### Formato de scope.txt

```
# ThreatSwarm Scope — Engagement: cliente-banco-central
# Formato: una entrada por línea, comentarios con #

# Redes (CIDR)
10.0.0.0/24
192.168.100.0/24

# Hosts individuales
10.0.1.100
192.168.100.10

# Dominios
*.banco-central.com
dc01.banco.local
app.banco.local
```

**Entradas soportadas:**

| Tipo | Ejemplo | Descripción |
|------|---------|-------------|
| CIDR | `10.0.0.0/24` | Rango de red |
| IP individual | `192.168.1.100` | Host único |
| Dominio | `app.target.com` | Dominio específico |
| Wildcard | `*.target.com` | Todos los subdominios |

#### Validación automática

```bash
# Validar scope.txt (busca solapamientos, formatos inválidos, subnets grandes)
python3 core/scripts/scope_validate.py --scope-file scope.txt

# Con umbral personalizado de warning (>2048 hosts)
python3 core/scripts/scope_validate.py --scope-file scope.txt --host-warning 2048

# Salida esperada (sin errores):
# ✅ scope.txt: 5 entries validated
#    Networks: 2 | Hosts: 1 | Domains: 2
#    Total hosts in scope: 512
```

**Salida con errores:**

```
❌ scope.txt: 2 issues found
   Line 3: Invalid domain format "not_a_domain"
   Line 5: 10.0.0.0/8 contains 16,777,216 hosts (warning threshold: 1024)
```

#### MCP server scope_check

El MCP server `scope-mcp` expone herramientas de validación accesibles desde OpenCode:

- `scope_check` — Valida si un target está en scope
- `scope_list` — Lista todas las entradas de scope
- `scope_add` — Agrega un target a scope.txt

> **Importante:** OpenCode no tiene sistema de hooks (a diferencia de Claude Code). La verificación de scope se debe realizar manualmente cada vez. El `instructions.md` incluye una instrucción explícita para que el agente verifique scope antes de cada comando de red.

### 4.4 Captura de Evidencia

Todas las evidencias se almacenan bajo `evidence/` con una estructura estandarizada:

```
evidence/
└── 20260430/                          # Fecha del engagement (YYYYMMDD)
    ├── 10.0.1.100/                    # Target
    │   ├── findings.md                # Hallazgos documentados
    │   ├── screenshots/               # Capturas de pantalla
    │   ├── pcap/                      # Capturas de red
    │   ├── output/                    # Salida de herramientas
    │   └── exploits/                  # Código de exploit/PoC
    ├── app.banco.local/
    │   ├── findings.md
    │   ├── screenshots/
    │   ├── output/
    │   │   ├── nmap_scan.txt
    │   │   ├── nuclei_results.txt
    │   │   └── sqlmap_output.txt
    │   └── web/
    │       ├── whatweb.txt
    │       └── nikto_scan.txt
    └── dc01.banco.local/
        ├── findings.md
        └── output/
            ├── bloodhound_analysis.json
            └── kerberoast_hashes.txt
```

#### Formato de findings.md

Cada hallazgo se documenta en formato estructurado:

```markdown
## [CRITICAL] SQL Injection en /api/v1/users

- **Severity:** CRITICAL
- **CVSS Score:** 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- **CWE:** CWE-89
- **Target:** app.banco.local:8080
- **Endpoint:** GET /api/v1/users?id=[INJECT]

### Descripción
El parámetro `id` en el endpoint /api/v1/users es vulnerable a
SQL injection sin autenticación. El WAF (ModSecurity) fue evadido
con tamper scripts space2comment y between.

### Prueba de concepto
```bash
sqlmap -u "http://app.banco.local:8080/api/v1/users?id=1" \
  --batch --risk=2 --level=3 \
  --tamper=space2comment,between \
  --dbs
```

### Impacto
Un atacante puede:
- Exfiltrar la base de datos completa (PII de clientes)
- Modificar registros (inyección UPDATE)
- Potencial acceso al sistema operativo (xp_cmdshell en MSSQL)

### Evidencia
- Salida SQLMap: `output/sqlmap_output.txt`
- Screenshot: `screenshots/sqli_proof.png`

### Remediación
1. Implementar consultas parametrizadas (prepared statements)
2. Aplicar input validation en el parámetro `id`
3. Configurar WAF con reglas específicas para SQLi
4. Restringir permisos del usuario de base de datos (principio de mínimo privilegio)

### Referencias
- CVE-2024-XXXX (pendiente asignación)
- OWASP: https://owasp.org/www-community/attacks/SQL_Injection
- ATT&CK: T1190 (Exploit Public-Facing Application)
```

#### MCP server evidence-mcp

Herramientas disponibles:

| Herramienta | Descripción |
|-------------|-------------|
| `evidence_capture_screenshot` | Captura screenshot de un target (via import) |
| `evidence_verify` | Verifica integridad de cadena de custodia |
| `evidence_list` | Lista todos los archivos de evidencia con metadata |
| `evidence_export` | Empaqueta evidencia en archivo (zip/tar) |

### 4.5 Generación de Reportes

#### CLI: report_generate.py

```bash
# Generar reporte ejecutivo (markdown)
python3 core/scripts/report_generate.py generate \
  --type executive \
  --evidence-dir ./evidence \
  --output ./reports

# Generar reporte técnico (HTML)
python3 core/scripts/report_generate.py generate \
  --type technical \
  --evidence-dir ./evidence \
  --output ./reports \
  --format html

# Generar reporte completo (PDF)
python3 core/scripts/report_generate.py generate \
  --type full \
  --evidence-dir ./evidence \
  --output ./reports \
  --format pdf
```

**Tipos de reporte:**

| Tipo | Descripción | Público |
|------|-------------|---------|
| `executive` | Resumen de alto nivel, postura de riesgo, métricas clave | C-Suite, Management |
| `technical` | Hallazgos detallados con CVSS, pasos a reproducir, remediación | Equipo técnico |
| `full` | Reporte completo combinando ejecutivo + técnico + remediación | Cliente final |

**Formatos de salida:**

| Formato | Flag | Requisitos |
|---------|------|------------|
| Markdown | `--format markdown` (default) | Ninguno |
| HTML | `--format html` | Ninguno |
| PDF | `--format pdf` | wkhtmltopdf o similar |

#### Templates disponibles

Los templates se encuentran en `core/templates/`:

| Archivo | Propósito |
|---------|-----------|
| `executive_summary.md` | Template para resumen ejecutivo |
| `technical_finding.md` | Template para hallazgo técnico individual |
| `remediation_roadmap.md` | Template para plan de remediación |
| `client/` | Template completo para entrega a cliente |

#### MCP server report-mcp

Herramientas disponibles:

| Herramienta | Descripción |
|-------------|-------------|
| `report_generate` | Genera un reporte desde el directorio de evidencia |
| `report_template_list` | Lista los templates de reporte disponibles |

**Uso dentro de OpenCode:**

```
> Genera reporte ejecutivo del engagement actual
> (OpenCode usa report-mcp para leer evidencia y generar el reporte)
```

### 4.6 Flujo de Trabajo Completo

Ejemplo paso a paso de un engagement real de pentesting web:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENGAGEMENT COMPLETE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ① /engage            ② Reconocimiento     ③ Ataque            │
│  ┌──────────┐         ┌──────────────┐     ┌──────────────┐    │
│  │ scope.txt│ ──────► │ nmap -sS -T4 │ ──► │ SQLi / XSS  │    │
│  │ evidencia│         │ subfinder    │     │ SSRF / LFI  │    │
│  │ vars env │         │ httpx        │     │ IDOR / Auth │    │
│  └──────────┘         │ nuclei       │     └──────┬───────┘    │
│                       └──────────────┘            │            │
│                                                   ▼            │
│  ⑥ Reporte          ⑤ Post-Ex           ④ Explotación         │
│  ┌──────────┐       ┌──────────────┐    ┌──────────────┐     │
│  │ ejecutivo│ ◄──── │ privesc      │ ◄── │ Metasploit  │     │
│  │ técnico  │       │ lateral move │    │ manual PoC  │     │
│  │ remediación│     │ persistence  │    │ SQLMap      │     │
│  └──────────┘       └──────────────┘    └──────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Paso 1: Preparación del Engagement

```bash
# Editar scope.txt con los targets autorizados
cat > scope.txt << 'EOF'
# Engagement: cliente-banco-central
# Fecha: 2026-04-30
10.0.0.0/24
192.168.100.0/24
*.banco-central.com
dc01.banco.local
app.banco.local
EOF

# Validar scope
python3 core/scripts/scope_validate.py --scope-file scope.txt
```

#### Paso 2: Iniciar Engagement en OpenCode

```bash
opencode
```

```
> /engage cliente-banco-central

ThreatSwarm: Engagement iniciado para cliente-banco-central
  Scope: 7 targets verificados
  Evidencia: evidence/20260430/
  LHOST=10.10.14.1, LPORT=4444

  Iniciando fase de reconocimiento...
```

#### Paso 3: Reconocimiento

```
> [recon] Escanea todos los targets en scope con nmap SYN

ThreatSwarm → recon: Ejecutando escaneo de descubrimiento.

# Discovery scan rápido
nmap -sS -T4 --open -oN evidence/20260430/discovery.nmap 10.0.0.0/24

# Resultados esperados:
# 10.0.0.1: 53/tcp (DNS), 88/tcp (Kerberos)
# 10.0.0.10: 80/tcp, 443/tcp (web server)
# 10.0.0.100: 445/tcp (SMB), 3389/tcp (RDP)
```

#### Paso 4: Ataque

```
> [web-attacker] Enfócate en app.banco.local:443, prueba OWASP Top 10

ThreatSwarm → web-attacker: Iniciando assessment web.

# Fingerprinting
whatweb -a 3 https://app.banco.local

# Directory enumeration
feroxbuster -u https://app.banco.local \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt

# Nuclei template scan
nuclei -u https://app.banco.local \
  -t /usr/share/nuclei/templates/http/vulnerabilities/ \
  -o evidence/20260430/app.banco.local/output/nuclei.txt

# Hallazgo: SQL Injection en /api/v1/users?id=
```

#### Paso 5: Explotación

```
> [exploit] Explota la SQLi en /api/v1/users

ThreatSwarm → exploit: Preparando explotación.

sqlmap -u "https://app.banco.local/api/v1/users?id=1" \
  --batch --risk=2 --level=3 \
  --tamper=space2comment,between \
  --dbs --dump-all

# Resultado: Base de datos exfiltrada, 3 tablas sensibles
# Evidencia guardada en: evidence/20260430/app.banco.local/output/
```

#### Paso 6: Post-Explotación

```
> [post-ex] Obtuvimos RCE en el servidor web, usuario www-data

ThreatSwarm → post-ex: Iniciando post-explotación.

# Escalada de privilegios
linpeas.sh

# Harvesting de credenciales (solo hashes)
hashes=$(cat /etc/shadow | cut -d: -f1-2)
echo "$hashes" > evidence/20260430/app.banco.local/creds/hashes.txt

# Movimiento lateral
# Target: 10.0.0.100 (DC01)
netexec smb 10.0.0.100 -u jsmith -p '[HASH]' --shares
```

#### Paso 7: Reporte

```
> /report full

ThreatSwarm → report-writer: Generando reporte completo.

python3 core/scripts/report_generate.py generate \
  --type full \
  --evidence-dir ./evidence \
  --output ./reports \
  --format markdown

# Reporte generado: reports/20260430_cliente-banco-central_full.md
```

---

## 5. Casos de Uso

### 5.1 Pentesting Web — OWASP Top 10

**Escenario:** Auditoría de seguridad de aplicación web bancaria contra OWASP Top 10.

```
> /engage banco-web scope: app.banco.local:443, api.banco.local:8443
> [recon] Descubre tecnologías, directorios, endpoints
> [web-attacker] Testea OWASP Top 10 completo:
>   - A01 Broken Access Control → IDOR en /api/orders/{id}
>   - A02 Cryptographic Failures → TLS 1.1 en endpoints internos
>   - A03 Injection → SQLi en /api/users?id=
>   - A04 Insecure Design → Bypass de MFA vía parameter tampering
>   - A05 Security Misconfiguration → Headers de seguridad faltantes
>   - A06 Vulnerable Components → Apache Struts 2.5.26 (CVE-2018-11776)
>   - A07 Auth Failures → Credential stuffing exitoso (sin rate limiting)
>   - A08 Software Integrity → CORS misconfigured: * en producción
>   - A09 Logging Failures → Errores SQL expuestos en HTTP 500
>   - A10 SSRF → /api/proxy?url=http://169.254.169.254 (metadata)
> /report full
```

### 5.2 Active Directory — Red Team

**Escenario:** Assessment de entorno Active Directory con objetivo de Domain Admin.

```
> /engage ad-redteam scope: 10.0.0.0/24, dc01.corp.local
> [recon] Descubrimiento de red con nmap, NetExec, LDAP enumeration
> [active-directory] BloodHound collection + análisis de paths
> [active-directory] Kerberoasting contra cuentas de servicio
> [password-attacks] Crackeo de hashes Kerberoast con hashcat
> [active-directory] DCSync para dump de NTDS.dit (Domain Admin obtenido)
> [post-ex] Golden Ticket creation + persistencia
> /report technical
```

**Comandos clave:**

```bash
# BloodHound data collection
bloodhound-python -d corp.local -u jsmith -p 'Password1' -ns 10.0.0.1 -c All

# Kerberoasting
impacket-GetUserSPNs corp.local/jsmith:'Password1' -request -outputfile hashes.asrep

# Hash cracking
hashcat -m 13100 hashes.asrep /usr/share/seclists/Passwords/rockyou.txt

# DCSync (post Domain Admin)
impacket-secretsdump corp.local/administrator@10.0.0.1 -just-dc-ntlm
```

### 5.3 Infraestructura Cloud (AWS)

**Escenario:** Assessment de seguridad de infraestructura AWS con focus en IAM y S3.

```
> /engage aws-assessment scope: cuenta AWS 123456789012
> [cloud-attacker] Enumeración con Pacu
> [cloud-attacker] Auditoría de buckets S3 (públicos, permisos excesivos)
> [cloud-attacker] Escalada de privilegios IAM
> [cloud-attacker] Lambda backdoor injection
> [cloud-postex] Persistence via IAM user creation
> /report full
```

**Comandos clave:**

```bash
# Pacu —框架 automatizado de AWS pentesting
pacu --exec recon_enum --region us-east-1

# S3 bucket audit
aws s3 ls --no-sign-request
aws s3api get-bucket-policy --bucket target-bucket

# IAM enumeration
aws iam list-users
aws iam list-attached-user-policies --user-name target-user
aws sts get-caller-identity
```

### 5.4 Respuesta a Incidentes

**Escenario:** Detección de actividad de ransomware en workstation corporativa.

```
> /ir ransomware en WS-0042 (10.0.3.42), usuario jsmith
> [dfir] Captura de memoria con Volatility3
> [dfir] Timeline analysis con Timesketch
> [malware-analyst] Análisis del binario ransomware
> [log-analyst] Correlación de logs (Splunk + Windows Event Logs)
> [threat-hunter] Búsqueda de IOC en otros hosts
> /report executive
```

**Comandos clave:**

```bash
# Memory capture
vol.py -f /tmp/memdump WS-0042.mem --profile Win10x64_19041 pslist
vol.py -f /tmp/memdump WS-0042.mem --profile Win10x64_19041 netscan
vol.py -f /tmp/memdump WS-0042.mem --profile Win10x64_19041 malware

# YARA scan
yara -r /rules/malware.yar /evidence/20260430/WS-0042/

# IOC extraction
grep -r "suspicious_domain\|malicious_ip" /evidence/20260430/WS-0042/
```

### 5.5 Wireless Assessment

**Escenario:** Testing de seguridad de red WiFi corporativa WPA3 Enterprise.

```
> /engage wifi-assessment scope: sede_principal, ssid:CORP-WPA3
> [wireless-attacker] Captura de handshakes
> [wireless-attacker] PMKID attack testing
> [wireless-attacker] Evil twin detection + testing
> [network-ops] Segmentación de red wireless vs wired
> /report technical
```

**Comandos clave:**

```bash
# Monitor mode
airmon-ng start wlan0

# Handshake capture
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# PMKID attack
hcxdumptool -i wlan0mon --enable_status=1 -o pmkid_capture.pcapng

# Hash conversion
hcxpcapngtool -o hashes.hc22000 pmkid_capture.pcapng

# Cracking
hashcat -m 22000 hashes.hc22000 /usr/share/seclists/Passwords/rockyou.txt
```

### 5.6 Mobile Application Testing

**Escenario:** Revisión de seguridad de aplicación Android APK.

```
> /engage mobile-app scope: target_app.apk
> [mobile-attacker] Análisis estático con MobSF + jadx
> [mobile-attacker] Bypass de SSL pinning con Frida
> [mobile-attacker] Análisis de tráfico con mitmproxy
> [api-attacker] Testing de APIs consumidas por la app
> /report full
```

**Comandos clave:**

```bash
# MobSF automated scan (API)
curl -F "file=@target_app.apk" http://localhost:8000/api/v1/upload

# APK decompilation
jadx -d jadx_output target_app.apk

# Frida instrumentation
frida -U -f com.target.app -l ssl_pinning_bypass.js

# APKtool for manifest analysis
apktool d target_app.apk -o apktool_output
```

### 5.7 Compliance Scanning

**Escenario:** Auditoría de compliance CIS Benchmark + PCI-DSS gap analysis.

```
> /engage compliance-audit scope: infra-production
> [compliance-scanner] CIS Benchmarks con Prowler (AWS) + ScoutSuite
> [compliance-scanner] PCI-DSS gap analysis
> [vuln-management] Vulnerability scanning con Nessus/Nuclei
> [blue-team] Verificación de controles compensatorios
> /report compliance
```

**Comandos clave:**

```bash
# AWS CIS Benchmark
prowler aws -M text -o prowler_output/

# ScoutSuite multi-cloud scan
scoutsuite aws --report-dir scoutsuite_output/

# Nuclei compliance templates
nuclei -t /usr/share/nuclei/templates/compliance/ -l targets.txt

# Nmap compliance scripts
nmap --script vuln,ssl-ccs-injection,ssl-heartbleed -oA compliance_scan 10.0.0.0/24
```

### 5.8 Integración con n8n

ThreatSwarm incluye templates de workflow para n8n en `integrations/n8n/`:

| Workflow | Trigger | Acción |
|----------|---------|--------|
| `engagement-start.json` | Manual | Inicializa scope, crea estructura de proyecto |
| `finding-sync.json` | Webhook | Sincroniza hallazgos con trackers externos |
| `report-notification.json` | Schedule | Alerta cuando reportes necesitan revisión |

**Ejemplo: Automatización de ingesta de hallazgos:**

```json
// Workflow n8n: finding-sync.json
// 1. Recibe webhook POST con nuevo hallazgo (JSON)
// 2. Valida formato contra schema de ThreatSwarm
// 3. Agrega a findings.json en evidence/ 
// 4. Si severidad CRITICAL/HIGH → envía notificación por Telegram
// 5. Actualiza dashboard de métricas del engagement
```

**Integración con OpenCode (non-interactive):**

```bash
# Desde n8n HTTP Request node
opencode -p "Nuevo hallazgo CRITICAL recibido: SQLi en /api/users. Actualiza findings.md y evalúa impacto."

# Programar generación de reportes (cron)
0 18 * * 5 cd /path/to/ThreatSwarm && python3 core/scripts/report_generate.py generate --type executive --evidence-dir ./evidence --output ./reports
```

---

## 6. Referencia Rápida

### 6.1 Comandos Slash

| Comando | Fase | Descripción |
|---------|------|-------------|
| `/engage` | Setup | Inicia engagement, verifica scope, crea estructura |
| `/attack` | Attack | Ejecuta vector de ataque según contexto |
| `/hunt` | Defense | Threat hunting con hipótesis |
| `/ir` | Defense | Respuesta a incidentes |
| `/pwned` | Post-Ex | Post-explotación (privesc, lateral, persistence) |
| `/report` | Report | Generación de reportes (exec/tech/full) |

### 6.2 Agentes por Categoría

**Red y Infraestructura:**
- `[network-ops]` — ARP, MITM, SMB relay, VLAN
- `[segmentation-tester]` — Cross-segment, firewall rules
- `[red-infra]` — C2 infraestructura, redirectors

**Web y APIs:**
- `[web-attacker]` — OWASP Top 10, SQLMap, Burp Suite
- `[api-attacker]` — REST, GraphQL, IDOR, BOLA

**Active Directory:**
- `[active-directory]` — BloodHound, Kerberoasting, DCSync
- `[password-attacks]` — Hashcat, spraying, relay

**Explotación y Post-Ex:**
- `[exploit]` — Metasploit, RCE, buffer overflows
- `[post-ex]` — Privesc, lateral, persistence
- `[evasion]` — AMSI, process injection, LOLBins

**Cloud y Contenedores:**
- `[cloud-attacker]` — AWS, Azure, GCP, Pacu
- `[cloud-postex]` — Cloud persistence, exfil
- `[container-attacker]` — Docker escape, K8s RBAC

**Análisis y Reversing:**
- `[reverse-engineer]` — Ghidra, dnSpy, shellcode
- `[malware-analyst]` — ELF/PE, YARA, sandbox
- `[crypto-attacker]` — TLS, JWT, padding oracle

**Mobile, IoT, Wireless:**
- `[mobile-attacker]` — Android/iOS, Frida, MobSF
- `[iot-attacker]` — Firmware, UART, SCADA, MQTT
- `[wireless-attacker]` — WPA/WPA3, PMKID, evil twin

**Reconocimiento:**
- `[recon]` — Nmap, Subfinder, Amass
- `[osint]` — SpiderFoot, DNS, footprinting

**Defensa y Compliance:**
- `[blue-team]` — Sigma, CIS, SIEM, EDR
- `[purple-team]` — ATT&CK mapping, detection gaps
- `[threat-hunter]` — Hunts, beacon detection
- `[dfir]` — Volatility3, disk forensics
- `[log-analyst]` — Splunk, audit logs
- `[vuln-management]` — Nuclei, Nessus, CVSS
- `[compliance-scanner]` — CIS, PCI-DSS, NIST

**Social Engineering y C2:**
- `[social-engineer]` — GoPhish, phishing, vishing
- `[c2-operator]` — Sliver, Havoc, Cobalt Strike

**Vulnerability Research:**
- `[vuln-researcher]` — CVE, PoC, patch diffing

**Reportes:**
- `[report-writer]` — Executive, technical, CVSS, remediation

### 6.3 Herramientas CLI del Framework

```bash
# Build system
python3 scripts/build.py --all              # Generar todos los adaptadores
python3 scripts/build.py --adapter opencode  # Solo adaptador OpenCode
python3 scripts/build.py --list             # Listar adaptadores disponibles

# Smoke test
bash scripts/smoke_test.sh                  # Verificación completa del repositorio

# Scope validation
python3 core/scripts/scope_validate.py --scope-file scope.txt

# Report generation
python3 core/scripts/report_generate.py generate \
  --type {executive,technical,full} \
  --evidence-dir ./evidence \
  --output ./reports \
  --format {markdown,html,pdf}

# Setup script (OpenCode)
bash adapters/opencode/setup.sh
```

### 6.4 MCP Server Tools

#### scope-mcp

| Herramienta | Parámetros | Descripción |
|-------------|-----------|-------------|
| `scope_check` | `target` (string) | Valida si un target está en scope |
| `scope_list` | — | Lista todas las entradas de scope |
| `scope_add` | `target` (string) | Agrega un target a scope.txt |

#### evidence-mcp

| Herramienta | Parámetros | Descripción |
|-------------|-----------|-------------|
| `evidence_capture_screenshot` | `target`, `path` | Captura screenshot de un target |
| `evidence_verify` | `path` | Verifica integridad SHA256 de evidencia |
| `evidence_list` | `directory` | Lista archivos de evidencia con metadata |
| `evidence_export` | `directory`, `format` | Empaqueta evidencia (zip/tar) |

#### report-mcp

| Herramienta | Parámetros | Descripción |
|-------------|-----------|-------------|
| `report_generate` | `type`, `evidence_dir`, `output_dir`, `format` | Genera reporte desde evidencia |
| `report_template_list` | — | Lista templates disponibles |

---

## 7. Solución de Problemas

### MCP servers no responden

**Síntoma:** OpenCode muestra error de conexión a MCP server.

**Diagnóstico:**

```bash
# Verificar que los servidores compilan
python3 -c "import py_compile; py_compile.compile('integrations/mcp/scope-mcp/server.py', doraise=True)"
python3 -c "import py_compile; py_compile.compile('integrations/mcp/evidence-mcp/server.py', doraise=True)"
python3 -c "import py_compile; py_compile.compile('integrations/mcp/report-mcp/server.py', doraise=True)"

# Verificar que python3 está en PATH
which python3
# Debe retornar: /usr/bin/python3 o similar

# Probar comunicación directa
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"scope_list","arguments":{}}}' \
  | python3 integrations/mcp/scope-mcp/server.py 2>/dev/null
```

**Solución:** Si `python3` no está en PATH o es una versión incompatible, editar `.opencode.json` para usar la ruta completa:

```json
{
  "mcpServers": {
    "threatswarm-scope": {
      "type": "stdio",
      "command": "/usr/bin/python3",
      "args": ["integrations/mcp/scope-mcp/server.py"],
      "env": []
    }
  }
}
```

### Scope check falla

**Síntoma:** El agente reporta targets fuera de scope que deberían estar incluidos.

**Diagnóstico:**

```bash
# Verificar contenido de scope.txt
cat scope.txt

# Verificar que no haya espacios en blanco o caracteres extraños
cat -A scope.txt | head -20

# Ejecutar validación
python3 core/scripts/scope_validate.py --scope-file scope.txt
```

**Problemas comunes:**
- Espacios después de CIDR/domain: `10.0.0.0/24 ` (quitar espacio final)
- Caracteres de Windows: `10.0.0.0/24\r` (convertir con `dos2unix scope.txt`)
- Formato de wildcard incorrecto: `banco-local.*` (debe ser `*.banco-local`)

### Report generation errors

**Síntoma:** Error al generar reporte, hallazgos faltantes.

**Diagnóstico:**

```bash
# Verificar estructura de evidencia
find evidence/ -type f | head -20

# Verificar que findings.md o findings.json existe
ls evidence/*/findings.md 2>/dev/null
ls evidence/*/*/findings.json 2>/dev/null

# Formato correcto de findings.json
cat evidence/20260430/target/findings.json | python3 -m json.tool
```

**Formato correcto de findings.json:**

```json
{
  "findings": [
    {
      "title": "SQL Injection en /api/users",
      "severity": "CRITICAL",
      "cvss": "9.8",
      "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "description": "El parámetro id es vulnerable a SQL injection",
      "target": "app.target.local:8080",
      "remediation": "Implementar prepared statements"
    }
  ]
}
```

### Model API errors

**Síntoma:** OpenCode muestra error de autenticación o rate limit.

**Diagnóstico:**

```bash
# Verificar API keys están configuradas
echo $ANTHROPIC_API_KEY  # Debe mostrar sk-ant-...
echo $OPENAI_API_KEY     # Debe mostrar sk-...

# Probar conexión (ejemplo con Anthropic)
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

**Solución:**
- Verificar que la API key sea válida (no expirada)
- Revisar límite de créditos en el dashboard del proveedor
- Si hay rate limiting, esperar o usar un modelo diferente

### OpenCode no carga instructions.md

**Síntoma:** OpenCode no reconoce los comandos de ThreatSwarm.

**Diagnóstico:**

```bash
# Verificar que instructions.md existe en la raíz
ls -la instructions.md

# Verificar contenido (debe comenzar con # ThreatSwarm)
head -5 instructions.md

# Verificar que .opencode.json referencia el archivo
cat .opencode.json | grep -i instruction
```

**Solución:** Copiar el archivo desde el adaptador:

```bash
cp adapters/opencode/instructions.md ./
```

### Herramientas de pentesting no encontradas

**Síntoma:** El agente sugiere comandos pero las herramientas no están instaladas.

**Solución:** Instalar las herramientas necesarias. Ejemplos para Kali Linux:

```bash
# Herramientas base
sudo apt update && sudo apt install -y nmap sqlmap nikto whatweb

# Enumeración
sudo apt install -y subfinder amass httpx feroxbuster nuclei

# Active Directory
sudo apt install -y impacket-scripts bloodhound-python netexec responder

# Post-explotación
sudo apt install -y hashcat hydra

# Mobile
pip3 install frida-tools objection
```

---

## 8. Changelog y Versión

### v2.0 — Funcionalidades principales

- **32 agentes especializados** (21 ofensivos, 7 defensivos, 2 recon, 1 colaborativo, 1 reportes)
- **4 adaptadores de plataforma:** Claude Code, GitHub Copilot, OpenCode, OpenClaw
- **Sistema de build** para generar adaptadores desde `core/agents/`
- **3 MCP servers:** scope-mcp, evidence-mcp, report-mcp
- **Pipeline de reportes** con 4 templates (executive, technical, remediation, client)
- **Sistema de evidencia** con estructura estandarizada y cadena de custodia
- **Integración con n8n** para automatización de workflows
- **OpenProject sync** para gestión de proyectos
- **Cybersecurity Skills plugin** con 80+ skills especializadas
- **Agente registry** con metadata, triggers y recomendaciones de modelo
- **Zero Docker** — corre con Python stdlib + herramientas CLI

### Migración desde v1.0

Si vienes de la versión original (mukul975/ThreatSwarm):

```bash
# 1. Renombrar o respaldar el proyecto original
mv ThreatSwarm ThreatSwarm-v1.bak

# 2. Clonar v2.0
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm

# 3. Migrar scope.txt
cp ../ThreatSwarm-v1.bak/scope.txt ./

# 4. Migrar evidencia existente (si aplica)
cp -r ../ThreatSwarm-v1.bak/evidence/* ./evidence/

# 5. Generar adaptadores
python3 scripts/build.py --all

# 6. Verificar
bash scripts/smoke_test.sh
```

**Cambios notables desde v1.0:**

| Aspecto | v1.0 | v2.0 |
|---------|------|------|
| Plataformas | Claude Code únicamente | 4 plataformas |
| Agentes | 27 | 32 (5 nuevos) |
| Reportes | Manual | Pipeline automatizado |
| Evidencia | Manual | Estructurada con MCP |
| Scope | Manual | MCP server + validación automática |
| Build | Manual | `build.py --all` |
| Skills | N/A | 80+ cybersecurity skills |

---

*ThreatSwarm v2.0 — Documentación generada para OpenCode*
*Última actualización: 2026-04-30*
