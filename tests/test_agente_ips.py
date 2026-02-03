import subprocess
from unittest.mock import patch

from src.ia_agente import agente_main

SAMPLE_BOTH = """
                           DISCOS ZOMBIS                            
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Nombre        ┃ Resource Group       ┃ Location   ┃ Sub ID      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ demo-llm-disk │ hamidounelhabtiadnan │ westeurope │ 4721a86d... │
│ zombie-alpha  │ hamidounelhabtiadnan │ westeurope │ 4721a86d... │
│ zombie-beta   │ hamidounelhabtiadnan │ westeurope │ 4721a86d... │
└───────────────┴──────────────────────┴────────────┴─────────────┘
3 zombis detectados!

                            IPs HÚRFANAS                            
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Nombre        ┃ Resource Group       ┃ Location   ┃ Sub ID      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ ip-zombie-001 │ hamidounelhabtiadnan │ westeurope │ 4721a86d... │
│ ip-zombie-002 │ hamidounelhabtiadnan │ westeurope │ 4721a86d... │
└───────────────┴──────────────────────┴────────────┴─────────────┘
2 zombis detectados!
"""

@patch('src.ia_agente.subprocess.run')
@patch('src.ia_agente.call_ollama')
def test_agente_includes_ips(mock_ollama, mock_run):
    # Forzar fallback de Ollama
    mock_ollama.return_value = None
    mock_run.return_value = subprocess.CompletedProcess(args=['python','src/guardian.py'], returncode=0, stdout=SAMPLE_BOTH)

    out = agente_main(print_json=False)
    assert 'zombis' in out
    assert len(out['zombis']) == 5
    ips = [z for z in out['zombis'] if z.get('resourceGroup') == 'hamidounelhabtiadnan' and (z.get('nombre').startswith('ip-') or z.get('type') == 'ip')]
    assert len(ips) == 2
    # Verificar que ahorro para IP coincide con cadena euro
    assert any(z.get('ahorro','').endswith('€') for z in out['zombis'])
