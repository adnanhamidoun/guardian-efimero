# 🛡️ Guardian Efímero v1 — 8 Detectores Testeables

**FinOps Azure** | Detecta recursos "zombis" para optimizar costos

---

## Vision General

Guardian Efímero v1 es una aplicación Streamlit que **detecta** recursos Azure innecesarios (zombis) sin ejecutar cambios automáticamente. Permite:

1. **Escanear** 8 tipos de zombis con queries KQL
2. **Analizar** con recomendaciones IA híbrida (heurística + Ollama)
3. **Revisar** manualmente (aprobación humana)
4. **Generar** comandos `az` CLI para ejecución manual

### ¿Por qué 8 detectores?

**v1** es una versión testeable que puede validarse en minutos con recursos reales de Azure creados por scripts. Los 8 detectores fueron elegidos por ser:
- **Reproducibles**: Puedes crearlos con `az` CLI en PowerShell
- **Comprobables**: Queries KQL simples y confiables
- **Económicos**: Detectan desperdicio real
- **Path a 10**: Estructura lista para agregar Storage, SQL, KeyVault en v2

---

## Los 8 Detectores v1

| # | Orden | Detector | ¿Qué es? | ¿Cómo crearlo? | ¿Cómo lo detecta? | ¿Cómo borrarlo? | Ahorro | Confianza |
|---|-------|----------|----------|----------------|-------------------|-------------------|--------|-----------|
| 1 | disk | Discos sin adjuntar | Managed Disk no conectado a VM | `az disk create --size-gb 32` | diskState == 'unattached' OR isempty(managedBy) | `az disk delete` | 0.08€/GB/mes | 9.5/10 |
| 2 | ip | IPs públicas huérfanas | Public IP sin asociación | `az network public-ip create` | ipConfiguration vacio/null | `az network public-ip delete` | 3€/mes | 9/10 |
| 3 | nic | NIC sin VM | Network Interface sin máquina asociada | `az network nic create` (sin VM) | virtualMachine vacio/null | `az network nic delete` | 1€/mes | 9.5/10 |
| 4 | vm | VM deallocated | Máquina parada (costo de almacenamiento) | `az vm deallocate` | powerState has 'deallocated' | `az vm delete` | 60€/mes | 9.5/10 |
| 5 | loadbalancer | LB sin reglas | Load Balancer sin ninguna regla | `az network lb create` (vacío) | loadBalancingRules array length == 0 | `az network lb delete` | 2€/mes | 8.5/10 |
| 6 | appserviceplan | Plan vacío | App Service Plan sin apps web | `az appservice plan create` (sin apps) | numberOfSites == 0 | `az appservice plan delete` | 5€/mes | 9/10 |
| 7 | snapshot | Snapshot antiguo | Snapshot >90d (parametrizable) | `az snapshot create` + esperar (usar age=0 en demo) | timeCreated <= ago(90d) | `az snapshot delete` | 0.08€/GB/mes | 8/10 |
| 8 | nsg | NSG sin asociar | Network Security Group sin NIC/subnet | `az network nsg create` (sin asociar) | networkInterfaces==0 AND subnets==0 | `az network nsg delete` | 0.5€/mes | 8.5/10 |

---

## Instalación y Setup

### Requisitos

- **Python 3.11+**
- **Azure CLI** (`az`) autenticado: `az login`
- **Streamlit**: `pip install streamlit`
- **PowerShell 5.1+** (para scripts demo en Windows)
- **Ollama** (opcional, en `http://localhost:11434` para IA mejorada)

### Instalación Rápida

```bash
# Clonar/descargar proyecto
cd guardian-efimero

# Crear entorno virtual
python -m venv venv
venv\Scripts\Activate.ps1           # Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt

# Autenticarse en Azure
az login
```

---

## Uso — Flujo Completo

### Opción A: Demo Rápida (5 min)

```powershell
# 1. Setup: Crea 8 recursos demo
.\scripts\demo_setup.ps1

# 2. Verifica que se crearon
.\scripts\demo_verify.ps1

# 3. Abre UI
streamlit run app.py
```

**En la UI:**
- Sidebar: Activa "🎯 DEMO MODE" → baja snapshot_age_days a 0
- Sección "1️⃣ Scan" → Click "🔍 Ejecutar escaneo"
- Esperado: Ver los 8 tipos de zombis detectados

```powershell
# 4. Limpia recursos
.\scripts\demo_cleanup.ps1
```

### Opción B: Escaneo Producción

```bash
# 1. Abre UI
streamlit run app.py

# 2. En sidebar:
#    - Resource Group Filter: (opcional) tu RG
#    - snapshot_age_days: 90 (default)
#    - DEMO MODE: OFF

# 3. Sección "1️⃣ Scan"
#    - Click "🔍 Ejecutar escaneo"

# 4. Sección "2️⃣ Recomendaciones IA"
#    - Click "🤖 Obtener recomendaciones"
#    - Revisa qué sugiere el agente

# 5. Sección "3️⃣ Aprobación Humana"
#    - Selecciona los que quieres borrar
#    - Ves ahorro potencial

# 6. Sección "4️⃣ Comandos az CLI"
#    - Copia los comandos
#    - Ejecuta en tu terminal (após review)
```

---

## Queries KQL Exactas (por Detector)

### 1. DISCO SIN ADJUNTAR

```kql
resources
| where type == 'microsoft.compute/disks'
| extend diskState = tostring(properties.diskState)
| where tolower(diskState) == 'unattached' or isempty(tostring(managedBy)) or tostring(managedBy) == ''
| project id, name, resourceGroup, subscriptionId, location, diskSizeGB = properties.diskSizeGB
```

**Cmd create demo:**
```powershell
az disk create --resource-group "RG" --name "zombie-disk-unattached" --size-gb 32 --sku Standard_LRS --tags "demo=zombi"
```

**Cmd detección (CLI):**
```bash
az graph query -q "resources | where type == 'microsoft.compute/disks' | where properties.diskState == 'Unattached' or isempty(tostring(properties.managedBy))"
```

---

### 2. IP PÚBLICA HUÉRFANA

```kql
resources
| where type == 'microsoft.network/publicipaddresses'
| where isnull(properties.ipConfiguration) or tostring(properties.ipConfiguration) == ''
| project id, name, resourceGroup, subscriptionId, location, ipAddress = tostring(properties.ipAddress)
```

**Cmd create demo:**
```powershell
az network public-ip create --resource-group "RG" --name "zombie-orphaned-ip" --sku Standard --tags "demo=zombi"
```

---

### 3. NETWORK INTERFACE SIN VM

```kql
resources
| where type == 'microsoft.network/networkinterfaces'
| where isnull(properties.virtualMachine) or tostring(properties.virtualMachine) == ''
| project id, name, resourceGroup, subscriptionId, location
```

**Cmd create demo:**
```powershell
# Primero crear VNET/subnet
az network vnet create --resource-group "RG" --name "zombie-vnet" --address-prefix 10.0.0.0/16 --subnet-name "zombie-subnet" --subnet-prefix 10.0.0.0/24

# Crear NIC sin VM
az network nic create --resource-group "RG" --name "zombie-orphaned-nic" --vnet-name "zombie-vnet" --subnet "zombie-subnet" --tags "demo=zombi"
```

---

### 4. VM DEALLOCATED

```kql
resources
| where type == 'microsoft.compute/virtualmachines'
| extend powerState = tostring(properties.statuses[].displayStatus)
| where powerState has 'deallocated' or powerState has 'stopped'
| project id, name, resourceGroup, subscriptionId, location, powerState
```

**Cmd create demo:**
```powershell
# Create + deallocate
az vm create --resource-group "RG" --name "zombie-deallocated-vm" --image UbuntuLTS --admin-username azureuser --generate-ssh-keys --tags "demo=zombi" --no-wait
az vm deallocate --resource-group "RG" --name "zombie-deallocated-vm" --no-wait
```

---

### 5. LOAD BALANCER SIN REGLAS

```kql
resources
| where type == 'microsoft.network/loadbalancers'
| extend ruleCount = array_length(properties.loadBalancingRules)
| where ruleCount == 0 or isempty(ruleCount)
| project id, name, resourceGroup, subscriptionId, location, ruleCount
```

**Cmd create demo:**
```powershell
# PIP para LB
az network public-ip create --resource-group "RG" --name "zombie-lb-ip" --sku Standard

# LB sin reglas
az network lb create --resource-group "RG" --name "zombie-empty-lb" --sku Standard --public-ip-address "zombie-lb-ip" --frontend-ip-name "frontend" --backend-pool-name "backend" --tags "demo=zombi"
```

---

### 6. APP SERVICE PLAN VACÍO

```kql
resources
| where type == 'microsoft.web/serverfarms'
| extend numberOfSites = toint(properties.numberOfSites)
| where numberOfSites == 0 or isempty(numberOfSites)
| project id, name, resourceGroup, subscriptionId, location, numberOfSites
```

**Cmd create demo:**
```powershell
az appservice plan create --resource-group "RG" --name "zombie-empty-plan" --sku B1 --tags "demo=zombi"
```

---

### 7. SNAPSHOT ANTIGUO

```kql
resources
| where type == 'microsoft.compute/snapshots'
| extend timeCreated = todatetime(properties.timeCreated)
| where timeCreated <= ago(90d)
| project id, name, resourceGroup, subscriptionId, location, diskSizeGB = properties.diskSizeGB, timeCreated
```

**Nota sobre snapshots en demo:** Los snapshots creados hoy **no serán detectados** con umbral 90 días. En demo_mode, baja `snapshot_age_days` a 0 para que se detecten independientemente de edad.

**Cmd create demo:**
```powershell
# Disco fuente
az disk create --resource-group "RG" --name "zombie-snapshot-source" --size-gb 16 --sku Standard_LRS

# Snapshot
az snapshot create --resource-group "RG" --name "zombie-old-snapshot" --source "zombie-snapshot-source" --tags "demo=zombi"
```

---

### 8. NSG SIN ASOCIAR

```kql
resources
| where type == 'microsoft.network/networksecuritygroups'
| extend networkInterfaceIds = array_length(properties.networkInterfaces)
| extend subnetIds = array_length(properties.subnets)
| where (networkInterfaceIds == 0 or isempty(networkInterfaceIds)) and (subnetIds == 0 or isempty(subnetIds))
| project id, name, resourceGroup, subscriptionId, location, networkInterfaceIds, subnetIds
```

**Cmd create demo:**
```powershell
az network nsg create --resource-group "RG" --name "zombie-unassociated-nsg" --tags "demo=zombi"
```

---

## Validación Manual en la UI

Después de ejecutar `demo_setup.ps1` y escanear:

1. **Sección Scan** debe mostrar:
   - Total de recursos: ≥8
   - Tipos: disk, ip, nic, vm, loadbalancer, appserviceplan, snapshot, nsg
   - Ahorro potencial: >80€/mes

2. **Sección Recomendaciones IA** (si Ollama está activo):
   - Mínimo 4⁄5 recursos con "Borrar"
   - Confianza 70-100%

3. **Sección Aprobación Humana**:
   - Todos los recursos seleccionables
   - Checkboxes funcionales

4. **Sección Comandos az CLI**:
   - 8 comandos `az delete` listos
   - Pueden copiarse y pegarse en terminal

---

## Limitaciones Conocidas y Falsos Positivos

### Snapshot Age

- **Limitación**: Snapshots creados hoy no se detectan como "antiguos" con umbral 90d
- **Workaround**: En demo_mode, baja `snapshot_age_days` a 0-1
- **Futuro**: ARG permite filtro temporal; podremos agregar "created in last X hours" en v2

### App Service Plan (NumberOfSites)

- **Limitación**: El campo `numberOfSites` en ARG **a veces no se actualiza inmediatamente** tras eliminar la última app
- **Confidence**: 9/10 (buena en la mayoría de casos)
- **Workaround**: Esperar 5min entre eliminar app y escanear, o revisar portal

### VM PowerState

- **Limitación**: `powerState` en propiedades es deprecated en algunas suscripciones. Usamos `properties.statuses[].displayStatus`
- **Confidence**: 9.5/10
- **Conocido**: En algunos casos, VMs "stopped" pueden no aparecer

### NSG (subnets/networkInterfaces)

- **Limitación**: Algunos NSG pueden estar "indirectamente asociados" vía VNET pero no capturados en `properties.subnets`
- **Confidence**: 8.5/10
- **Nota**: Es un falso positivo bajo pero posible

---

## Troubleshooting

### Error: "No autenticado en Azure"

```bash
az login
# Selecciona tu suscripción si tienes varias
az account set --subscription "YOUR-SUBSCRIPTION-ID"
```

### Error: "Ollama no disponible"

Streamlit seguirá funcionando con **heurísticas puras** (100% confiabilidad):
```bash
# Si quieres IA mejorada, instala Ollama:
# https://ollama.ai → Descargar y ejecutar
ollama pull llama3.2:1b
ollama serve
```

### Snapshots no se detectan

- En sidebar, baja `snapshot_age_days` a 0 (demo_mode lo hace automático)
- Los snapshots creados hoy solo se ven con umbral 0

### "ResourceGroup no tiene recursos"

- Verifica: `az group exists --name "TU-RG"`
- Si escaneas con filter, asegúrate de que hay recursos en ese RG
- Sin filter: escanea **todas las suscripciones** (puede ser lento)

---

## Estructura del Proyecto

```
guardian-efimero/
├── app.py                   # UI Streamlit principal
├── src/
│   ├── detectores.py       # 8 detectores v1 (KQL queries)
│   ├── ia_agente.py        # Agente híbrido (heurística + Ollama)
│   ├── cli_generator.py    # Generador comandos az
│   └── tools/
│       └── arg_detector.py # Cliente Azure Resource Graph
├── scripts/
│   ├── demo_setup.ps1      # Crea 8 recursos demo
│   ├── demo_cleanup.ps1    # Borra recursos demo (tag demo=zombi)
│   └── demo_verify.ps1     # Verifica acceso a ARG
├── requirements.txt         # Dependencias Python
└── docs/
    └── ... documentación adicional
```

---

## Roadmap

### v1 (actual) — 8 Detectores Testeables
- ✅ 8 detectores KQL simples
- ✅ Demo setup/cleanup/verify en PowerShell
- ✅ UI Streamlit con filtros
- ✅ Ahorro estimado por tipo

### v2 (próximo) — 10 Detectores
- [ ] Storage Accounts (criterios mejorados)
- [ ] SQL Databases (con fallback)
- [ ] KeyVaults (si en producción)
- [ ] Ahorro dinámico por ubicación/SKU

### v3+ (futuro)
- [ ] Machine Learning para detección de "similares a zombis"
- [ ] Historial de scans
- [ ] Webhook para notificaciones
- [ ] Multi-suscripción Dashboard

---

## Contribuciones

👉 Ver `CONTRIBUTING.md` si quieres mejorar v1 o proponer detectores nuevos.

---

## Licencia

MIT | Redistribuible con atribución.

---

## Contacto y Support

- 📧 Email: (configurar)
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Guardian Efímero** — Ayudándote a limpiar Azure, un zombi a la vez. 🛡️
