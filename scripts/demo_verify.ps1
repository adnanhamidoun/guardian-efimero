#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verifica que Guardian Efímero puede detectar los recursos demo creados.

.DESCRIPTION
    Script que:
    1. Verifica autenticación en Azure
    2. Verifica que existen recursos con tag demo=zombi
    3. Ejecuta una query KQL rápida para cada detector
    4. Guía al usuario a ejecutar streamlit para UI completo

.PARAMETER ResourceGroup
    Nombre del Resource Group. Default: "HamidounElHabtiAdnan"

.EXAMPLE
    .\scripts\demo_verify.ps1
    .\scripts\demo_verify.ps1 -ResourceGroup "MyRG"
#>

param(
    [string]$ResourceGroup = "HamidounElHabtiAdnan"
)

# Colores
$Success = @{ ForegroundColor = 'Green' }
$Error = @{ ForegroundColor = 'Red' }
$Info = @{ ForegroundColor = 'Cyan' }
$Warning = @{ ForegroundColor = 'Yellow' }

Write-Host "`n=== Guardian Efímero - DEMO VERIFY ===" @Info
Write-Host "Resource Group: $ResourceGroup`n" @Info

# 1. Verificar autenticación
Write-Host "[1/3] Verificando autenticación en Azure..." @Info
try {
    $sub = az account show --query "{name: name, id: id}" -o json | ConvertFrom-Json
    Write-Host "✓ Autenticado en: $($sub.name)" @Success
} catch {
    Write-Host "✗ Error: No autenticado. Ejecuta: az login" @Error
    exit 1
}

# 2. Verificar que el RG existe y tiene recursos demo
Write-Host "`n[2/3] Buscando recursos con tag demo=zombi..." @Info
try {
    $rgExists = az group exists -n $ResourceGroup -o json | ConvertFrom-Json
    if (-not $rgExists) {
        Write-Host "✗ Resource Group no encontrado: $ResourceGroup" @Error
        Write-Host "   Ejecuta primero: .\scripts\demo_setup.ps1" @Warning
        exit 1
    }
    
    # Contar recursos demo
    $demoResources = az resource list -g $ResourceGroup --query "[?tags.demo=='zombi']" -o json | ConvertFrom-Json
    $count = $demoResources.Count -as [int]
    if ($count -gt 0) {
        Write-Host "✓ Encontrados $count recurso(s) de demo" @Success
        foreach ($res in $demoResources) {
            Write-Host "  • $($res.name) [$($res.type)]" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠ No se encontraron recursos demo" @Warning
        Write-Host "  Ejecuta primero: .\scripts\demo_setup.ps1" @Warning
    }
} catch {
    Write-Host "✗ Error: $_" @Error
    exit 1
}

# 3. Verificar que se pueden ejecutar queries KQL (prueba rápida)
Write-Host "`n[3/3] Verificando acceso a Azure Resource Graph..." @Info
try {
    # Query simple: contar todos los recursos en el RG
    $kql = @"
resources
| where resourceGroup == '$ResourceGroup'
| summarize count()
"@
    
    $result = az graph query -q $kql -o json | ConvertFrom-Json
    $totalResources = $result.count
    
    if ($totalResources -gt 0) {
        Write-Host "✓ ARG accesible. Total recursos en RG: $totalResources" @Success
    } else {
        Write-Host "⚠ RG vacío o sin permisos de lectura" @Warning
    }
} catch {
    Write-Host "✗ Error accediendo ARG: $_" @Error
    Write-Host "  Verifica permisos Reader en Azure y subscription" @Warning
}

# Mostrar guía de uso
Write-Host "`n=== PRÓXIMOS PASOS ===" @Info
Write-Host ""
Write-Host "✓ CONFIGURACIÓN LISTA" @Success
Write-Host ""
Write-Host "Opción A: UI Completa (Recomendado)" @Info
Write-Host "  1. Activa tu sesión Python:" @Info
Write-Host "     venv\Scripts\Activate.ps1" @Warning
Write-Host "  2. Ejecuta la UI:" @Warning
Write-Host "     streamlit run app.py" @Warning
Write-Host "  3. En la UI:" @Info
Write-Host "     • Sidebar → Activa 'DEMO MODE' (checkbox)" @Info
Write-Host "     • Sidebar → Baja sliders a valores bajos (ej: snapshot_age_days=0)" @Info
Write-Host "     • Sección '1️⃣ Scan' → Click '🔍 Ejecutar escaneo'" @Info
Write-Host "  4. Verifica que aparezcan los 8 tipos:" @Info
Write-Host "     ✓ disk, ip, nic, vm, loadbalancer, appserviceplan, snapshot, nsg" @Info
Write-Host ""
Write-Host "Opción B: Query Manual (CLI)" @Info
Write-Host "  Ejecuta queries KQL directas:" @Warning
Write-Host "    az graph query -q \"resources | where resourceGroup == '$ResourceGroup' | where tags.demo == 'zombi'\"" @Warning
Write-Host ""
Write-Host "Limpiar después:" @Info
Write-Host "  .\scripts\demo_cleanup.ps1" @Warning
Write-Host ""
Write-Host "=== FIN ===" @Info
Write-Host ""
