#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Crea recursos demo "zombis" para testear Guardian Efímero.

.DESCRIPTION
    Crea 8 tipos de recursos zombis con tag demo=zombi en el RG especificado.
    Todos pueden ser limpiados con demo_cleanup.ps1.

.PARAMETER ResourceGroup
    Nombre del Resource Group. Default: "HamidounElHabtiAdnan"

.PARAMETER Location
    Ubicación Azure (ej: "eastus", "westeurope"). Default: "eastus"

.EXAMPLE
    .\scripts\demo_setup.ps1
    .\scripts\demo_setup.ps1 -ResourceGroup "MyRG" -Location "westus2"
#>

param(
    [string]$ResourceGroup = "HamidounElHabtiAdnan",
    [string]$Location = "eastus"
)

# Colores para output
$Success = @{ ForegroundColor = 'Green' }
$Error = @{ ForegroundColor = 'Red' }
$Info = @{ ForegroundColor = 'Cyan' }
$Warning = @{ ForegroundColor = 'Yellow' }

Write-Host "`n=== Guardian Efímero - DEMO SETUP ===" @Info
Write-Host "Resource Group: $ResourceGroup" @Info
Write-Host "Location: $Location`n" @Info

# Verificar que estamos autenticados en Azure
try {
    $sub = az account show --query "name" -o tsv
    Write-Host "✓ Autenticado en suscripción: $sub" @Success
} catch {
    Write-Host "✗ Error: No autenticado. Ejecuta: az login" @Error
    exit 1
}

# Crear Resource Group si no existe
Write-Host "`n[1/8] Creando/Verificando Resource Group..." @Info
try {
    $rgExists = az group exists -n $ResourceGroup -o json | ConvertFrom-Json
    if (-not $rgExists) {
        Write-Host "  Creando RG $ResourceGroup..." 
        az group create -n $ResourceGroup -l $Location | Out-Null
        Write-Host "  ✓ Resource Group creado" @Success
    } else {
        Write-Host "  ✓ Resource Group ya existe" @Success
    }
} catch {
    Write-Host "  ✗ Error creando RG: $_" @Error
    exit 1
}

# 1. DISCO SIN ADJUNTAR (unattached managed disk)
Write-Host "`n[2/8] Creando Disco sin adjuntar..." @Info
try {
    $diskName = "zombie-disk-unattached"
    $exists = az disk show -g $ResourceGroup -n $diskName 2>$null
    if (-not $exists) {
        az disk create `
            --resource-group $ResourceGroup `
            --name $diskName `
            --size-gb 32 `
            --sku Standard_LRS `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ✓ Disco creado: $diskName" @Success
    } else {
        Write-Host "  ✓ Disco ya existe: $diskName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 2. IP PÚBLICA HUÉRFANA (orphaned public IP)
Write-Host "`n[3/8] Creando IP Pública huérfana..." @Info
try {
    $ipName = "zombie-orphaned-ip"
    $exists = az network public-ip show -g $ResourceGroup -n $ipName 2>$null
    if (-not $exists) {
        az network public-ip create `
            --resource-group $ResourceGroup `
            --name $ipName `
            --sku Standard `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ✓ IP Pública creada: $ipName" @Success
    } else {
        Write-Host "  ✓ IP Pública ya existe: $ipName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 3. NETWORK INTERFACE SIN VM (orphaned NIC)
Write-Host "`n[4/8] Creando Network Interface sin VM..." @Info
try {
    $nicName = "zombie-orphaned-nic"
    $vnetName = "zombie-vnet"
    $subnetName = "zombie-subnet"
    
    # Crear VNET y subnet si no existen
    $vnetExists = az network vnet show -g $ResourceGroup -n $vnetName 2>$null
    if (-not $vnetExists) {
        az network vnet create `
            --resource-group $ResourceGroup `
            --name $vnetName `
            --address-prefix 10.0.0.0/16 `
            --subnet-name $subnetName `
            --subnet-prefix 10.0.0.0/24 | Out-Null
    }
    
    # Crear NIC
    $nicExists = az network nic show -g $ResourceGroup -n $nicName 2>$null
    if (-not $nicExists) {
        az network nic create `
            --resource-group $ResourceGroup `
            --name $nicName `
            --vnet-name $vnetName `
            --subnet $subnetName `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ✓ NIC creado: $nicName" @Success
    } else {
        Write-Host "  ✓ NIC ya existe: $nicName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 4. VM NO EJECUTÁNDOSE (deallocated VM)
Write-Host "`n[5/8] Creando VM en estado deallocated..." @Info
try {
    $vmName = "zombie-deallocated-vm"
    $nicName = "zombie-vm-nic"
    $vnetName = "zombie-vnet"
    $subnetName = "zombie-subnet"
    $imageUrn = "UbuntuLTS"
    
    # Crear NIC para la VM si no existe
    $nicExists = az network nic show -g $ResourceGroup -n $nicName 2>$null
    if (-not $nicExists) {
        az network nic create `
            --resource-group $ResourceGroup `
            --name $nicName `
            --vnet-name $vnetName `
            --subnet $subnetName | Out-Null
    }
    
    # Crear VM
    $vmExists = az vm show -g $ResourceGroup -n $vmName 2>$null
    if (-not $vmExists) {
        az vm create `
            --resource-group $ResourceGroup `
            --name $vmName `
            --nics $nicName `
            --image $imageUrn `
            --admin-username azureuser `
            --generate-ssh-keys `
            --tags "demo=zombi" `
            --no-wait | Out-Null
        Write-Host "  ℹ VM creada (puede tomar 1-2 min): $vmName" @Info
        
        # Esperar a que esté lista
        Write-Host "  Esperando a que VM esté lista..." @Warning
        Start-Sleep -Seconds 30
        
        # Deallocar la VM
        Write-Host "  Deallocando VM..." @Info
        az vm deallocate -g $ResourceGroup -n $vmName --no-wait | Out-Null
        Write-Host "  ✓ VM deallocated: $vmName" @Success
    } else {
        Write-Host "  ✓ VM ya existe: $vmName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 5. LOAD BALANCER SIN REGLAS (empty load balancer)
Write-Host "`n[6/8] Creando Load Balancer vacío..." @Info
try {
    $lbName = "zombie-empty-lb"
    $pubipName = "zombie-lb-ip"
    
    # Crear IP Pública para el LB si no existe
    $pubipExists = az network public-ip show -g $ResourceGroup -n $pubipName 2>$null
    if (-not $pubipExists) {
        az network public-ip create `
            --resource-group $ResourceGroup `
            --name $pubipName `
            --sku Standard | Out-Null
    }
    
    # Crear LB
    $lbExists = az network lb show -g $ResourceGroup -n $lbName 2>$null
    if (-not $lbExists) {
        az network lb create `
            --resource-group $ResourceGroup `
            --name $lbName `
            --sku Standard `
            --public-ip-address $pubipName `
            --frontend-ip-name "frontend" `
            --backend-pool-name "backend" `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ✓ Load Balancer creado (sin reglas): $lbName" @Success
    } else {
        Write-Host "  ✓ Load Balancer ya existe: $lbName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 6. APP SERVICE PLAN VACÍO (empty plan)
Write-Host "`n[7/8] Creando App Service Plan vacío..." @Info
try {
    $planName = "zombie-empty-plan"
    
    $planExists = az appservice plan show -g $ResourceGroup -n $planName 2>$null
    if (-not $planExists) {
        az appservice plan create `
            --resource-group $ResourceGroup `
            --name $planName `
            --sku B1 `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ✓ App Service Plan creado (vacío): $planName" @Success
    } else {
        Write-Host "  ✓ App Service Plan ya existe: $planName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 7. SNAPSHOT ANTIGUO (old snapshot)
Write-Host "`n[8/8] Creando Snapshot antiguo (>90 días)..." @Info
try {
    $snapshotName = "zombie-old-snapshot"
    $sourceDiskName = "zombie-snapshot-source"
    
    # Crear disco fuente si no existe
    $sourceDiskExists = az disk show -g $ResourceGroup -n $sourceDiskName 2>$null
    if (-not $sourceDiskExists) {
        az disk create `
            --resource-group $ResourceGroup `
            --name $sourceDiskName `
            --size-gb 16 `
            --sku Standard_LRS | Out-Null
    }
    
    # Crear snapshot
    $snapshotExists = az snapshot show -g $ResourceGroup -n $snapshotName 2>$null
    if (-not $snapshotExists) {
        az snapshot create `
            --resource-group $ResourceGroup `
            --name $snapshotName `
            --source $sourceDiskName `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ℹ Snapshot creado: $snapshotName" @Info
        Write-Host "  ⚠ NOTA: Para que sea detectable como 'antiguo' (>90 días)," @Warning
        Write-Host "    necesita esperar 91 días o usar un umbral bajo en la UI." @Warning
        Write-Host "    En demo_mode puedes usar snapshot_age_days=0 para probarlo." @Warning
    } else {
        Write-Host "  ✓ Snapshot ya existe: $snapshotName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

# 8. NETWORK SECURITY GROUP SIN ASOCIAR (unassociated NSG)
Write-Host "`n[9/8] Creando NSG sin asociar..." @Info
try {
    $nsgName = "zombie-unassociated-nsg"
    
    $nsgExists = az network nsg show -g $ResourceGroup -n $nsgName 2>$null
    if (-not $nsgExists) {
        az network nsg create `
            --resource-group $ResourceGroup `
            --name $nsgName `
            --tags "demo=zombi" | Out-Null
        Write-Host "  ✓ NSG sin asociar creado: $nsgName" @Success
    } else {
        Write-Host "  ✓ NSG ya existe: $nsgName" @Success
    }
} catch {
    Write-Host "  ✗ Error: $_" @Error
}

Write-Host "`n=== SETUP COMPLETADO ===" @Success
Write-Host "`nProximos pasos:" @Info
Write-Host "1. Ejecuta: streamlit run app.py" @Info
Write-Host "2. En la UI:" @Info
Write-Host "   - Sidebar: Activa 'DEMO MODE'" @Info
Write-Host "   - Sidebar: Baja 'snapshot_age_days' a 0" @Info
Write-Host "   - Sección 'Scan': Corre el escaneo" @Info
Write-Host "3. Esperado: 8 tipos de zombis detectados" @Info
Write-Host "`nPara limpiar recursos:" @Info
Write-Host "   .\scripts\demo_cleanup.ps1`n" @Info
