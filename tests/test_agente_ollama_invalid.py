import json
from unittest.mock import Mock, patch
import subprocess

from src.ia_agente import call_ollama, agente_main

@patch('src.ia_agente.requests.post')
def test_call_ollama_empty_body(mock_post):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {}  # respuesta vacía
    mock_post.return_value = resp

    res = call_ollama({'nombre': 'x', 'size_gb': 40, 'resourceGroup': 'rg'})
    assert res is None

@patch('src.ia_agente.requests.post')
def test_call_ollama_bad_response_string(mock_post):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {'response': 'no json here'}
    mock_post.return_value = resp

    res = call_ollama({'nombre': 'x', 'size_gb': 40, 'resourceGroup': 'rg'})
    assert res is None

@patch('src.ia_agente.requests.post')
@patch('src.ia_agente.fetch_zombis')
def test_agente_uses_fallback_when_ollama_invalid(mock_fetch, mock_post):
    # Ollama devuelve respuesta inválida
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {'response': 'bad'}
    mock_post.return_value = resp

    mock_fetch.return_value = [{"nombre":"disk-test","size_gb":40,"resourceGroup":"rg"}]
    out = agente_main(print_json=False)
    assert out['zombis'][0]['fallback'] is True
    assert out['zombis'][0]['accion'] in ('borrar','snapshot','keep')
