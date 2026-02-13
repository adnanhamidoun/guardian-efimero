#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Limpia recursos demo creados por demo_setup.ps1.

.DESCRIPTION
    Borra todos los recursos Azure con tag demo=zombi en el RG especificado,
    o borra el RG completo si se pasa -DeleteResourceGroup.

.PARAMETER ResourceGroup
    Nombre del Resource Group. Default: "HamidounElHabtiAdnan"

.PARAMETER DeleteResourceGroup
    Si $true, borra el RG completo. Default: $false (solo borra recursos con tag)

.EXAMPLE
    .\scripts\demo_cleanup.ps1
    .\scripts\demo_cleanup.ps1 -ResourceGroup "MyRG"
    .\scripts\demo_cleanup.ps1 -DeleteResourceGroup $true
#>

param(
    [string]$ResourceGroup = "HamidounElHabtiAdnan",
    [bool]$DeleteResourceGroup = $false
)

# Colores
$Success = @{ ForegroundColor = 'Green' }
$Error = @{ ForegroundColor = 'Red' }
$Info = @{ ForegroundColor = 'Cyan' }
$Warning = @{ ForegroundColor = 'Yellow' }
$Question = @{ ForegroundColor = 'Magenta' }

Write-Host "`n=== Guardian Efímero - DEMO CLEANUP ===" @Info
Write-Host "Resource Group: $ResourceGroup" @Info

if ($DeleteResourceGroup) {
    Write-Host "Modo: Borrar RG completo" @Warning
} else {
    Write-Host "Modo: Borrar solo recursos con tag demo=zombi" @Info
}
Write-Host ""

# Verificar autenticación
try {
    $sub = az account show --query "name" -o tsv
    Write-Host "✓ Autenticado en: $sub" @Success
} catch {
    Write-Host "✗ Error: No autenticado. Ejecuta: az login" @Error
    exit 1
}

# Verificar que el RG existe
try {
    $rgExists = az group exists -n $ResourceGroup -o json | ConvertFrom-Json
    if (-not $rgExists) {
        Write-Host "✗ Resource Group no encontrado: $ResourceGroup" @Error
        exit 1
    }
} catch {
    Write-Host "✗ Error verificando RG: $_" @Error
    exit 1
}

if ($DeleteResourceGroup) {
    # Opción 1: Borrar RG completo
    Write-Host "`n⚠️  ADVERTENCIA: Vas a borrar el Resource Group completo: $ResourceGroup" @Warning
    Write-Host "Esto eliminará TODOS los recursos, no solo los de demo." @Warning
    $confirm = Read-Host "¿Estás seguro? (escribe 'yes' para confirmar)"
    
    if ($confirm -eq "yes") {
        try {
            Write-Host "`nBorrando Resource Group $ResourceGroup..." @Warning
            az group delete -n $ResourceGroup --yes --no-wait | Out-Null
            Write-Host "✓ Eliminación iniciada (puede tomar varios minutos)" @Success
        } catch {
            Write-Host "✗ Error borrando RG: $_" @Error
            exit 1
        }
    } else {
        Write-Host "Cancelado." @Info
        exit 0
    }
} else {
    # Opción 2: Borrar solo recursos con tag demo=zombi
    Write-Host "`nBuscando recursos con tag 'demo=zombi'..." @Info
    
    try {
        # Obtener IDs de todos los recursos con el tag en el RG
        $query = "az resource list -g $ResourceGroup --query ""[?tags.demo=='zombi'].id"" -o json"
        $resourceIds = Invoke-Expression $query | ConvertFrom-Json
        
        if ($resourceIds.Count -eq 0) {
            Write-Host "No se encontraron recursos con tag demo=zombi" @Info
            exit 0
        }
        
        Write-Host "Encontrados $($resourceIds.Count) recurso(s)" @Info
        Write-Host ""
        
        # Listar recursos a borrar
        foreach ($id in $resourceIds) {
            $name = $id -split "/" | Select-Object -Last 1
            Write-Host "  • $name" @Warning
        }
        
        Write-Host ""
        $confirm = Read-Host "¿Borrar estos $($resourceIds.Count) recurso(s)? (escribe 'yes' para confirmar)"
        
        if ($confirm -eq "yes") {
            $deleted = 0
            foreach ($id in $resourceIds) {
                try {
                    $name = $id -split "/" | Select-Object -Last 1
                    Write-Host "  Borrando $name..." @Info
                    az resource delete --ids $id --no-wait | Out-Null
                    $deleted++
                } catch {
                    Write-Host "  ✗ Error borrando $name : $_" @Error
                }
            }
            Write-Host "`n✓ Elimados $deleted recurso(s) (proceso en background)" @Success
        } else {
            Write-Host "Cancelado." @Info
            exit 0
        }
    } catch {
        Write-Host "✗ Error: $_" @Error
        exit 1
    }
}

Write-Host "`n=== CLEANUP COMPLETADO ===" @Success
Write-Host "Los recursos se eliminarán en los próximos minutos." @Info
Write-Host "Usa 'az resource list -g $ResourceGroup' para verificar el estado.`n" @Info
