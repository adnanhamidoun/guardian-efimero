DEMO — Guardian Efímero (v1) — 5 minutos
=========================================

Objetivo
--------
Crear un entorno demo reproducible con 8 recursos "zombi", escanearlos con la app y limpiar todo después.

Requisitos
----------
- Azure CLI configurado y autenticado (`az login`)
- PowerShell (Windows PowerShell o PowerShell Core)
- Entorno virtual Python activado (opcional)
- Tener la app lista: `streamlit run app.py`

Archivos útiles
--------------
- `scripts/demo_setup.ps1`  — crea recursos demo (vnet, disk, nic, vm, lb, appplan, snapshot, nsg)
- `scripts/demo_cleanup.ps1` — elimina recursos demo por tag o borra RG completo
- `app.py` — Streamlit UI

Flujo rápido (5 minutos)
------------------------
1. (Opcional) Crear Resource Group y ejecutar demo setup:

```powershell
# Crea los recursos demo en RG HamidounElHabtiAdnan
.\scripts\demo_setup.ps1
```

2. Ejecuta la app Streamlit:

```powershell
streamlit run app.py
```

3. En la UI:
- En el `Sidebar` activa `DEMO MODE` o fija `snapshot_age_days=0`
- Filtra por `Resource Group`: `HamidounElHabtiAdnan` (opcional)
- En `1️⃣ Escanear Azure` presiona `🔍 Ejecutar escaneo`

4. Comprobaciones esperadas:
- El escaneo detecta los tipos: Disk, IP, NIC, VM (deallocated), LoadBalancer, AppServicePlan, Snapshot, NSG
- Verás valores de `Ahorro` por recurso (ej: `2.56€`)
- En `2️⃣ Recomendaciones del Agente IA` puedes obtener decisiones (Borrar/Snapshot/Keep)
- En `3️⃣ Aprobación Humana` selecciona recursos (checkboxes)
- En `4️⃣ Comandos az CLI Sugeridos` copia/descarga el script generado

5. Limpieza (importante):

```powershell
# Borra solo recursos con tag demo=zombi en el RG
.\scripts\demo_cleanup.ps1

# O bien, para borrar el Resource Group completo (peligroso).
.\scripts\demo_cleanup.ps1 -DeleteResourceGroup $true
```

Notas
-----
- La app NUNCA ejecuta comandos en Azure. Solo genera los comandos; revisa y ejecuta manualmente.
- Si la detección de snapshots no aparece, usa `snapshot_age_days=0` en el sidebar para pruebas rápidas.
- Si algo falla con ARG, revisa que `az` esté instalado y que tengas acceso a los recursos en la suscripción.

Troubleshooting rápido
----------------------
- "No autenticado": `az login`
- "0 recursos": Asegúrate de ejecutar `demo_setup.ps1` en el mismo RG y usar el filtro RG en la UI
- Errores ARG (ParserFailure): el código intenta fallback a `az`; revisa permisos y disponibilidad de `az`

Fin
---
Si quieres, puedo también añadir un badge en el README y un pequeño comando `Makefile` para ejecutar el demo automáticamente.