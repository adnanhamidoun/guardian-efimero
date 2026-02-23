#!/usr/bin/env pwsh
# Demo setup script for Azure "zombies" resources
# Normalized file encoding and line endings to avoid PowerShell parse issues

<#
.SYNOPSIS
    Crea recursos demo "zombis" para testear Guardian Efímero.

.DESCRIPTION
    Crea 7 tipos de recursos zombis con tag demo=zombi en el RG especificado.
    Todos pueden ser limpiados con demo_cleanup.ps1.

.PARAMETER ResourceGroup
    #!/usr/bin/env pwsh
    # Demo setup script for Azure "zombies" resources (ASCII-safe)

    <#
    .SYNOPSIS
        Crea recursos demo "zombis" para testear Guardian Efímero.

    .DESCRIPTION
        Crea 7 tipos de recursos zombis con tag demo=zombi en el RG especificado.
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
        [string]$ResourceGroup = "prueba-guardian-efimero",
        [string]$Location = "swedencentral"
    )

    # Colores para output (avoid clobbering PS automatic variables)
    $SuccessStyle = @{ ForegroundColor = 'Green' }
    $ErrStyle     = @{ ForegroundColor = 'Red' }
    $InfoStyle    = @{ ForegroundColor = 'Cyan' }
    $WarnStyle    = @{ ForegroundColor = 'Yellow' }

    Write-Host "`n=== Guardian Efimero - DEMO SETUP ===" @InfoStyle
    Write-Host "Resource Group: $ResourceGroup" @InfoStyle
    Write-Host "Location: $Location`n" @InfoStyle

    # Verificar que estamos autenticados en Azure
    try {
        $sub = az account show --query "name" -o tsv
        Write-Host "[OK] Autenticado en suscripcion: $sub" @SuccessStyle
    } catch {
        Write-Host "[ERR] Error: No autenticado. Ejecuta: az login" @ErrStyle
        exit 1
    }

    # Crear Resource Group si no existe
    Write-Host "`n[1/7] Creando/Verificando Resource Group..." @InfoStyle
    try {
        $rgExists = az group exists -n $ResourceGroup -o json | ConvertFrom-Json
        if (-not $rgExists) {
            Write-Host "  Creando RG $ResourceGroup..."
            az group create -n $ResourceGroup -l $Location | Out-Null
            Write-Host "  [OK] Resource Group creado" @SuccessStyle
        } else {
            Write-Host "  [OK] Resource Group ya existe" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error creando RG: $_" @ErrStyle
        exit 1
    }

    # 1. DISCO SIN ADJUNTAR (unattached managed disk)
    Write-Host "`n[2/7] Creando Disco sin adjuntar..." @InfoStyle
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
            Write-Host "  [OK] Disco creado: $diskName" @SuccessStyle
        } else {
            Write-Host "  [OK] Disco ya existe: $diskName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }

    # 2. IP PUBLICA HUERFANA (orphaned public IP)
    Write-Host "`n[3/7] Creando IP Publica huerfana..." @InfoStyle
    try {
        $ipName = "zombie-orphaned-ip"
        $exists = az network public-ip show -g $ResourceGroup -n $ipName 2>$null
        if (-not $exists) {
            az network public-ip create `
                --resource-group $ResourceGroup `
                --name $ipName `
                --sku Standard `
                --tags "demo=zombi" | Out-Null
            Write-Host "  [OK] IP Publica creada: $ipName" @SuccessStyle
        } else {
            Write-Host "  [OK] IP Publica ya existe: $ipName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }

    # 3. NETWORK INTERFACE SIN VM (orphaned NIC)
    Write-Host "`n[4/7] Creando Network Interface sin VM..." @InfoStyle
    try {
        $nicName = "zombie-orphaned-nic"
        $vnetName = "zombie-vnet"
        $subnetName = "zombie-subnet"
        $vnetLocation = "uksouth"

        # Crear VNet y subnet solo si no existen (en UK South)
        $vnetExists = az network vnet show -g $ResourceGroup -n $vnetName 2>$null
        if (-not $vnetExists) {
            az network vnet create `
                --resource-group $ResourceGroup `
                --name $vnetName `
                --address-prefix 10.0.0.0/16 `
                --subnet-name $subnetName `
                --subnet-prefix 10.0.0.0/24 `
                --location $vnetLocation | Out-Null
        }

        # Crear NIC
        $nicExists = az network nic show -g $ResourceGroup -n $nicName 2>$null
        if (-not $nicExists) {
            az network nic create `
                --resource-group $ResourceGroup `
                --name $nicName `
                --vnet-name $vnetName `
                --subnet $subnetName `
                --location $vnetLocation `
                --tags "demo=zombi" | Out-Null
            Write-Host "  [OK] NIC creado: $nicName" @SuccessStyle
        } else {
            Write-Host "  [OK] NIC ya existe: $nicName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }

    # 4. VM NO EJECUTANDOSE (deallocated VM)
    Write-Host "`n[5/7] Creando VM en estado deallocated... (Sweden Central)" @InfoStyle
    try {
        $vmName = "zombie-deallocated-vm"
        $imageUrn = "Ubuntu2204"
        $vmLocation = "swedencentral"
        $vmSize = "Standard_B1s"

        # Crear VM
        $vmExists = az vm show -g $ResourceGroup -n $vmName 2>$null
        if (-not $vmExists) {
            az vm create `
                --resource-group $ResourceGroup `
                --name $vmName `
                --image $imageUrn `
                --size $vmSize `
                --location $vmLocation `
                --admin-username azureuser `
                --generate-ssh-keys `
                --tags demo=zombi | Out-Null
            Write-Host "  [INFO] VM creada (puede tomar 1-2 min): $vmName" @InfoStyle

            # Esperar a que VM esté lista
            Write-Host "  Esperando a que VM esté lista..." @WarnStyle
            Start-Sleep -Seconds 30

            # Deallocar la VM
            Write-Host "  Deallocando VM..." @InfoStyle
            az vm deallocate --resource-group $ResourceGroup --name $vmName | Out-Null
            Write-Host "  [OK] VM deallocated: $vmName" @SuccessStyle
        } else {
            Write-Host "  [OK] VM ya existe: $vmName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }

    # 5. LOAD BALANCER SIN REGLAS (empty load balancer)
    Write-Host "`n[6/7] Creando Load Balancer vacio..." @InfoStyle
    try {
        $lbName = "zombie-empty-lb"
        $pubipName = "zombie-lb-ip"

        # Crear IP Publica para el LB si no existe
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
            Write-Host "  [OK] Load Balancer creado (sin reglas): $lbName" @SuccessStyle
        } else {
            Write-Host "  [OK] Load Balancer ya existe: $lbName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }

    # 6. APP SERVICE PLAN VACIO (empty plan)
    Write-Host "`n[7/7] Creando App Service Plan vacio..." @InfoStyle
    try {
        $planName = "zombie-empty-plan"

        $planExists = az appservice plan show -g $ResourceGroup -n $planName 2>$null
        if (-not $planExists) {
            az appservice plan create `
                --resource-group $ResourceGroup `
                --name $planName `
                --sku B1 `
                --tags "demo=zombi" | Out-Null
            Write-Host "  [OK] App Service Plan creado (vacio): $planName" @SuccessStyle
        } else {
            Write-Host "  [OK] App Service Plan ya existe: $planName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }



    # 7. NETWORK SECURITY GROUP SIN ASOCIAR (unassociated NSG)
    Write-Host "`n[8/7] Creando NSG sin asociar..." @InfoStyle
    try {
        $nsgName = "zombie-unassociated-nsg"

        $nsgExists = az network nsg show -g $ResourceGroup -n $nsgName 2>$null
        if (-not $nsgExists) {
            az network nsg create `
                --resource-group $ResourceGroup `
                --name $nsgName `
                --tags "demo=zombi" | Out-Null
            Write-Host "  [OK] NSG sin asociar creado: $nsgName" @SuccessStyle
        } else {
            Write-Host "  [OK] NSG ya existe: $nsgName" @SuccessStyle
        }
    } catch {
        Write-Host "  [ERR] Error: $_" @ErrStyle
    }

    Write-Host "`n=== SETUP COMPLETADO ===" @SuccessStyle
    Write-Host "`nProximos pasos:" @InfoStyle
    Write-Host "1. Ejecuta: streamlit run app.py" @InfoStyle
    Write-Host "2. En la UI: Ejecuta el escaneo desde la sección principal" @InfoStyle
    Write-Host "3. Esperado: 7 tipos de zombis detectados" @InfoStyle
    Write-Host "`nPara limpiar recursos:" @InfoStyle
    Write-Host "   .\scripts\demo_cleanup.ps1`n" @InfoStyle
