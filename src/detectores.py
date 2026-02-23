"""Detectores Fase 3 — 8 tipos de zombis Azure (v1 testeable).

8 detectores testeables en v1:
  1. disk — Discos sin adjuntar (unattached)
  2. ip — IPs públicas huérfanas (orphaned)
  3. nic — Network Interfaces sin VM
  4. vm — VMs deallocated/stopped
  5. loadbalancer — Load Balancers sin reglas
  6. appserviceplan — App Service Plans vacíos
  7. snapshot — Snapshots antiguos (parametrizable)
  8. nsg — NSGs sin asociar

Exporta `full_scan(snapshot_age_days=90)` que ejecuta los 8 detectores y devuelve lista concatenada.
"""
from typing import List, Dict, Any

from .tools.arg_detector import ARGDetector

# Heurísticas de ahorro por tipo (valores por defecto para fallback)
HEUR_PRICES = {
    "disk_per_gb": 0.08,  # €/mes/GB
    "ip": 3.0,            # €/mes por IP pública
    "vm_stopped": 60.0,
    "appserviceplan": 5.0,
    "nic": 1.0,
    "lb": 2.0,
    "snapshot_per_gb_per_month": 0.08,  # €/GB/mes
    "nsg": 0.5,           # €/mes por NSG
}


def _normalize_base(row: Dict[str, Any], tipo: str, reason: str = "") -> Dict[str, Any]:
    """Normaliza un resultado ARG a estructura estándar."""
    return {
        "tipo": tipo,
        "id": row.get("id") or row.get("resourceId") or None,
        "nombre": row.get("name") or row.get("nombre") or None,
        "resourceGroup": row.get("resourceGroup", "").replace("hamidounelhabtiadnan", "HamidounElHabtiAdnan"),
        "subscriptionId": row.get("subscriptionId"),
        "location": row.get("location", ""),
        "confianza": 8.0,
        "reason": reason,
    }


def _build_delete_command(recurso: Dict[str, Any]) -> str:
    """Construye comando az delete para un tipo de recurso."""
    tipo = recurso.get("tipo", "").lower()
    rg = recurso.get("resourceGroup", "")
    nombre = recurso.get("nombre", "")
    
    if not rg or not nombre:
        return f"# Falta información: {nombre}"
    
    if tipo == "disk":
        return f"az disk delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "ip":
        return f"az network public-ip delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "nic":
        return f"az network nic delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "vm":
        return f"az vm delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "loadbalancer":
        return f"az network lb delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "appserviceplan":
        return f"az appservice plan delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "snapshot":
        return f"az snapshot delete --resource-group '{rg}' --name '{nombre}' --yes"
    elif tipo == "nsg":
        return f"az network nsg delete --resource-group '{rg}' --name '{nombre}' --yes"
    else:
        return f"az resource delete --ids {recurso.get('id', 'UNKNOWN')} --yes"


def detect_disks_unattached(detector: ARGDetector) -> List[Dict[str, Any]]:
    """Discos managed sin adjuntar a VM."""
    q = r"""
resources
| where type == 'microsoft.compute/disks'
| extend diskState = tostring(properties.diskState)
| where tolower(diskState) == 'unattached' or isempty(tostring(managedBy)) or tostring(managedBy) == ''
| project id, name, resourceGroup, subscriptionId, location, diskSizeGB = properties.diskSizeGB
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        size = int(r.get("diskSizeGB") or 0)
        ahorro = round(size * HEUR_PRICES["disk_per_gb"], 2)
        base = _normalize_base(r, "disk", reason=f"Disco sin adjuntar ({size}GB)")
        base.update({
            "size_gb": size,
            "estimatedMonthlySavings": f"{ahorro}€",
            "azDeleteCommand": _build_delete_command(base),
        })
        out.append(base)
    return out


def detect_ips_orphaned(detector: ARGDetector) -> List[Dict[str, Any]]:
    """IPs públicas sin asociación."""
    q = r"""
resources
| where type == 'microsoft.network/publicipaddresses'
| where isnull(properties.ipConfiguration) or tostring(properties.ipConfiguration) == ''
| project id, name, resourceGroup, subscriptionId, location, ipAddress = tostring(properties.ipAddress)
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        ahorro = round(HEUR_PRICES["ip"], 2)
        base = _normalize_base(r, "ip", reason="IP pública sin asociar")
        base.update({
            "ipAddress": r.get("ipAddress"),
            "estimatedMonthlySavings": f"{ahorro}€",
            "azDeleteCommand": _build_delete_command(base),
        })
        out.append(base)
    return out


def detect_nics_without_vm(detector: ARGDetector) -> List[Dict[str, Any]]:
    """Network Interfaces sin VM asociada."""
    q = r"""
resources
| where type == 'microsoft.network/networkinterfaces'
| where isnull(properties.virtualMachine) or tostring(properties.virtualMachine) == ''
| project id, name, resourceGroup, subscriptionId, location
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        ahorro = round(HEUR_PRICES["nic"], 2)
        base = _normalize_base(r, "nic", reason="NIC sin VM asociada")
        base.update({
            "estimatedMonthlySavings": f"{ahorro}€",
            "azDeleteCommand": _build_delete_command(base),
        })
        out.append(base)
    return out


def detect_vms_not_running(detector: ARGDetector) -> List[Dict[str, Any]]:
    """VMs deallocated o stopped.

    Note: Azure Resource Graph does not reliably expose instance view powerState via a simple
    properties.statuses[] expression. To avoid ParserFailure we first list VMs via ARG and
    then, when possible, query the instance view via `az vm get-instance-view` for each VM
    to determine the runtime power state. If `az` is not available or the call fails, the
    VM will be skipped to avoid raising an exception in the UI.
    """
    import subprocess
    import json
    import shutil

    # First, list all VMs with ARG (no power state filter)
    q = r"""
resources
| where type == 'microsoft.compute/virtualmachines'
| project id, name, resourceGroup, subscriptionId, location
"""
    rows = detector._run_query(q)
    out = []

    az_exe = shutil.which('az') or shutil.which('az.cmd')

    for r in rows:
        name = r.get('name')
        rg = r.get('resourceGroup')
        power_state = None

        # Try to get power state via az CLI if available
        if az_exe and name and rg:
            try:
                proc = subprocess.run([
                    az_exe, 'vm', 'get-instance-view',
                    '--name', name,
                    '--resource-group', rg,
                    '-o', 'json'
                ], capture_output=True, text=True, check=True)
                inst = json.loads(proc.stdout or '{}')
                statuses = inst.get('instanceView', {}).get('statuses', [])
                # Find a status that indicates PowerState
                for s in statuses:
                    code = s.get('code', '') or ''
                    display = s.get('displayStatus', '') or ''
                    if code.lower().startswith('powerstate') or 'powerstate' in code.lower():
                        power_state = display
                        break
                # fallback: look for displayStatus containing 'deallocated' or 'stopped'
                if not power_state:
                    for s in statuses:
                        display = s.get('displayStatus', '') or ''
                        if 'deallocated' in display.lower() or 'stopped' in display.lower():
                            power_state = display
                            break
            except Exception:
                power_state = None

        # If we determined the VM is not running, include it
        if power_state and (('deallocated' in power_state.lower()) or ('stopped' in power_state.lower())):
            ahorro = round(HEUR_PRICES["vm_stopped"], 2)
            base = _normalize_base(r, "vm", reason=f"VM {power_state}")
            base.update({
                "estimatedMonthlySavings": f"{ahorro}€",
                "azDeleteCommand": _build_delete_command(base),
            })
            out.append(base)

    return out


def detect_loadbalancers_without_rules(detector: ARGDetector) -> List[Dict[str, Any]]:
    """Load Balancers sin reglas."""
    q = r"""
resources
| where type == 'microsoft.network/loadbalancers'
| extend ruleCount = array_length(properties.loadBalancingRules)
| where ruleCount == 0 or isempty(ruleCount)
| project id, name, resourceGroup, subscriptionId, location, ruleCount
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        ahorro = round(HEUR_PRICES["lb"], 2)
        base = _normalize_base(r, "loadbalancer", reason="Load Balancer sin reglas")
        base.update({
            "ruleCount": r.get("ruleCount", 0),
            "estimatedMonthlySavings": f"{ahorro}€",
            "azDeleteCommand": _build_delete_command(base),
        })
        out.append(base)
    return out


def detect_appserviceplans_empty(detector: ARGDetector) -> List[Dict[str, Any]]:
    """App Service Plans sin apps."""
    q = r"""
resources
| where type == 'microsoft.web/serverfarms'
| extend numberOfSites = toint(properties.numberOfSites)
| where numberOfSites == 0 or isempty(numberOfSites)
| project id, name, resourceGroup, subscriptionId, location, numberOfSites
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        ahorro = round(HEUR_PRICES["appserviceplan"], 2)
        base = _normalize_base(r, "appserviceplan", reason="Plan sin apps asociadas")
        base.update({
            "numberOfSites": r.get("numberOfSites", 0),
            "estimatedMonthlySavings": f"{ahorro}€",
            "azDeleteCommand": _build_delete_command(base),
        })
        out.append(base)
    return out




def detect_nsgs_unassociated(detector: ARGDetector) -> List[Dict[str, Any]]:
    """NSGs sin asociaciones a NICs o subnets."""
    q = r"""
resources
| where type == 'microsoft.network/networksecuritygroups'
| extend networkInterfaceIds = array_length(properties.networkInterfaces)
| extend subnetIds = array_length(properties.subnets)
| where (networkInterfaceIds == 0 or isempty(networkInterfaceIds)) and (subnetIds == 0 or isempty(subnetIds))
| project id, name, resourceGroup, subscriptionId, location, networkInterfaceIds, subnetIds
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        ahorro = round(HEUR_PRICES["nsg"], 2)
        base = _normalize_base(r, "nsg", reason="NSG sin asociaciones")
        base.update({
            "estimatedMonthlySavings": f"{ahorro}€",
            "azDeleteCommand": _build_delete_command(base),
        })
        out.append(base)
    return out


def detect_vnets_orphaned(detector: ARGDetector) -> List[Dict[str, Any]]:
    """VNets sin subnets ni recursos asociados."""
    q = r'''
resources
| where type == 'microsoft.network/virtualnetworks'
| extend subnetCount = array_length(properties.subnets)
| where subnetCount == 0 or isempty(subnetCount)
| project id, name, resourceGroup, subscriptionId, location
'''
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "vnet", reason="VNet sin subnets ni recursos asociados")
        base.update({
            "estimatedMonthlySavings": "0€",
            "azDeleteCommand": f'az network vnet delete --resource-group "{base["resourceGroup"]}" --name "{base["nombre"]}"'
        })
        out.append(base)
    return out


def full_scan() -> List[Dict[str, Any]]:
    """Ejecuta los detectores de recursos zombis (sin snapshots)."""
    detector = ARGDetector()
    scans = [
        detect_disks_unattached(detector),
        detect_ips_orphaned(detector),
        detect_nics_without_vm(detector),
        detect_vms_not_running(detector),
        detect_loadbalancers_without_rules(detector),
        detect_appserviceplans_empty(detector),
        detect_nsgs_unassociated(detector),
        detect_vnets_orphaned(detector),
    ]
    # Aplanar resultados
    result: List[Dict[str, Any]] = []
    for s in scans:
        result.extend(s)
    return result
