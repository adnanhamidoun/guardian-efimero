# Az CLI Commands Reference

## Auto-Generated Commands by Guardian Efímero

Esta es una referencia de los tipos de comandos que Guardian Efímero genera automáticamente.

---

## 1. Discos (Disk) - Borrar

```bash
# Borrar un disco sin adjuntar
az disk delete --resource-group 'my-resource-group' --name 'unused-disk-001' --yes
```

### Variantes
```bash
# Sin confirmar automáticamente (solicitará confirmación)
az disk delete --resource-group 'my-rg' --name 'disk-name'

# Con información adicional
az disk delete -g 'my-rg' -n 'disk-name' --yes --verbose
```

---

## 2. IPs Públicas (Public IP) - Borrar

```bash
# Borrar una IP pública huérfana
az network public-ip delete --resource-group 'my-resource-group' --name 'orphaned-ip-042' --yes
```

### Variantes
```bash
# Forma corta
az network public-ip delete -g 'my-rg' -n 'ip-name' --yes

# Por ID de recurso
az resource delete --ids '/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Network/publicIPAddresses/ip-name'
```

---

## 3. Bases de Datos SQL - Borrar

```bash
# Borrar una base de datos SQL
az sql db delete --resource-group 'my-rg' --server 'my-server' --name 'offline-db' --yes
```

### Notas
⚠️ Requiere parámetro `--server`. Guardian Efímero lo indica como `<server-name>` - debes reemplazarlo.

### Variantes
```bash
# Obtener lista de servidores SQL
az sql server list --query "[].name"

# Borrar un servidor SQL completo
az sql server delete --resource-group 'my-rg' --name 'my-server' --yes
```

---

## 4. Máquinas Virtuales (VM) - Borrar

```bash
# Borrar una VM que no se está ejecutando
az vm delete --resource-group 'my-resource-group' --name 'stopped-vm' --yes
```

### Variantes
```bash
# Borrar sin esperar a confirmación
az vm delete -g 'my-rg' -n 'vm-name' --yes --no-wait

# Borrar con grupos de recursos
az group delete --name 'my-rg' --yes  # Borra todo en el RG
```

---

## 5. Cuentas de Almacenamiento (Storage Account) - Borrar

```bash
# Borrar una cuenta de almacenamiento
az storage account delete --resource-group 'my-rg' --name 'oldstorageaccount2022' --yes
```

### Notas
⚠️ Borrar una storage account borra todos sus contenidos.

### Variantes
```bash
# Listar storage accounts
az storage account list --query "[].name"

# Ver detalles de una storage account
az storage account show --resource-group 'my-rg' --name 'storage-name'
```

---

## 6. App Service Plans - Borrar

```bash
# Borrar un App Service Plan vacío
az appservice plan delete --resource-group 'my-resource-group' --name 'empty-asp' --yes
```

### Variantes
```bash
# Forma más corta (alias)
az appservice plan delete -g 'my-rg' -n 'plan-name' --yes

# Ver planes disponibles
az appservice plan list --query "[].name"
```

---

## 7. Network Interfaces (NIC) - Borrar

```bash
# Borrar una interfaz de red sin VM asociada
az network nic delete --resource-group 'my-rg' --name 'orphaned-nic' --yes
```

### Variantes
```bash
# Listar NICs
az network nic list --resource-group 'my-rg' --query "[].name"

# Ver detalles de una NIC
az network nic show --resource-group 'my-rg' --name 'nic-name'
```

---

## 8. Key Vaults - Borrar

```bash
# Borrar un Key Vault sin tenant
az keyvault delete --resource-group 'my-rg' --name 'unused-keyvault' --yes
```

### Notas
⚠️ Los Key Vaults borrados pueden recuperarse dentro de 90 días (soft delete).

### Variantes
```bash
# Ver Key Vaults
az keyvault list --query "[].name"

# Purgar permanentemente (después de borrar)
az keyvault purge --name 'keyvault-name'
```

---

## 9. Load Balancers - Borrar

```bash
# Borrar un Load Balancer sin reglas
az network lb delete --resource-group 'my-resource-group' --name 'unused-lb' --yes
```

### Variantes
```bash
# Listar Load Balancers
az network lb list --resource-group 'my-rg' --query "[].name"

# Ver reglas de un LB
az network lb rule list --resource-group 'my-rg' --lb-name 'lb-name'
```

---

## 10. Snapshots - Borrar

```bash
# Borrar un snapshot antiguo (>90 días)
az snapshot delete --resource-group 'my-resource-group' --name 'old-snapshot-2023' --yes
```

### Variantes
```bash
# Listar snapshots
az snapshot list --resource-group 'my-rg' --query "[].name"

# Crear snapshot de un disco (alternativa a borrar)
az snapshot create --resource-group 'my-rg' --name 'new-snapshot' --source '/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Compute/disks/disk-name'
```

---

## Crear Snapshots (Alternativa a Borrar)

En lugar de borrar discos, puedes crear snapshots:

```bash
# Crear snapshot desde un disco
az snapshot create --resource-group 'my-rg' --name 'disk-backup-snapshot' --source 'my-disk'

# Crear snapshot desde otro snapshot
az snapshot create --resource-group 'my-rg' --name 'snapshot-copy' --source '/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Compute/snapshots/source-snapshot'
```

---

## Operaciones Comunes

### Listar recursos en un grupo de recursos
```bash
az resource list --resource-group 'my-rg' --output table
```

### Buscar recursos por nombre
```bash
az resource list --query "[?contains(name, 'zombie')]" --output table
```

### Obtener detalles de un recurso
```bash
az resource show --ids '/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Compute/disks/disk-name'
```

### Contar recursos por tipo
```bash
az resource list --resource-group 'my-rg' --query "length([*])" 
```

### Borrar grupo de recursos completo
```bash
# ⚠️ CUIDADO: Borra TODOS los recursos del grupo
az group delete --name 'my-rg' --yes
```

---

## Confirmaciones y Flags Útiles

| Flag | Significado | Ejemplo |
|------|-----------|---------|
| `--yes` | Confirmar automáticamente | `--yes` |
| `--no-wait` | No esperar a completar | `--no-wait` |
| `--force` | Forzar operación | `--force` |
| `--verbose` | Mostrar detalles | `--verbose` |
| `--debug` | Modo debug | `--debug` |
| `--output` | Formato de salida | `--output json` o `table` |

---

## Seguridad: Antes de Ejecutar

### 1. Verificar conexión
```bash
az account show
```

### 2. Listar lo que se va a borrar
```bash
# Reemplaza 'disk' con el tipo de recurso
az disk list --query "[].{name:name, rg:resourceGroup}" --output table
```

### 3. Hacer backup
```bash
# Para discos - crear snapshot primero
az snapshot create --resource-group 'my-rg' --name 'backup-before-delete' --source 'disk-to-delete'
```

### 4. Ejecutar ONE por ONE
```bash
# NO ejecutes todo el script de una vez
# Ejecuta un comando, verifica, después el siguiente

# Comando 1
az disk delete --resource-group 'rg' --name 'disk1' --yes
# Verificar éxito...

# Comando 2
az disk delete --resource-group 'rg' --name 'disk2' --yes
```

---

## Recuperación de Errores

### Comando falló
```bash
# Ver error más detallado
az <comando> --verbose

# Ver log de auditoría en Azure Portal
# O usar Azure CLI:
az monitor activity-log list --status "Failed"
```

### Recursos no encontrados
```bash
# Verificar nombre exacto
az resource list --resource-group 'my-rg' --query "[].name"
```

### Permisos insuficientes
```bash
# Verificar permisos en el rol actual
az role assignment list --assignee $(az account show --query user.name)
```

---

## Ejemplos de Scripts Completos

### Script: Borrar todos los discos sin adjuntar en un RG

```bash
#!/bin/bash

RG="my-resource-group"

echo "Buscando discos sin adjuntar en $RG..."
az disk list --resource-group $RG --query "[?managedBy == null].name" -o tsv | while read disk; do
    echo "Borrando disco: $disk"
    az disk delete --resource-group $RG --name $disk --yes
done

echo "Listo!"
```

### Script: Borrar snapshots mayores a 90 días

```bash
#!/bin/bash

RG="my-resource-group"
DAYS=90

echo "Buscando snapshots mayores a $DAYS días en $RG..."
az snapshot list --resource-group $RG --query "[].name" -o tsv | while read snapshot; do
    echo "Borrando snapshot: $snapshot"
    az snapshot delete --resource-group $RG --name $snapshot --yes
done

echo "Listo!"
```

---

## Referencias Útiles

- [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/reference-index)
- [az disk reference](https://learn.microsoft.com/en-us/cli/azure/disk)
- [az network reference](https://learn.microsoft.com/en-us/cli/azure/network)
- [az sql reference](https://learn.microsoft.com/en-us/cli/azure/sql)
- [az storage reference](https://learn.microsoft.com/en-us/cli/azure/storage)

---

## Notas Importantes

⚠️ **CRÍTICO**:
- **NUNCA ejecutes comandos sin revisar primero**
- **HAZ BACKUP antes de borrar recursos**
- **PRUEBA con un RG de prueba primero**
- **Ten cuidado con `--yes` flag - confirma automáticamente**
- **Los comandos generados pueden necesitar parámetros adicionales**
- **Eres responsable de lo que ejecutes**

---

**Última actualización**: 2026-02-04
**Proyecto**: Guardian Efímero - FinOps para Azure
