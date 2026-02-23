#!/usr/bin/env python
"""
Test rápido de detección de storage zombis
Verifica que stgteste7180 se detecta correctamente
"""

from src.detectores import detect_storage_unavailable

class MockDetector:
    def _run_query(self, q):
        """Simula stgteste7180 - storage sin blobs/containers"""
        return [
            {
                "id": "/subscriptions/test/resourceGroups/HamidounElHabtiAdnan/providers/Microsoft.Storage/storageAccounts/stgteste7180",
                "name": "stgteste7180",
                "resourceGroup": "HamidounElHabtiAdnan",
                "subscriptionId": "test-sub",
                "prov": "succeeded",
                "blobCount": 0,
                "containerCount": 0,
                "timeCreated": "2026-02-04T00:00:00Z"
            },
            {
                "id": "/subscriptions/test/resourceGroups/HamidounElHabtiAdnan/providers/Microsoft.Storage/storageAccounts/disk-test-efimero",
                "name": "disk-test-efimero",
                "resourceGroup": "HamidounElHabtiAdnan",
                "subscriptionId": "test-sub",
                "prov": "succeeded",
                "blobCount": 100,
                "containerCount": 5,
                "timeCreated": "2025-01-01T00:00:00Z"
            }
        ]

def test_storage_detection():
    """Prueba detección de storage zombis"""
    print("🧪 Testing detect_storage_unavailable()...")
    print()
    
    detector = MockDetector()
    results = detect_storage_unavailable(detector)
    
    print(f"✅ Detectados: {len(results)} storage zombis")
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['nombre']}")
        print(f"   - Tipo: {result['tipo']}")
        print(f"   - RG: {result['resourceGroup']}")
        print(f"   - Ahorro: {result['ahorro']}")
        if 'razon' in result:
            print(f"   - Razón: {result['razon']}")
        print()
    
    # Verificar que stgteste7180 se detectó
    nombres_detectados = [r['nombre'] for r in results]
    
    if 'stgteste7180' in nombres_detectados:
        print("✅ SUCCESS: stgteste7180 detectado correctamente!")
        return True
    else:
        print("❌ FAILED: stgteste7180 NO fue detectado")
        print(f"   Detectados: {nombres_detectados}")
        return False

if __name__ == "__main__":
    success = test_storage_detection()
    exit(0 if success else 1)
