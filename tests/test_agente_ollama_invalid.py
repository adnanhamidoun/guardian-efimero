import json
from unittest.mock import Mock, patch
import subprocess

from src.ia_agente import fallback_decision, analyze_zombi, agente_main

def test_fallback_decision_disk():
    """Test fallback_decision (heuristic) for disk type"""
    result = fallback_decision({'tipo': 'disk', 'nombre': 'disk-1', 'size_gb': 100})
    assert result['accion'] == 'Borrar'
    assert result['confianza'] == 100
    assert 'razon' in result

def test_fallback_decision_ip():
    """Test fallback_decision (heuristic) for IP type"""
    result = fallback_decision({'tipo': 'ip', 'nombre': 'ip-1'})
    assert result['accion'] == 'Borrar'
    assert result['confianza'] == 100
    assert 'IP' in result['razon'] or 'ip' in result['razon'].lower()

def test_fallback_decision_unknown_type():
    """Test fallback_decision for unknown type (uses general heuristic)"""
    result = fallback_decision({'tipo': 'unknown', 'nombre': 'unknown-1'})
    assert result['accion'] == 'Borrar'
    assert result['confianza'] >= 70
    assert 'razon' in result

@patch('src.ia_agente.fetch_zombis')
def test_agente_all_heuristic(mock_fetch):
    """Test agente_main with all heuristics-only (no external calls)"""
    mock_fetch.return_value = [
        {"nombre":"disk-test","tipo":"disk","diskState":"Unattached","size_gb":40,"resourceGroup":"rg"},
        {"nombre":"ip-orphan","tipo":"ip","resourceGroup":"rg"}
    ]
    out = agente_main(print_json=False)
    
    assert 'zombis' in out
    assert len(out['zombis']) >= 2
    # All should be heuristic  
    assert all(z['metodo'] == 'heuristic' for z in out['zombis'])
    # All should have valid decisions
    assert all(z['accion'] in ('Borrar', 'borrar', 'delete') for z in out['zombis'])
    assert all(isinstance(z['confianza'], int) for z in out['zombis'])
    assert all(z['ahorro'].endswith('€') for z in out['zombis'])

