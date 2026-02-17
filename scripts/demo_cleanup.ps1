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
    [ValidateSet('interactive','manual','auto')][string]$Mode = 'interactive',
    [bool]$DeleteResourceGroup = $false,
    [switch]$Approve,
    [switch]$DryRun,
    [string]$OutputFile = ""
)

# Colores (no sobrescribir variables automáticas)
$SuccessStyle = @{ ForegroundColor = 'Green' }
$ErrStyle     = @{ ForegroundColor = 'Red' }
$InfoStyle    = @{ ForegroundColor = 'Cyan' }
$WarnStyle    = @{ ForegroundColor = 'Yellow' }
$QuestionStyle= @{ ForegroundColor = 'Magenta' }

Write-Host "`n=== Guardian Efimero - DEMO CLEANUP ===" @InfoStyle
Write-Host "Resource Group: $ResourceGroup" @InfoStyle
Write-Host "Modo: $Mode" @InfoStyle
if ($DeleteResourceGroup) {
    Write-Host "Modo de borrado: Borrar RG completo" @WarnStyle
} else {
    Write-Host "Modo de borrado: Borrar solo recursos con tag demo=zombi" @InfoStyle
}
if ($DryRun) { Write-Host "DRY RUN: No se ejecutarán comandos de borrado." @WarnStyle }
if ($Approve) { Write-Host "Aprobación automática activada (-Approve)." @WarnStyle }
Write-Host ""

# Verificar autenticación
try {
    $sub = az account show --query "name" -o tsv
    Write-Host "[OK] Autenticado en: $sub" @SuccessStyle
} catch {
    Write-Host "[ERR] Error: No autenticado. Ejecuta: az login" @ErrStyle
    exit 1
}

# Verificar que el RG existe
try {
    $rgExists = az group exists -n $ResourceGroup -o json | ConvertFrom-Json
    if (-not $rgExists) {
        Write-Host "[ERR] Resource Group no encontrado: $ResourceGroup" @ErrStyle
        exit 1
    }
} catch {
    Write-Host "[ERR] Error verificando RG: $_" @ErrStyle
    exit 1
}

if ($DeleteResourceGroup) {
    # Delete resource group flow
    $rgCmd = "az group delete -n $ResourceGroup --yes --no-wait"
    if ($Mode -eq 'manual') {
        Write-Host "`n[MODO MANUAL] Comando para borrar RG:" @InfoStyle
        Write-Host $rgCmd @WarnStyle
        if ($OutputFile) { Set-Content -Path $OutputFile -Value $rgCmd -Encoding UTF8; Write-Host "Comando guardado en $OutputFile" @InfoStyle }
        Write-Host "Ejecuta el comando manualmente cuando quieras." @InfoStyle
        exit 0
    }

    if ($Mode -eq 'interactive' -or $Mode -eq 'auto') {
        Write-Host "`n[WARN] ADVERTENCIA: Vas a borrar el Resource Group completo: $ResourceGroup" @WarnStyle
        Write-Host "Esto eliminará TODOS los recursos, no solo los de demo." @WarnStyle

        if (-not $Approve) {
            $confirm = Read-Host "¿Estás seguro? (escribe 'yes' para confirmar)"
            if ($confirm -ne 'yes') { Write-Host 'Cancelado.' @InfoStyle; exit 0 }
        } else {
            Write-Host "Aprobación automática detectada (-Approve). Procediendo..." @WarnStyle
        }

        if ($DryRun) { Write-Host "DRY RUN: $rgCmd" @WarnStyle; exit 0 }

        try {
            Write-Host "Borrando Resource Group $ResourceGroup..." @WarnStyle
            Invoke-Expression $rgCmd
            Write-Host "[OK] Eliminación iniciada (puede tomar varios minutos)" @SuccessStyle
        } catch {
            Write-Host "[ERR] Error borrando RG: $_" @ErrStyle
            exit 1
        }
    }
} else {
    # Delete resources with tag demo=zombi
    Write-Host "`nBuscando recursos con tag 'demo=zombi'..." @InfoStyle
    try {
        $resourceIds = az resource list -g $ResourceGroup --query "[?tags.demo=='zombi'].id" -o json | ConvertFrom-Json

        if (-not $resourceIds -or $resourceIds.Count -eq 0) {
            Write-Host "No se encontraron recursos con tag demo=zombi" @InfoStyle
            exit 0
        }

        Write-Host "Encontrados $($resourceIds.Count) recurso(s)" @InfoStyle
        Write-Host ""

        # Prepare delete commands
        $commands = @()
        foreach ($id in $resourceIds) {
            $commands += "az resource delete --ids $id --no-wait"
        }

        if ($Mode -eq 'manual') {
            Write-Host "`n[MODO MANUAL] Generando comandos para borrar (no ejecutados):" @InfoStyle
            foreach ($c in $commands) { Write-Host $c }
            if ($OutputFile) {
                Set-Content -Path $OutputFile -Value ($commands -join "`n") -Encoding UTF8
                Write-Host "Comandos guardados en: $OutputFile" @InfoStyle
            } else {
                Write-Host "Puedes copiar los comandos anteriores y ejecutarlos manualmente." @InfoStyle
            }
            exit 0
        }

        # interactive or auto
        foreach ($id in $resourceIds) {
            $name = ($id -split "/")[-1]
            Write-Host "  • $name" @WarnStyle
        }

        if ($Mode -eq 'interactive' -and -not $Approve) {
            $confirm = Read-Host "¿Borrar estos $($resourceIds.Count) recurso(s)? (escribe 'yes' para confirmar)"
            if ($confirm -ne 'yes') { Write-Host 'Cancelado.' @InfoStyle; exit 0 }
        }

        if ($DryRun) {
            Write-Host "DRY RUN: los siguientes comandos se habrían ejecutado:" @WarnStyle
            foreach ($c in $commands) { Write-Host $c }
            exit 0
        }

        # Execute deletions
        $deleted = 0
        foreach ($id in $resourceIds) {
            try {
                $name = ($id -split "/")[-1]
                Write-Host "  Borrando $name..." @InfoStyle
                if ($Mode -eq 'auto' -and -not $Approve) {
                    # require explicit approval for auto mode unless -Approve passed
                    $ok = Read-Host "Confirmar borrado de $name? (yes/no)"
                    if ($ok -ne 'yes') { Write-Host "  Omitido: $name" @InfoStyle; continue }
                }
                az resource delete --ids $id --no-wait | Out-Null
                $deleted++
            } catch {
                Write-Host "  [ERR] Error borrando $name : $_" @ErrStyle
            }
        }
        Write-Host "`n[OK] Elimidados $deleted recurso(s) (proceso en background)" @SuccessStyle

    } catch {
        Write-Host "[ERR] Error: $_" @ErrStyle
        exit 1
    }
}

Write-Host "`n=== CLEANUP COMPLETADO ===" @Success
Write-Host "Los recursos se eliminarán en los próximos minutos." @Info
Write-Host "Usa 'az resource list -g $ResourceGroup' para verificar el estado.`n" @Info
