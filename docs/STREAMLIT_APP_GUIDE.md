# Guardian Efímero - Interfaz Streamlit

## Descripción

`app.py` es una interfaz web interactiva basada en Streamlit para **Guardian Efímero**. Permite:

1. **Escanear Azure** - Detecta 10 tipos de recursos "zombis"
2. **Obtener recomendaciones IA** - Usa el agente IA para evaluar qué hacer con cada recurso
3. **Revisar y aprobar** - Interfaz para seleccionar qué recursos procesar
4. **Generar comandos az CLI** - Crea comandos listos para ejecutar (sin ejecutarlos automáticamente)

## Requisitos

- Python 3.10+
- Dependencias instaladas: `pip install -r requirements.txt`
- Autenticación de Azure configurada: `az login`
- (Opcional) Ollama ejecutándose en `localhost:11434` para recomendaciones IA mejoradas

## Instalación y Configuración

### 1. Instalar dependencias

```bash
# Si aún no lo has hecho
pip install -r requirements.txt

# O instala Streamlit directamente
pip install streamlit
```

### 2. Configurar autenticación Azure

```bash
az login
```

### 3. (Opcional) Configurar Ollama

Si quieres usar recomendaciones IA mejoradas:

```bash
# Instala Ollama desde https://ollama.ai
# Luego, en otra terminal:
ollama pull llama3.2:1b
ollama serve
```

Si no tienes Ollama, la app usará heurísticas locales automáticamente.

## Ejecución

### Opción 1: Con Streamlit directamente

```bash
streamlit run app.py
```

Abrirá la app en `http://localhost:8501`

### Opción 2: Con Make (si tienes disponible)

```bash
make streamlit
```

## Uso de la Interfaz

### Sección 1️⃣: Escanear Azure

1. Haz clic en **"🔍 Ejecutar escaneo"**
2. Espera a que finalice (1-2 minutos aproximadamente)
3. Verás una tabla con todos los recursos detectados
4. Métricas:
   - **Total de recursos**: Cantidad de zombis encontrados
   - **Tipos de zombis**: Número de categorías diferentes
   - **Ahorro potencial**: Ahorro mensual estimado
   - **Ambigüedad**: Promedio de recursos por tipo

### Sección 2️⃣: Recomendaciones del Agente IA

1. Haz clic en **"🤖 Obtener recomendaciones IA"**
2. El agente IA analizará cada recurso
3. Verás:
   - **Acción propuesta**: borrar, snapshot, o mantener
   - **Confianza**: Qué tan seguro está el agente (0-100%)
   - **Razón**: Explicación de por qué sugiere esa acción
   - **Ahorro**: Cuánto dinero ahorrarías

### Sección 3️⃣: Aprobación Humana

1. Revisa cada recurso cuidadosamente
2. Usa los checkboxes para seleccionar cuáles quieres procesar
3. Usa **"✓ Seleccionar todos"** para una selección rápida
4. Verás:
   - **Recursos seleccionados**: Cuántos has marcado
   - **Ahorro total**: Ahorro combinado de los seleccionados
   - **% del total**: Qué porcentaje del total estás incluyendo

### Sección 4️⃣: Comandos az CLI Sugeridos

1. La app genera automáticamente comandos basados en tu selección
2. **⚠️ ADVERTENCIA CRÍTICA**:
   - Los comandos NO se ejecutan automáticamente
   - DEBES revisarlos manualmente antes de ejecutar
   - Algunos comandos pueden necesitar parámetros adicionales
   - **Siempre haz una copia de seguridad antes**

3. Opciones:
   - **Copiar**: Selecciona el código, cópialo con Ctrl+C
   - **Descargar**: Descarga como `guardian-efimero-commands.sh`

## Estructura de Recursos Detectados

La app detecta 10 tipos de recursos:

| Tipo | Descripción | Acción típica |
|------|-------------|---|
| **disk** | Discos sin adjuntar | Borrar si no se usa |
| **ip** | IPs públicas huérfanas | Borrar siempre |
| **sql** | Bases de datos SQL offline | Borrar |
| **vm** | VMs no ejecutándose | Borrar o iniciar |
| **storage** | Storage accounts sin disponibilidad | Borrar |
| **appserviceplan** | App Service Plans vacíos | Borrar |
| **nic** | Network Interfaces sin VM | Borrar |
| **keyvault** | Key Vaults sin tenant | Borrar |
| **loadbalancer** | Load Balancers sin reglas | Borrar |
| **snapshot** | Snapshots antiguos (>90 días) | Borrar |

## Ejemplos de Comandos Generados

### Borrar disco
```bash
az disk delete --resource-group 'mi-rg' --name 'disco-zombi' --yes
```

### Borrar IP pública
```bash
az network public-ip delete --resource-group 'mi-rg' --name 'ip-huerfana' --yes
```

### Crear snapshot
```bash
az snapshot create --resource-group 'mi-rg' --name 'disco-zombi-snapshot' --source 'disco-zombi'
```

### Borrar VM
```bash
az vm delete --resource-group 'mi-rg' --name 'vm-parada' --yes
```

## Flujo de Trabajo Recomendado

1. **Escanear** → Detecta todos los recursos
2. **Analizar** → Obtén recomendaciones IA
3. **Revisar** → Examine cuidadosamente cada recomendación
4. **Seleccionar** → Elige qué recursos procesar
5. **Generar** → Obtén los comandos
6. **Revisar nuevamente** → Asegúrate de entender cada comando
7. **Ejecutar** → Copia los comandos a tu terminal y ejecútalos manualmente

## Solución de Problemas

### "Error: No se puede conectar a Ollama"

**Solución**: La app usa heurísticas automáticamente. Los resultados serán basados en reglas simples en lugar del modelo IA.

### "Error de autenticación Azure"

**Solución**: 
```bash
az login
az account set --subscription "<tu-subscription-id>"
```

### "La app se congela durante el escaneo"

**Solución**: El escaneo de Azure puede tardar 1-2 minutos. Es normal. Si tarda más:
- Comprueba tu conexión de red
- Verifica que `az login` esté configurado
- Intenta de nuevo

### "No se generan comandos"

**Solución**: 
- Asegúrate de haber seleccionado al menos un recurso (checkboxes)
- Verifica que los resultados del escaneo y IA se hayan completado

## Integración con el Código Existente

La app reutiliza:
- `src.detectores.full_scan()` - Para escanear recursos
- `src.ia_agente.agente_main()` - Para obtener recomendaciones IA
- `src.cli_generator` - Para generar comandos az CLI

Puedes reutilizar el módulo `src.cli_generator` en tus propios scripts:

```python
from src.cli_generator import generate_az_command, build_script

# Generar un comando individual
cmd = generate_az_command(
    {"tipo": "disk", "nombre": "d1", "resourceGroup": "rg1"},
    "delete"
)
print(cmd)  # az disk delete --resource-group 'rg1' --name 'd1' --yes

# Construir un script completo
script = build_script(scan_results, ia_results, selected)
```

## Seguridad

⚠️ **IMPORTANTE**:

- Esta app **NO ejecuta comandos de Azure automáticamente**
- Todos los comandos generados deben ser **revisados manualmente**
- La app genera sugerencias basadas en heurísticas y IA, no decisiones finales
- **Eres responsable de lo que ejecutes** en tu suscripción de Azure
- **Siempre haz copias de seguridad** antes de borrar recursos

## Limitaciones

- Los cálculos de ahorro son **estimaciones aproximadas** basadas en precios de referencia
- El agente IA puede no ser 100% preciso en sus recomendaciones
- Algunos recursos complejos pueden requerir parámetros adicionales en los comandos
- No detecta recursos en subscripciones a las que no tengas acceso

## Feedback y Mejoras

Si encuentras bugs o tienes sugerencias:
1. Documenta el problema
2. Incluye los pasos para reproducirlo
3. Comparte cualquier salida de error

## Licencia

Mismo que el proyecto principal: Guardian Efímero
