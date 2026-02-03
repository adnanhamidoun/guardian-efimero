"""Detectores Fase 3 — 10 tipos de zombis Azure.

Cada función ejecuta una Query KQL (vía ARGDetector._run_query) y normaliza la salida a
una lista de diccionarios con claves mínimas:
  - tipo: str
  - id: resource id si está disponible
  - nombre (name)
  - resourceGroup
  - subscriptionId
  - confianza: float (heurística)
  - ahorro: str (ej: "12.34€")

Exporta `full_scan()` que devuelve la lista concatenada de los 10 detectores.
"""
from typing import List, Dict, Any

from tools.arg_detector import ARGDetector

# Heurísticas de ahorro por tipo (valores por defecto para fallback)
HEUR_PRICES = {
    "disk_per_gb": 0.08,  # €/mes/GB
    "ip": 3.0,            # €/mes por IP pública
    "sql": 45.0,
    "vm_stopped": 60.0,
    "storage": 10.0,
    "appserviceplan": 5.0,
    "nic": 1.0,
    "keyvault": 0.5,
    "lb": 2.0,
    "snapshot_day_factor": 0.08,  # €/GB per day factor (very rough)
}


def _normalize_base(row: Dict[str, Any], tipo: str) -> Dict[str, Any]:
    return {
        "tipo": tipo,
        "id": row.get("id") or row.get("resourceId") or None,
        "nombre": row.get("name") or row.get("nombre") or None,
        "resourceGroup": row.get("resourceGroup"),
        "subscriptionId": row.get("subscriptionId"),
        "confianza": 8.0,
    }


def detect_disks_unattached(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.compute/disks'
| extend diskState = tostring(properties.diskState)
| where tolower(diskState) == 'unattached' or isempty(tostring(managedBy)) or tostring(managedBy) == ''
| project id, name, resourceGroup, subscriptionId, diskSizeGB = properties.diskSizeGB, timeCreated = properties.timeCreated
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "disk")
        try:
            size = int(r.get("diskSizeGB") or 0)
        except Exception:
            size = 0
        ahorro = round(size * HEUR_PRICES["disk_per_gb"], 2)
        base.update({"size_gb": size, "ahorro": f"{ahorro}€"})
        out.append(base)
    return out


def detect_ips_orphaned(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.network/publicipaddresses'
| where isnull(properties['ipConfiguration']) or tostring(properties['ipConfiguration']) == ''
| project id, name, resourceGroup, subscriptionId, ipAddress = tostring(properties.ipAddress)
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "ip")
        ahorro = round(HEUR_PRICES["ip"], 2)
        base.update({"ipAddress": r.get("ipAddress"), "ahorro": f"{ahorro}€"})
        out.append(base)
    return out


def detect_sql_databases_offline(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type has 'microsoft.sql/servers/databases'
| extend status = tostring(properties.status) // attempt
| where status == '' or tolower(status) != 'online'
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "sql")
        base.update({"ahorro": f"{HEUR_PRICES['sql']}€"})
        out.append(base)
    return out


def detect_vms_not_running(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.compute/virtualmachines'
| extend powerState = tostring(properties['powerState'])
| where powerState != '' and tolower(powerState) != 'vm running' and tolower(powerState) != 'running'
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "vm")
        base.update({"ahorro": f"{HEUR_PRICES['vm_stopped']}€"})
        out.append(base)
    return out


def detect_storage_unavailable(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.storage/storageaccounts'
| extend prov = tostring(properties['provisioningState'])
| where prov != '' and tolower(prov) != 'succeeded'
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "storage")
        base.update({"ahorro": f"{HEUR_PRICES['storage']}€"})
        out.append(base)
    return out


def detect_appserviceplans_empty(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.web/serverfarms'
| extend sites = tostring(properties['numberOfSites'])
| where sites == '' or toint(sites) == 0
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "appserviceplan")
        base.update({"ahorro": f"{HEUR_PRICES['appserviceplan']}€"})
        out.append(base)
    return out


def detect_nics_without_vm(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.network/networkinterfaces'
| where isnull(properties['virtualMachine']) or tostring(properties['virtualMachine']) == ''
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "nic")
        base.update({"ahorro": f"{HEUR_PRICES['nic']}€"})
        out.append(base)
    return out


def detect_keyvaults_without_tenant(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.keyvault/vaults'
| where isnull(properties['tenantId']) or tostring(properties['tenantId']) == ''
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "keyvault")
        base.update({"ahorro": f"{HEUR_PRICES['keyvault']}€"})
        out.append(base)
    return out


def detect_loadbalancers_without_rules(detector: ARGDetector) -> List[Dict[str, Any]]:
    q = r"""
resources
| where type == 'microsoft.network/loadbalancers'
| where isnull(properties['loadBalancingRules']) or tostring(properties['loadBalancingRules']) == ''
| project id, name, resourceGroup, subscriptionId
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "loadbalancer")
        base.update({"ahorro": f"{HEUR_PRICES['lb']}€"})
        out.append(base)
    return out


def detect_snapshots_old(detector: ARGDetector, days: int = 90) -> List[Dict[str, Any]]:
    # Buscamos snapshots y devolvemos los mayores a `days` mediante un campo timeCreated
    q = rf"""
resources
| where type == 'microsoft.compute/snapshots'
| extend timeCreated = todatetime(properties.timeCreated)
| where timeCreated <= ago({days}d)
| project id, name, resourceGroup, subscriptionId, diskSizeGB = properties.diskSizeGB, timeCreated
"""
    rows = detector._run_query(q)
    out = []
    for r in rows:
        base = _normalize_base(r, "snapshot")
        try:
            size = int(r.get("diskSizeGB") or 0)
        except Exception:
            size = 0
        ahorro = round(size * HEUR_PRICES['snapshot_day_factor'] * (days / 30.0), 2)
        base.update({"size_gb": size, "timeCreated": r.get("timeCreated"), "ahorro": f"{ahorro}€"})
        out.append(base)
    return out


def full_scan() -> List[Dict[str, Any]]:
    detector = ARGDetector()
    scans = [
        detect_disks_unattached(detector),
        detect_ips_orphaned(detector),
        detect_sql_databases_offline(detector),
        detect_vms_not_running(detector),
        detect_storage_unavailable(detector),
        detect_appserviceplans_empty(detector),
        detect_nics_without_vm(detector),
        detect_keyvaults_without_tenant(detector),
        detect_loadbalancers_without_rules(detector),
        detect_snapshots_old(detector),
    ]
    # aplanar
    result: List[Dict[str, Any]] = []
    for s in scans:
        result.extend(s)
    return result
