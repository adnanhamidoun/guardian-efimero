import json
from unittest.mock import patch, Mock
import subprocess

from src.ia_agente import parse_guardian_table, fetch_zombis, fallback_decision, analyze_zombi, agente_main

SAMPLE_GUARDIAN_OUTPUT = """
                                  DISCOS ZOMBIS                                  
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Nombre                   ┃ Resource Group       ┃ Location      ┃ Sub ID      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ test-zombi-disk-001      │ hamidounelhabtiadnan │ westeurope    │ 4721a86d... │
└──────────────────────────┴──────────────────────┴───────────────┴─────────────┘
"""


def test_parse_guardian_table():
    rows = parse_guardian_table(SAMPLE_GUARDIAN_OUTPUT, section_title="DISCOS ZOMBIS")
    assert len(rows) == 1
    assert rows[0]["nombre"] == "test-zombi-disk-001"
    assert rows[0]["resourceGroup"] == "hamidounelhabtiadnan"


@patch('src.ia_agente.subprocess.run')
def test_fetch_zombis_from_stdout(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(args=['python', 'src/guardian.py'], returncode=0, stdout=SAMPLE_GUARDIAN_OUTPUT)
    z = fetch_zombis()
    assert isinstance(z, list)
    assert z[0]["nombre"] == "test-zombi-disk-001"




def test_analyze_zombi_heuristic_disk():
    """Test heuristic-only analyze_zombi for disk"""
    result = analyze_zombi({
        'nombre': 'disk-test',
        'tipo': 'disk',
        'diskState': 'Unattached',
        'size_gb': 40,
        'resourceGroup': 'rg'
    })
    assert isinstance(result, dict)
    assert result['accion'] == 'Borrar'
    assert result['confianza'] == 100
    assert result['metodo'] == 'heuristic'
    assert 'ahorro' in result and result['ahorro'].endswith('€')


def test_agente_heuristic_only(monkeypatch):
    """Test agente_main (heuristics-only) with sample zombies"""
    # Monkeypatch fetch_zombis to return sample zombie resources
    monkeypatch.setattr('src.ia_agente.fetch_zombis', lambda: [
        {"nombre":"disk-test","tipo":"disk","diskState":"Unattached","size_gb":40,"resourceGroup":"rg"},
        {"nombre":"ip-test","tipo":"ip","resourceGroup":"rg"}
    ])

    out = agente_main(print_json=False)
    assert 'zombis' in out
    assert len(out['zombis']) == 2
    # Both should be marked as heuristic method
    assert all(z['metodo'] == 'heuristic' for z in out['zombis'])
    # All should have delete action
    assert all(z['accion'].lower() in ('borrar', 'delete') for z in out['zombis'])
    # All should have ahorro in euros
    assert all(z['ahorro'].endswith('€') for z in out['zombis'])

