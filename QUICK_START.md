# 🚀 QUICK START - Guardian Efímero

## 1️⃣ Verificación Previa (5 minutos)

### ✅ Requisitos Previos
```bash
# Verificar Python 3.13+
python --version

# Verificar Azure CLI
az version

# Verificar autenticación Azure
az account show
```

### ✅ Instalar Dependencias
```bash
# Opción 1: Script automático (recomendado)
python install_dependencies.py

# Opción 2: Manual
pip install -r requirements.txt
```

---

## 2️⃣ Ejecutar la Aplicación

### Opción A: Dashboard Streamlit (RECOMENDADO)
```bash
# Ejecutar
streamlit run app.py

# Se abrirá automáticamente en:
# http://localhost:8501
```

### Opción B: Escaneo Terminal
```bash
# Solo escanear sin UI
python src/guardian.py
```

---

## 3️⃣ Usar el Dashboard

### 📍 Ubicación: http://localhost:8501

### 🎯 4 Secciones Interactivas

#### 🔍 **Sección 1: Escanear Azure**
1. Haz clic en **"Escanear Azure"**
2. Espera ~2 segundos
3. Ver resultados:
   - **Estadísticas**: Total, Ahorro, Ambigüedad
   - **Desglose**: 💾 Discos, 📡 IPs, 📦 Storage, 🗄️ SQL
   - **Tabla**: Todos los recursos detectados

#### 🤖 **Sección 2: Recomendaciones IA**
- Se ejecuta automáticamente después del escaneo
- Muestra para cada recurso:
  - ✅ Acción (Borrar, Retener, etc.)
  - 📊 Confianza (%)
  - 💬 Razón
  - 💰 Ahorro €/mes

#### 👤 **Sección 3: Aprobación Humana**
1. **Selecciona** qué recursos eliminar (☑️)
2. Ve información clara:
   - 💾 Tipo con emoji
   - Acción recomendada
   - Confianza %
   - Ahorro €/mes
3. **Totales dinámicos** se actualizan:
   - Total seleccionados
   - Total ahorro

#### 🔧 **Sección 4: Comandos az CLI**
1. Selecciona recursos en Sección 3
2. Los comandos se generan automáticamente
3. **3 opciones**:
   - 📋 **Copiar a Clipboard** - Copia a portapapeles
   - 💾 **Descargar como .sh** - Descarga script
   - ℹ️ **Ver información** - Muestra detalles
4. Ver comandos numerados (Comando 1/4, 2/4, etc.)
5. Total de comandos y ahorro mostrado

---

## 📋 Ejemplos Prácticos

### Ejemplo 1: Limpiar Storage Vacío

```
1. Abre http://localhost:8501
2. Haz clic "Escanear Azure"
3. En Sección 3, busca "stgteste7180" (📦 Storage)
4. Marca el checkbox ☑
5. Ve el comando en Sección 4:
   az storage account delete --resource-group 'RG' --name 'stgteste7180' --yes
6. Copia con "📋 Copiar a Clipboard"
7. Pega en tu terminal
8. El storage se elimina
```

### Ejemplo 2: Múltiples Recursos

```
1. Escanea Azure
2. En Sección 3, marca 4 checkboxes:
   ☑ disk-test-efimero
   ☑ ip-test-efimero
   ☑ stgteste7180
   ☑ master (SQL)
3. En Sección 4, ves 4 comandos:
   Comando 1/4: az disk delete ...
   Comando 2/4: az network public-ip delete ...
   Comando 3/4: az storage account delete ...
   Comando 4/4: az sql server delete ...
4. Copia todo con "📋 Copiar a Clipboard"
5. Descarga con "💾 Descargar como .sh"
```

### Ejemplo 3: Crear Script y Ejecutar

```bash
# 1. Descarga script desde UI
# Guarda como: delete-zombis.sh

# 2. Revisa el contenido
cat delete-zombis.sh

# 3. Ejecuta
bash delete-zombis.sh

# 4. Confirma cada comando (--yes flag incluido)
```

---

## 🔒 Seguridad - Cosas Importantes

### ⚠️ **Recuerda**
- ✅ Los comandos **NO se ejecutan automáticamente**
- ✅ Debes copiar/pegar manualmente en tu terminal
- ✅ Puedes revisar cada comando antes de ejecutar
- ✅ Cada comando tiene `--yes` para confirmar
- ✅ Los cambios son **PERMANENTES** - no hay deshacer

### 🛡️ **Mejores Prácticas**
1. **Revisa cada comando** antes de ejecutar
2. **Ejecuta de uno en uno** no todos a la vez
3. **Haz backup** de datos importantes
4. **Testa en DEV primero** no PROD
5. **Documenta qué eliminaste**

---

## 🐛 Troubleshooting

### ❌ Error: "ModuleNotFoundError"
```bash
# Solución
pip install -r requirements.txt
python install_dependencies.py
```

### ❌ Error: "No se conecta a Azure"
```bash
# Solución
az login
az account show  # Verifica conexión
```

### ❌ Error: "No detecta recursos"
```bash
# Solución 1: Verifica permisos
az role assignment list

# Solución 2: Verifica recursos existen
az resource list --query "length([])"

# Solución 3: Cambia suscripción
az account set --subscription <ID>
```

### ❌ Error: "Streamlit no inicia"
```bash
# Solución 1: Cambiar puerto
streamlit run app.py --server.port 8502

# Solución 2: Limpiar cache
streamlit cache clear

# Solución 3: Verificar puerto disponible
netstat -an | grep 8501
```

### ❌ Ollama no conecta (solo aviso)
```bash
# No es crítico - usa heurísticas automáticamente
# Si quieres Ollama:

# Opción 1: Descargar desde https://ollama.ai
# Opción 2: Docker
docker run -d -p 11434:11434 ollama/ollama
ollama run llama2
```

---

## 📊 Interpretación de Resultados

### Desglose por Tipo
```
💾 Discos: 1    → 1 disco sin adjuntar
📡 IPs: 1       → 1 IP pública huérfana
📦 Storage: 1   → 1 cuenta storage vacía
🗄️ SQL: 1       → 1 base de datos offline
```

### Confianza IA
```
100%  → Seguro que es zombi, elimina
90%   → Muy probable, verifica primero
70%   → Probable, revisa con el equipo
<50%  → Incierto, no elimines
```

### Ahorro
```
€58.8/mes   → Ahorro potencial si eliminas todo
€10€0       → Ahorro si eliminas solo stgteste7180
```

---

## ✨ Características Principales

### ✅ Qué Detecta
- ✅ Discos sin adjuntar
- ✅ IPs públicas huérfanas
- ✅ SQL databases offline
- ✅ VMs paradas
- ✅ Storage vacío (⭐ stgteste7180)
- ✅ NICs sin VM
- ✅ Key Vaults sin tenant
- ✅ Load Balancers sin reglas
- ✅ Snapshots muy antiguos
- ✅ App Service Plans sin apps

### ✅ Qué Genera
- ✅ Comandos `az CLI` correctos
- ✅ Scripts `.sh` ejecutables
- ✅ Copy-paste listo
- ✅ Totales de ahorro
- ✅ Estimaciones de confianza

### ✅ Qué NO Hace
- ❌ Ejecutar comandos automáticamente
- ❌ Borrar sin aprobación
- ❌ Modificar archivos
- ❌ Requerir Ollama (usa fallback)

---

## 📱 Interfaz Visual

```
┌─────────────────────────────────────────────────┐
│ 🛡️ Guardian Efímero                            │
├─────────────────────────────────────────────────┤
│                                                  │
│ 📊 Estadísticas                                 │
│    🔍 Total: 4  🏷️ Tipos: 4  💰 €58.8/mes     │
│                                                  │
│ Desglose:                                       │
│    💾 1    📡 1    📦 1    🗄️ 1               │
│                                                  │
├─────────────────────────────────────────────────┤
│ 🤖 Recomendaciones IA (4 analizados)           │
│    ✅ stgteste7180: Borrar, 100%, €10         │
│    ✅ disk-test...: Borrar, 100%, €0.8       │
│    ...                                          │
├─────────────────────────────────────────────────┤
│ 👤 Aprobación Humana                           │
│    ☑ 💾 disk-test-efimero... (€0.8)           │
│    ☑ 📡 ip-test-efimero... (€3.0)             │
│    ☑ 📦 stgteste7180... (€10.0) ⭐            │
│    ☑ 🗄️ master... (€45.0)                     │
│                                                  │
│    ✅ 4 Seleccionados | 💰 €58.8              │
├─────────────────────────────────────────────────┤
│ 🔧 Comandos az CLI                             │
│                                                  │
│    [📋 Copy] [💾 Download] [ℹ️ Info]         │
│                                                  │
│    Comando 1/4:                                 │
│    az disk delete --resource-group '...' ...  │
│                                                  │
│    Comando 2/4:                                 │
│    az network public-ip delete ...             │
│                                                  │
│    Comando 3/4:                                 │
│    az storage account delete --name ...        │
│                                                  │
│    Comando 4/4:                                 │
│    az sql server delete ...                    │
│                                                  │
│    📊 Total: 4 comandos | 💰 €58.8/mes       │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Checklist de Uso

- [ ] Ejecuté `az login`
- [ ] Ejecuté `streamlit run app.py`
- [ ] Abrí http://localhost:8501
- [ ] Hice clic "Escanear Azure"
- [ ] Vi los 4 tipos de zombis
- [ ] Incluye stgteste7180 (📦 Storage)
- [ ] Seleccioné recursos en "Aprobación"
- [ ] Vi los comandos CLI
- [ ] Copié/Descargué comandos
- [ ] (OPCIONAL) Ejecuté los comandos

---

## 💡 Tips & Tricks

### Tip 1: Copiar Comandos Rápido
```
1. En Sección 4, haz clic [📋 Copy]
2. Ctrl+V en terminal
3. Enter
```

### Tip 2: Guardar Script para Después
```
1. En Sección 4, haz clic [💾 Download]
2. Guarda como: delete-zombis.sh
3. Ejecuta después: bash delete-zombis.sh
```

### Tip 3: Ver Todos los Detalles
```
1. En Sección 4, haz clic [ℹ️ Info]
2. Muestra: Tipo, Acción, Confianza, Razón
```

### Tip 4: Escaneo sin UI
```
python src/guardian.py
# JSON a stdout
```

---

## 📞 Ayuda

### Documentación Completa
- [GUIA_USUARIO.md](GUIA_USUARIO.md) - Guía detallada
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) - Detalles técnicos

### Verificación
- [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) - Estado actual
- [CHECKLIST_VALIDACION.md](CHECKLIST_VALIDACION.md) - Tests pasados

---

## 🚀 ¡Listo!

```bash
# 1. Autentica
az login

# 2. Ejecuta
streamlit run app.py

# 3. ¡Usa el dashboard!
# http://localhost:8501
```

**¡Bienvenido a Guardian Efímero! 🛡️**

---

**Última actualización**: 2026-02-04
**Versión**: 3.0
**Status**: ✅ PRODUCTION-READY
