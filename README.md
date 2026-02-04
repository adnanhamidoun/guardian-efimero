# 🛡 El Guardián Efímero

Agente IA local-first FinOps Azure | [PDF visión](docs/vision.md)

## Status
# Guardian Efímero

Herramienta FinOps para detectar y gestionar "recursos zombis" en Azure.

Resumen:
- Escanea 10 tipos de recursos (discos, IPs, storage, SQL, VMs, etc.)
- Recomienda acciones con un agente híbrido (heurística + Ollama)
- Permite aprobación humana y genera comandos `az` para ejecución manual

Requisitos:
- Python 3.11+ (probado en 3.13)
- Tener `az` configurado y autenticado (az login)
- (Opcional) Ollama en `http://localhost:11434` para recomendaciones IA

Instalación rápida (desde la raíz del repositorio):
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

Comandos útiles:
- Ejecutar escaneo en terminal: `make full_scan`  
- Ejecutar agente IA: `make agente-hybrid`  
- Ejecutar UI: `streamlit run app.py`

Seguridad:
- Esta aplicación NO ejecuta comandos en Azure automáticamente. Siempre revisa y ejecuta los comandos generados de forma manual.

Ver `docs/` para más detalles de uso y arquitectura.

