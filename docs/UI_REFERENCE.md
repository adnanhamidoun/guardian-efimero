# Guardian Efímero - Interfaz Streamlit

## Estructura Visual

```
┌─ Guardian Efímero [Web App - Streamlit] ─────────────────────────────────────────┐
│                                                                                   │
│ 🛡️ Guardian Efímero                                                             │
│ Escanea recursos zombis en Azure y obtén recomendaciones del agente IA          │
│                                                                                   │
│ ┌─ ⚠️ ADVERTENCIA ────────────────────────────────────────────────────────────┐ │
│ │ Esta aplicación NO ejecuta comandos en Azure automáticamente.               │ │
│ │ Solo genera recomendaciones basadas en análisis FinOps.                     │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│ ┌─ SIDEBAR: ⚙️ Configuración ──────────────────────────────────────────────────┐ │
│ │                                                                               │ │
│ │ Guardian Efímero te ayuda a:                                                 │ │
│ │ 1. 🔍 Escanear 10 tipos de recursos zombis                                  │ │
│ │ 2. 🤖 Obtener recomendaciones del agente IA                                 │ │
│ │ 3. ✅ Revisar y aprobar cambios                                             │ │
│ │ 4. 📋 Generar comandos az CLI                                               │ │
│ │                                                                               │ │
│ │ [🔄 Limpiar caché]                                                           │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│ ══════════════════════════════════════════════════════════════════════════════   │
│                                                                                   │
│ 1️⃣ ESCANEAR AZURE                                                               │
│                                                                                   │
│ Detecta los 10 tipos de recursos zombis en tu suscripción:                       │
│ • 💾 Discos sin adjuntar                  • 🔗 Network Interfaces sin VM         │
│ • 📡 IPs públicas huérfanas               • 🔐 Key Vaults sin tenant            │
│ • 💾 Bases de datos SQL offline           • ⚖️ Load Balancers sin reglas        │
│ • 🖥️ VMs no ejecutándose                  • 📸 Snapshots antiguos (>90 días)    │
│ • 📦 Storage unavailable                                                         │
│ • 🏗️ App Service Plans vacíos                                                   │
│                                                                                   │
│ [🔍 Ejecutar escaneo] ◄─── Click aquí para comenzar                            │
│                                                                                   │
│ Si ya se ejecutó:                                                                │
│ ───────────────────────────────────────────────────────────────────────────────  │
│                                                                                   │
│ 📊 Total de recursos │ 🏷️ Tipos de zombis │ 💰 Ahorro potencial │ 📈 Ambigüedad│
│        15            │        6           │     847.50€/mes    │  2.5 avg     │
│                                                                                   │
│ 📋 Recursos detectados                                                           │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ Tipo         │ Nombre                │ Grupo          │ Ahorro        │    │ │
│ ├─────────────────────────────────────────────────────────────────────────────┤ │
│ │ disk         │ disk-unused-001       │ prod-rg        │ 400.00€       │    │ │
│ │ ip           │ ip-orphaned-042       │ dev-rg         │ 3.00€         │    │ │
│ │ disk         │ disk-unattached-99    │ test-rg        │ 240.00€       │    │ │
│ │ storage      │ oldstg2022            │ legacy-rg      │ 180.00€       │    │ │
│ │ sql          │ database-archive      │ prod-rg        │ 45.00€        │    │ │
│ │ ...          │ ...                   │ ...            │ ...           │    │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│ ══════════════════════════════════════════════════════════════════════════════   │
│                                                                                   │
│ 2️⃣ RECOMENDACIONES DEL AGENTE IA                                                │
│                                                                                   │
│ [🤖 Obtener recomendaciones IA] ◄─── Click para obtener análisis del agente    │
│                                                                                   │
│ Si ya se ejecutó:                                                                │
│ ───────────────────────────────────────────────────────────────────────────────  │
│                                                                                   │
│ 🗑️ Borrar: 8  │  📸 Snapshot: 3  │  ✅ Mantener: 4                             │
│                                                                                   │
│ 📋 Decisiones del agente                                                         │
│                                                                                   │
│ ▼ **disk-unused-001** - Acción: BORRAR (Confianza: 92%, Ahorro: 400.00€)       │
│   ├─ Recurso: disk-unused-001          │ Ubicación: eastus                       │
│   ├─ Grupo: prod-rg                    │ Confianza: 92%                          │
│   ├─ Decisión: `borrar`                                                         │
│   ├─ Ahorro potencial: 400.00€/mes                                              │
│   ├─ Razón: Disco de 500GB sin usar desde hace 6 meses, costo significativo     │
│   └─ ℹ️ Usando modelo Ollama (no fallback)                                      │
│                                                                                   │
│ ▼ **ip-orphaned-042** - Acción: BORRAR (Confianza: 100%, Ahorro: 3.00€)        │
│   ├─ Recurso: ip-orphaned-042          │ Ubicación: westeurope                   │
│   ├─ Grupo: dev-rg                     │ Confianza: 100%                         │
│   ├─ Decisión: `borrar`                                                         │
│   ├─ Ahorro potencial: 3.00€/mes                                                │
│   ├─ Razón: IP pública sin configuración ni asociaciones, puro costo            │
│   └─ ℹ️ Usando modelo Ollama (no fallback)                                      │
│                                                                                   │
│ ▼ **disk-unattached-99** - Acción: SNAPSHOT (Confianza: 65%, Ahorro: 240.00€)  │
│   ├─ Recurso: disk-unattached-99       │ Ubicación: northeurope                  │
│   ├─ Grupo: test-rg                    │ Confianza: 65%                          │
│   ├─ Decisión: `snapshot`                                                       │
│   ├─ Ahorro potencial: 240.00€/mes                                              │
│   ├─ Razón: Disco de 300GB que podría retenerse como snapshot por costes menores│
│   └─ ⚠️ Usando heurística (Ollama no disponible)                                │
│                                                                                   │
│ ══════════════════════════════════════════════════════════════════════════════   │
│                                                                                   │
│ 3️⃣ APROBACIÓN HUMANA                                                            │
│                                                                                   │
│ Selecciona los recursos que deseas procesar:                                     │
│                                                                                   │
│ ☑ ✓ Seleccionar todos                                                           │
│                                                                                   │
│ 📋 Recursos a procesar                                                           │
│                                                                                   │
│ ☑ **disk-unused-001**           │ Acción: `borrar`    │ Ahorro: 400.00€       ✅ │
│    Tipo: disk                   │ Confianza: 92%      │ RG: prod-rg               │
│                                                                                   │
│ ☐ **ip-orphaned-042**           │ Acción: `borrar`    │ Ahorro: 3.00€            │
│    Tipo: ip                     │ Confianza: 100%     │ RG: dev-rg                │
│                                                                                   │
│ ☑ **disk-unattached-99**        │ Acción: `snapshot`  │ Ahorro: 240.00€       ✅ │
│    Tipo: disk                   │ Confianza: 65%      │ RG: test-rg               │
│                                                                                   │
│ ☑ **storage-legacy-2022**       │ Acción: `borrar`    │ Ahorro: 180.00€       ✅ │
│    Tipo: storage                │ Confianza: 88%      │ RG: legacy-rg             │
│                                                                                   │
│ ───────────────────────────────────────────────────────────────────────────────  │
│                                                                                   │
│ ✅ Recursos seleccionados: 3  │  💰 Ahorro total: 820.00€/mes  │  📊 % total: 40% │
│                                                                                   │
│ ══════════════════════════════════════════════════════════════════════════════   │
│                                                                                   │
│ 4️⃣ COMANDOS AZ CLI SUGERIDOS                                                    │
│                                                                                   │
│ ┌─ ⚠️ ATENCIÓN CRÍTICA ────────────────────────────────────────────────────────┐ │
│ │ • Estos comandos NO se ejecutan automáticamente                              │ │
│ │ • Revísalos cuidadosamente antes de ejecutarlos                              │ │
│ │ • Algunos comandos pueden necesitar parámetros adicionales                   │ │
│ │ • Ejecuta en tu terminal: bash si es necesario                               │ │
│ │ • SIEMPRE haz una copia de seguridad antes de borrar recursos               │ │
│ └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│ 📋 Bloque de comandos listo para copiar                                          │
│                                                                                   │
│ ┌──────────────────────────────────────────────────────────────────────────────┐ │
│ │ #!/bin/bash                                                                  │ │
│ │ # Comandos generados por Guardian Efímero                                    │ │
│ │ # ADVERTENCIA: Ejecuta estos comandos bajo tu responsabilidad               │ │
│ │ # Algunos comandos pueden requerir parámetros adicionales                    │ │
│ │                                                                               │ │
│ │ az disk delete --resource-group 'prod-rg' --name 'disk-unused-001' --yes    │ │
│ │ az snapshot create --resource-group 'test-rg' --name 'disk-unattached-99-  │ │
│ │ snapshot' --source 'disk-unattached-99'                                      │ │
│ │ az storage account delete --resource-group 'legacy-rg' --name 'oldstg2022'  │ │
│ │ --yes                                                                         │ │
│ │                                                                               │ │
│ │ # Total de recursos a procesar: 3                                            │ │
│ └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                   │
│ 📋 Selecciona el código anterior, cópialo y ejecútalo en tu terminal            │
│                                                                                   │
│ [📥 Descargar script.sh]                                                        │
│                                                                                   │
│ ──────────────────────────────────────────────────────────────────────────────── │
│                                                                                   │
│ Guardian Efímero - FinOps para Azure                                             │
│ Proyecto de código abierto | No garantiza exactitud de cálculos de ahorro       │
│ Siempre revisa los comandos antes de ejecutarlos                                │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Top Banner (Siempre visible)
- Logo y título
- Descripción breve
- Banner de advertencia rojo/amarillo

### 2. Sidebar (Izquierda)
- Configuración y opciones
- Información general
- Botón para limpiar caché

### 3. Sección 1: Escanear Azure
**Estado inicial**: Vacío
- Explicación de qué se escanea (10 tipos)
- Botón principal: "🔍 Ejecutar escaneo"
- Spinner mientras se ejecuta

**Después del escaneo**:
- 4 métricas: Total, tipos, ahorro, ambigüedad
- Tabla de recursos con sorting/filtrado
- Columnas: Tipo, Nombre, Grupo, Ahorro

### 4. Sección 2: Recomendaciones IA
**Estado inicial**: Oculto
- Botón: "🤖 Obtener recomendaciones IA"
- Información sobre Ollama

**Después de obtener recomendaciones**:
- 3 métricas: Borrar, Snapshot, Mantener
- Cards expandibles para cada recurso
- Información: nombre, grupo, ubicación, confianza
- Decisión y razón
- Indicador de fallback/Ollama

### 5. Sección 3: Aprobación Humana
**Estado inicial**: Oculto
- Checkboxes para cada recurso
- Opción "Seleccionar todos"
- Vista tabular de recursos

**Información por recurso**:
- Checkbox (✓ o ☐)
- Nombre + tipo
- Acción + confianza
- Ahorro + grupo de recursos
- Indicador visual (✅ si seleccionado)

**Resumen**:
- Recursos seleccionados
- Ahorro total
- Porcentaje del total

### 6. Sección 4: Comandos az CLI
**Estado inicial**: Oculto (si no hay selecciones)
- Banner de advertencia crítico
- Bloque de código con syntax highlight
- Botón de descarga

**Características**:
- Script bash con header
- Comandos formatados
- Total de recursos al final
- Opción de copiar/descargar

### 7. Footer (Siempre visible)
- Créditos
- Advertencia final
- Links a documentación

## Flujo de Interacción

```
Usuario abre app
    ↓
Ve instrucciones en Sidebar y Sección 1
    ↓
Haz click en "Escanear"
    ↓
Espera spinner (1-2 min)
    ↓
Ve tabla de resultados
    ↓
Click en "Obtener recomendaciones"
    ↓
Espera spinner (variable)
    ↓
Ve cards de IA
    ↓
Expande cards para leer detalles
    ↓
Usa checkboxes para seleccionar
    ↓
Ve resumen de selección
    ↓
Lee bloque de comandos
    ↓
Copia/descarga comandos
    ↓
Abre terminal y ejecuta manualmente
```

## Elementos Visuales Clave

- 🛡️ Logo del proyecto
- 🔍 Escaneo
- 🤖 Inteligencia Artificial
- ✅ Aprobación
- 📋 Comandos/Scripts
- ⚠️ Advertencias
- 💰 Ahorro/Costos
- 📊 Métricas/Estadísticas
- 🏷️ Etiquetas/Tags

## Responsividad

La app está optimizada para:
- **Desktop** (1920x1080 y superior): Layout de 2-3 columnas
- **Tablet** (768-1024px): Layout adaptado
- **Mobile** (< 768px): Apilado verticalmente (parcialmente soportado)

## Paleta de Colores

- **Azul**: Información, botones primarios
- **Verde**: Éxito, confirmación
- **Rojo/Amarillo**: Advertencias, peligro
- **Gris**: Información secundaria, deshabilitado

## Elementos Interactivos

- Botones: "Ejecutar escaneo", "Obtener recomendaciones", "Limpiar caché"
- Checkboxes: Seleccionar recursos
- Expanders: Leer detalles de recomendaciones
- Dataframes: Ordenar/filtrar resultados
- Descargas: Guardar scripts
- Copiar: Código en clipboard
