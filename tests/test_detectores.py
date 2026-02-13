from unittest.mock import patch
from src.detectores import (
    detect_disks_unattached,
    detect_ips_orphaned,
    detect_vms_not_running,
    detect_appserviceplans_empty,
    detect_nics_without_vm,
    detect_loadbalancers_without_rules,
    detect_snapshots_old,
    detect_nsgs_unassociated,
    full_scan,
)


class DummyDetector:
    def __init__(self, rows):
        self._rows = rows

    def _run_query(self, q):
        return self._rows


def test_detect_disks_unattached_simple():
    rows = [{"id": "/subscriptions/1/.../disk/1", "name": "d1", "resourceGroup": "rg1", "subscriptionId": "s1", "diskSizeGB": 10}]
    out = detect_disks_unattached(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "disk"
    assert out[0]["ahorro"].endswith('€')


def test_detect_ips_orphaned_simple():
    rows = [{"id": "/.../ip/1", "name": "ip1", "resourceGroup": "rg1", "subscriptionId": "s1", "ipAddress": "1.2.3.4"}]
    out = detect_ips_orphaned(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "ip"


def test_detect_sql_databases_offline_simple():
    rows = [{"id": "/.../sql/1", "name": "sql1", "resourceGroup": "rg1", "subscriptionId": "s1", "status": "offline"}]
    out = detect_sql_databases_offline(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "sql"


def test_detect_vms_not_running_simple():
    rows = [{"id": "/.../vm/1", "name": "vm1", "resourceGroup": "rg1", "subscriptionId": "s1", "powerState": "stopped"}]
    out = detect_vms_not_running(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "vm"


def test_detect_storage_unavailable_simple():
    rows = [{"id": "/.../st/1", "name": "st1", "resourceGroup": "rg1", "subscriptionId": "s1", "prov": "failed", "blobCount": 0, "containerCount": 0}]
    out = detect_storage_unavailable(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "storage"


def test_detect_storage_stgteste7180():
    """Test específico para detectar stgteste7180 - storage sin blobs/containers"""
    rows = [
        {
            "id": "/subscriptions/XXX/resourceGroups/HamidounElHabtiAdnan/providers/Microsoft.Storage/storageAccounts/stgteste7180",
            "name": "stgteste7180",
            "resourceGroup": "HamidounElHabtiAdnan",
            "subscriptionId": "test-sub",
            "prov": "succeeded",
            "blobCount": 0,
            "containerCount": 0,
            "timeCreated": "2026-02-04T00:00:00Z"  # Creado recientemente
        }
    ]
    out = detect_storage_unavailable(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "storage"
    assert out[0]["nombre"] == "stgteste7180"
    assert out[0]["resourceGroup"] == "HamidounElHabtiAdnan"
    assert "€" in out[0]["ahorro"]


def test_detect_storage_by_recent_creation():
    """Test storage zombi detectado por creación reciente (posible error)"""
    rows = [
        {
            "id": "/.../st/recent",
            "name": "storage-new",
            "resourceGroup": "rg1",
            "subscriptionId": "s1",
            "prov": "succeeded",
            "blobCount": 5,
            "containerCount": 1,
            "timeCreated": "2026-02-02T00:00:00Z"  # Hace 2 días
        }
    ]
    out = detect_storage_unavailable(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "storage"


def test_detect_storage_by_failed_provisioning():
    """Test storage zombi detectado por provisioning fallido"""
    rows = [
        {
            "id": "/.../st/failed",
            "name": "storage-failed",
            "resourceGroup": "rg1",
            "subscriptionId": "s1",
            "prov": "failed",
            "blobCount": 0,
            "containerCount": 0
        }
    ]
    out = detect_storage_unavailable(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "storage"


def test_detect_appserviceplans_empty_simple():
    rows = [{"id": "/.../asp/1", "name": "asp1", "resourceGroup": "rg1", "subscriptionId": "s1", "numberOfSites": 0}]
    out = detect_appserviceplans_empty(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "appserviceplan"


def test_detect_nics_without_vm_simple():
    rows = [{"id": "/.../nic/1", "name": "nic1", "resourceGroup": "rg1", "subscriptionId": "s1"}]
    out = detect_nics_without_vm(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "nic"


def test_detect_keyvaults_without_tenant_simple():
    rows = [{"id": "/.../kv/1", "name": "kv1", "resourceGroup": "rg1", "subscriptionId": "s1"}]
    out = detect_keyvaults_without_tenant(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "keyvault"


def test_detect_loadbalancers_without_rules_simple():
    rows = [{"id": "/.../lb/1", "name": "lb1", "resourceGroup": "rg1", "subscriptionId": "s1"}]
    out = detect_loadbalancers_without_rules(DummyDetector(rows))
    assert len(out) == 1
    assert out[0]["tipo"] == "loadbalancer"


def test_detect_snapshots_old_simple():
    rows = [{"id": "/.../snap/1", "name": "snap1", "resourceGroup": "rg1", "subscriptionId": "s1", "diskSizeGB": 30, "timeCreated": "2025-01-01T00:00:00Z"}]
    out = detect_snapshots_old(DummyDetector(rows), days=90)
    assert len(out) == 1
    assert out[0]["tipo"] == "snapshot"


def test_full_scan_aggregates_all():
    # For full_scan we patch ARGDetector to return no rows (sanity check: should return a list)
    with patch('src.detectores.ARGDetector') as MockDet:
        MockDet.return_value._run_query.return_value = []
        res = full_scan()
        assert isinstance(res, list)
