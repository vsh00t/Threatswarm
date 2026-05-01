# Prompt de Revisión — Material del Curso

**Curso:** Taller: Uso de Agentes de IA para Pentest Autónomo
**Instructor:** Jorge Moya — Ironcybersec
**Documentos:** SLIDES.md, WORKBOOK.md, CHEATSHEET.md
**Ubicación:** `docs/course/` en el repositorio ThreatSwarm

---

## Instrucciones para el Revisor

Eres un editor técnico especializado en ciberseguridad ofensiva e inteligencia artificial aplicada. Tu misión es revisar el material completo de este taller (8 horas, nivel profesional, 4 asistentes con experiencia en seguridad) y garantizar que cumple los más altos estándares de rigor técnico, precisión factual y calidad pedagógica.

### Stack tecnológico del curso

Los documentos deben reflejar este stack **en este orden de prioridad**:

1. **VS Code + GitHub Copilot** (plataforma principal de orquestación)
   - Copilot en VS Code soporta MCP servers de forma nativa
   - Se usa para demos de pentest web, mobile y engagement completo
   - Terminal integrada en VS Code para ejecución de comandos

2. **OpenCode + Z.AI** (terminal-based, alternativa)
   - OpenCode (migrado a charmbracelet/crush) como agente en terminal
   - Z.AI como proveedor LLM
   - Soporta MCP servers via .opencode.json
   - Ideal para labs y tareas desde terminal

3. **Claude / Anthropic** (terciario, uso limitado)
   - Disponible pero con rate limits restrictivos
   - Se usa para tareas de razonamiento complejo cuando Copilot/Z.AI no alcanzan
   - NO es la plataforma principal — corregir cualquier referencia que lo sugiera

### Criterios de Revisión

#### 1. Rigor Técnico (CRÍTICO)

Para CADA herramienta, técnica o afirmación técnica, verifica:

- [ ] **Versiones correctas**: Nmap, Burp Suite, Frida, OpenCode, VS Code Copilot — ¿las versiones mencionadas son las actuales (abril 2026)?
- [ ] **Comandos exactos**: ¿Cada comando de terminal es syntácticamente correcto? ¿Los flags existen en las versiones actuales? Ejecuta mentalmente cada comando.
- [ ] **CVEX/Referencias**: ¿Los CVEs mencionados existen y corresponden a lo descrito? ¿Los repos de GitHub son correctos y están activos?
- [ ] **Arquitectura MCP**: ¿La descripción de JSON-RPC 2.0, stdio transport, tools/resources/prompts es técnicamente precisa según la spec de Anthropic?
- [ ] **Burp Suite MCP Server**: ¿La descripción de la extensión de PortSwigger (BApp Store, Feb 2026) es precisa? ¿Las tools que expone son correctas?
- [ ] **Frida MCP servers**: ¿kahlo-mcp (FuzzySecurity) y frida-c2-mcp (s4dp4nd4) existen como se describen? ¿Las capacidades mencionadas son correctas?
- [ ] **pentest-ai-agents (0xSteph)**: ¿Son 28 subagentes? ¿Es compatible con OpenCode? ¿El MCP server compañero tiene 150+ tools?
- [ ] **ThreatSwarm v2.0**: ¿Son 32 agentes? ¿Los categorizados están correctos? ¿El adapter de GitHub Copilot existe y funciona?
- [ ] **Modelos LLM**: ¿Z.AI es un proveedor válido para OpenCode? ¿La config en .opencode.json es correcta?

#### 2. Precisión Factual

- [ ] ¿Cada fecha, nombre, y evento mencionado es real y verificable?
- [ ] ¿Las estadísticas (si hay) tienen fuente?
- [ ] ¿Las citas o referencias a blogs/posts son atribuidas correctamente?
- [ ] ¿No hay afirmaciones exageradas ni marketing disfrazado de hecho?
- [ ] ¿Mythos por Anthropic fue bloqueado por la Casa Blanca? Verificar.
- [ ] ¿oh-my-opencode tuvo prompt injection detectado por Cisco CX? Verificar.
- [ ] ¿Claude Code RCE (novee.security) es real? Verificar.

#### 3. Consistencia Interna

- [ ] ¿El stack tecnológico es consistente en los 3 documentos? (VS Code Copilot → OpenCode+Z.AI → Claude limitado)
- [ ] ¿No hay contradicciones entre SLIDES, WORKBOOK y CHEATSHEET?
- [ ] ¿Los comandos en el CHEATSHEET coinciden con los del WORKBOOK?
- [ ] ¿Los labs del WORKBOOK usan las mismas herramientas que las slides describen?
- [ ] ¿El número de agentes (32), categorías, y nombres son idénticos en los 3 documentos?

#### 4. Calidad Pedagógica

- [ ] ¿La progresión de dificultad en los labs es lógica? (Lab 1 fácil → Lab 4 avanzado)
- [ ] ¿Un profesional de seguridad con 3+ años puede seguir el material sin contexto adicional?
- [ ] ¿Los ejercicios son realizables en 8 horas con 4 asistentes?
- [ ] ¿Las soluciones de los labs son completas y correctas?
- [ ] ¿Hay suficiente contexto teórico para entender el "por qué" antes de cada demo?
- [ ] ¿El CHEATSHEET es usable como referencia rápida durante el taller?

#### 5. Formato y Presentación

- [ ] ¿Los diagramas ASCII son legibles y correctos?
- [ ] ¿El markdown está bien formateado sin errores de sintaxis?
- [ ] ¿Las tablas están alineadas correctamente?
- [ ] ¿Los bloques de código tienen el lenguaje correcto especificado?
- [ ] ¿No hay secciones vacías o placeholders sin completar (ej: "[INSERTAR FECHA]")?

#### 6. Seguridad del Contenido

- [ ] ¿El material NO contiene credenciales, API keys, ni información sensible real?
- [ ] ¿El contenido es adecuado para un taller autorizado de pentesting?
- [ ] ¿Se mencionan las restricciones legales y éticas necesarias?
- [ ] ¿El scope enforcement está presentado como obligatorio, no opcional?

### Formato de Output

Para cada documento, genera:

```
## [NOMBRE DEL DOCUMENTO]

### Errores Críticos (deben corregirse)
- Línea X: [descripción del error] → [corrección sugerida]

### Advertencias (recomendado corregir)
- Línea X: [descripción] → [sugerencia]

### Mejoras Sugeridas
- [descripción de la mejora]

### Aprobación
- [ ] Apto para entrega profesional
- [ ] Requiere revisiones menores
- [ ] Requiere revisiones mayores
```

### Nota Final

Este material se usará comercialmente. La calidad debe ser impecable. Si algo no estás seguro de que sea correcto, márcalo explícitamente. Es preferible marcar una duda que dejar pasar un error factual que el instructor no pueda defender ante profesionales de la industria.

---

*Generado por Baphomet — Ironcybersec*
