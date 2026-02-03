import json
from unittest.mock import patch, Mock
import subprocess

from src.ia_agente import parse_guardian_table, fetch_zombis, call_ollama, fallback_decision, agente_main

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


@patch('src.ia_agente.requests.post')
def test_call_ollama_success(mock_post):
    # response.json() returns {'response': '<json-as-string>'}
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {'response': json.dumps({'accion':'borrar','confianza':9,'ahorro':'2.4€','razon':'ok'})}
    mock_post.return_value = resp

    res = call_ollama({'nombre': 'x', 'size_gb': 40, 'resourceGroup': 'rg'})
    assert isinstance(res, dict)
    assert res['accion'] == 'borrar'


def test_agente_fallback_heuristic(monkeypatch):
    # Forcing no Ollama: monkeypatch call_ollama to return None
    monkeypatch.setattr('src.ia_agente.call_ollama', lambda z: None)
    # Monkeypatch fetch_zombis to return a big disk
    monkeypatch.setattr('src.ia_agente.fetch_zombis', lambda: [{"nombre":"disk-test","size_gb":40,"resourceGroup":"rg"}])

    out = agente_main(print_json=False)
    assert 'zombis' in out
    assert out['zombis'][0]['fallback'] is True
    assert out['zombis'][0]['accion'] == 'borrar'
    assert out['zombis'][0]['ahorro'].endswith('€')
