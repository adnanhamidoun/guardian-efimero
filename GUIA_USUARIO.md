# 🛡️ Guardian Efímero - Guía de Usuario

## 📋 Descripción

**Guardian Efímero** es una aplicación Streamlit que escanea tu suscripción de Azure para detectar recursos "zombis" (sin usar o infrautilizados), obtiene recomendaciones de IA, y genera comandos `az CLI` listos para eliminarlos.

### 🎯 Objetivos
- ✅ Detectar 10 tipos de recursos zombis en Azure
- ✅ Estimar ahorro potencial (€/mes)
- ✅ Obtener recomendaciones del agente IA
- ✅ Generar comandos `az CLI` para eliminación
- ✅ Permitir selección manual antes de ejecutar

---

## 🚀 Inicio Rápido

### Paso 1: Autenticarse en Azure
```bash
az login
```

### Paso 2: Ejecutar la aplicación
```bash
streamlit run app.py
```

### Paso 3: Usar el dashboard
- Escanea recursos zombis
- Revisa recomendaciones IA
- Selecciona qué eliminar
- Copia/descarga comandos az CLI

---

## 🎨 Interfaz de Usuario

### Sección 1️⃣: Escanear Azure

Muestra el resultado del escaneo completo:

```
📊 Estadísticas:
   🔍 Total: 4 recursos
   🏷️  Tipos: 4 diferentes
   💰 Ahorro: €58.8/mes
   ❓ Ambigüedad media: 0.0

Desglose por tipo:
   💾 Discos: 1      📡 IPs: 1      📦 Storage: 1      🗄️ SQL: 1

Tabla de recursos detectados:
   | Tipo    | Nombre          | RG              | Acción | Confianza | Ahorro |
   |---------|-----------------|-----------------|--------|-----------|--------|
   | disk    | disk-test-...   | HamidounEl...   | borrar | 100%      | 0.8€   |
   | ip      | ip-test-efimero | HamidounEl...   | borrar | 100%      | 3.0€   |
   | storage | stgteste7180    | HamidounEl...   | borrar | 100%      | 10.0€  |
   | sql     | master          | HamidounEl...   | borrar | 100%      | 45.0€  |
```

### Sección 2️⃣: Recomendaciones IA

Muestra análisis del agente IA:

```
🤖 Análisis IA (4 recursos)

✅ disk-test-efimero
   Acción: Borrar
   Confianza: 100%
   Razón: Disco sin adjuntar detectado
   Ahorro: 0.8€/mes

✅ ip-test-efimero
   Acción: Borrar
   Confianza: 100%
   Razón: IP pública huérfana sin máquina asociada
   Ahorro: 3.0€/mes

✅ stgteste7180
   Acción: Borrar
   Confianza: 100%
   Razón: Storage sin contenedores ni blobs
   Ahorro: 10.0€/mes

✅ master (SQL)
   Acción: Borrar
   Confianza: 100%
   Razón: Base de datos offline
   Ahorro: 45.0€/mes
```

### Sección 3️⃣: Aprobación Humana

Selecciona qué recursos eliminar:

```
👤 Aprobar Cambios

Selecciona qué recursos deseas eliminar:

☑ 💾 disk-test-efimero
   Acción: borrar | Confianza: 100% | Ahorro: 0.8€/mes

☑ 📡 ip-test-efimero
   Acción: borrar | Confianza: 100% | Ahorro: 3.0€/mes

☑ 📦 stgteste7180
   Acción: borrar | Confianza: 100% | Ahorro: 10.0€/mes

☑ 🗄️ master (SQL)
   Acción: borrar | Confianza: 100% | Ahorro: 45.0€/mes

✅ Total seleccionado: 4 recursos
💰 Ahorro total: €58.8/mes
```

### Sección 4️⃣: Comandos az CLI

Muestra comandos listos para copiar/descargar:

```
🔧 Generador de Scripts az CLI

[📋 Copiar a Clipboard] [💾 Descargar como .sh] [ℹ️ Ver información]

✅ Resumen de Comandos

Comando 1/4:
  az disk delete --resource-group 'HamidounElHabtiAddan' --name 'disk-test-efimero' --yes

Comando 2/4:
  az network public-ip delete --resource-group 'HamidounElHabtiAddan' --name 'ip-test-efimero' --yes

Comando 3/4:
  az storage account delete --resource-group 'HamidounElHabtiAddan' --name 'stgteste7180' --yes

Comando 4/4:
  az sql server delete --resource-group 'HamidounElHabtiAddan' --name 'master' --yes

📊 Total: 4 comandos | 💰 Ahorro: €58.8/mes
```

---

## 🔍 Tipos de Recursos Detectados

| Tipo | Descripción | Razón de Zombi |
|------|-------------|-----------------|
| 💾 **Discos** | Discos no adjuntos | No están asociados a ninguna VM |
| 📡 **IPs Públicas** | IPs sin máquina | No tienen recurso asociado |
| 🗄️ **SQL Databases** | Bases de datos offline | No están en estado 'Online' |
| 🐢 **VMs Paradas** | Máquinas virtuales apagadas | Estado 'VM deallocated' |
| 📦 **Storage** | Cuentas de almacenamiento | Provisioning fallido, sin blobs/containers |
| 🔌 **NICs** | Interfaces de red sin VM | No están adjuntas a ninguna máquina |
| 🔑 **Key Vaults** | Bóvedas de claves sin tenant | No tienen tenant configurado |
| ⚖️ **Load Balancers** | Balanceadores sin reglas | No tienen reglas de balanceo |
| 📸 **Snapshots** | Snapshots muy antiguos | Creados hace >90 días |
| 🌐 **App Service Plans** | Planes sin aplicaciones | No tienen sitios web asociados |

---

## 💾 Usar los Comandos

### Opción 1: Copiar a Portapapeles
1. Haz clic en **"📋 Copiar a Clipboard"**
2. Pega en tu terminal: `Ctrl+V`
3. Ejecuta los comandos

### Opción 2: Descargar como Script
1. Haz clic en **"💾 Descargar como .sh"**
2. Guarda el archivo (ej: `delete-zombis.sh`)
3. Ejecuta: `bash delete-zombis.sh`

### Opción 3: Copiar Manual
1. Selecciona el texto del comando
2. Copia: `Ctrl+C`
3. Pega en tu terminal

---

## 🛡️ Características de Seguridad

### ✅ Sin Ejecución Automática
Los comandos **NO se ejecutan automáticamente**. Debes copiar/pegar manualmente.

### ✅ Confirmación Humana
Todos los cambios requieren selección manual y aprobación.

### ✅ Preview Completo
Puedes ver exactamente qué se va a eliminar antes de hacerlo.

### ✅ Estimación de Ahorro
Se muestra el ahorro potencial en €/mes para cada recurso.

---

## ⚙️ Configuración

### Variables de Entorno (Opcional)

```bash
# Usar Ollama local en vez de heurísticas
export OLLAMA_HOST=http://localhost:11434

# Configurar timeout
export OLLAMA_TIMEOUT=30
```

### Ejecutar con Ollama

```bash
# Asegurate que Ollama esté corriendo
ollama serve

# En otro terminal
streamlit run app.py
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'azure.identity'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error: "No se puede autenticar con Azure"
```bash
# Login en Azure
az login

# Verificar suscripción
az account show
```

### Error: "No se detectan recursos"
```bash
# Verificar que tienes permisos en Azure
az role assignment list --assignee $(az account show --query user.name -o tsv)

# Verificar que hay recursos en tu suscripción
az resource list --query "length([])" -o tsv
```

### Streamlit no inicia
```bash
# Verificar puerto
netstat -an | grep 8501

# Cambiar puerto
streamlit run app.py --server.port 8502
```

---

## 📊 Ejemplos de Uso

### Escenario 1: Limpiar Discos Huérfanos
1. Escanea recursos
2. Ve que hay 3 discos sin adjuntar
3. Selecciona los 3
4. Copia comandos
5. Ejecuta: `bash delete-disks.sh`

### Escenario 2: Eliminar IPs Públicas Innecesarias
1. Escanea recursos
2. Ve 5 IPs públicas sin VM
3. Selecciona las que no necesitas
4. Descarga script
5. Revisa antes de ejecutar

### Escenario 3: Auditoría de Almacenamiento
1. Escanea recursos
2. Genera reporte con costos potenciales
3. Comparte con el equipo
4. Aprueba eliminación en reunión

---

## 📞 Soporte

### Información del Sistema
- **Lenguaje**: Python 3.13
- **Framework**: Streamlit 1.41
- **Azure SDK**: azure-mgmt-resourcegraph 8.0
- **IA**: LangChain + Ollama (opcional)

### Logs
Los logs se guardan en:
```
~/.streamlit/logs
```

### Contacto
Para reportar bugs o sugerencias, crea un issue en el repositorio.

---

## 📜 Licencia

Este proyecto es software de código abierto. Úsalo libremente en tu organización.

---

## ⚡ Próximas Características

- [ ] Programar escaneos automáticos
- [ ] Exportar reportes PDF
- [ ] Integración con Teams/Slack
- [ ] Machine Learning para detección avanzada
- [ ] Soporte multi-cloud (AWS, GCP)

---

**¡Gracias por usar Guardian Efímero! 🛡️**

Última actualización: 2026-02-04
