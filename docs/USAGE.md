# USAGE

Paso a paso para usar Guardian Efímero

1. Preparar entorno

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Escanear recursos (terminal)

```powershell
make full_scan
```

3. Ejecutar interfaz Streamlit

```powershell
streamlit run app.py
```

4. Flujo en la UI

- Pestaña "Scan": Ejecuta el escaneo y revisa resultados.
- Pestaña "Recomendaciones": Ejecuta el agente híbrido para obtener acciones sugeridas.
- Pestaña "Aprobación": Selecciona recursos para procesar.
- Pestaña "Comandos": Revisa y descarga el script con los comandos `az`.

5. Ejecutar comandos (MANUAL)

Revisa el script y ejecuta los comandos desde tu terminal. Haz backups antes de borrar recursos.
