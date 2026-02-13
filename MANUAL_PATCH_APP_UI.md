MANUAL PATCH — app.py Cambios Finales UI
==========================================

**OPCIÓN A: Automática (recomendado)**

```bash
# Desde raíz del proyecto con Python activado
python scripts/update_app_ui.py

# Output esperado:
# ✅ app.py actualizado correctamente
```

---

**OPCIÓN B: Manual (si script falla)**

Edita `app.py` manualmente:

### 1. Línea ~80-90 — Actualizar docstring

**BUSCAR:**
```python
"""
Guardian Efímero - Interfaz Streamlit

Aplicación web para escanear recursos "zombis" en Azure...
- Escanea 10 tipos de recursos zombis en Azure
```

**REEMPLAZAR CON:**
```python
"""
Guardian Efímero - Interfaz Streamlit (v1 — 8 detectores testeable)

Aplicación web para escanear recursos "zombis" en Azure y obtener recomendaciones del agente IA.

Características:
- Escanea 8 tipos de recursos zombis en Azure (v1 testeable)
- Obtiene recomendaciones del agente IA (acción, confianza, ahorro)
- Permite seleccionar recursos para aprobación
- Genera comandos az CLI sugeridos (sin ejecutarlos automáticamente)
- Modo demo con umbrales configurables

8 detectores en v1:
  1. Discos sin adjuntar (unattached)
  2. IPs públicas huérfanas (orphaned)
  3. Network Interfaces sin VM
  4. VMs no ejecutándose (deallocated)
  5. Load Balancers sin reglas
  6. App Service Plans vacíos
  7. Snapshots antiguos (parametrizable)
  8. Network Security Groups sin asociar

Uso:
    streamlit run app.py

Configuración sidebar:
    - resource_group_filter: Opcional, filtrar por RG
    - snapshot_age_days: Umbral día para snapshots (default 90, demo 0)
    - demo_mode: Activa modo demo con etiquetas visuales

Requisitos:
- Tener streamlit instalado: pip install streamlit
- Tener configurada la autenticación de Azure (az login)
- Tener Ollama disponible en localhost:11434 (opcional, usa heurísticas si no está disponible)
"""
```

### 2. Línea ~105-115 — Actualizar session_state

**BUSCAR:**
```python
if "scan_results" not in st.session_state:
    st.session_state.scan_results = None
if "ia_results" not in st.session_state:
    st.session_state.ia_results = None
if "selected_resources" not in st.session_state:
    st.session_state.selected_resources = {}
if "scanning" not in st.session_state:
    st.session_state.scanning = False


# Caching helpers: cache scan and analysis for the session to avoid repeated calls
@st.cache_data(ttl=300)
def cached_full_scan():
    return full_scan()
```

**REEMPLAZAR CON:**
```python
if "scan_results" not in st.session_state:
    st.session_state.scan_results = None
if "ia_results" not in st.session_state:
    st.session_state.ia_results = None
if "selected_resources" not in st.session_state:
    st.session_state.selected_resources = {}
if "scanning" not in st.session_state:
    st.session_state.scanning = False
if "snapshot_age_days" not in st.session_state:
    st.session_state.snapshot_age_days = 90
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "resource_group_filter" not in st.session_state:
    st.session_state.resource_group_filter = ""


# Caching helpers: cache scan and analysis for the session to avoid repeated calls
@st.cache_data(ttl=300)
def cached_full_scan(snapshot_age_days: int = 90):
    """Ejecuta full_scan con parámetro snapshot_age_days."""
    return full_scan(snapshot_age_days=snapshot_age_days)
```

### 3. Línea ~130-160 — Reemplazar SIDEBAR

**BUSCAR:**
```python
# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("""
    **Guardian Efímero** te ayuda a:
    1. 🔍 Escanear 10 tipos de recursos zombis
    2. 🤖 Obtener recomendaciones del agente IA
    3. ✅ Revisar y aprobar cambios
    4. 📋 Generar comandos az CLI
    """)
    
    st.markdown("---")
    if st.button("🔄 Limpiar caché", use_container_width=True):
        st.session_state.scan_results = None
        st.session_state.ia_results = None
        st.session_state.selected_resources = {}
        st.rerun()
```

**REEMPLAZAR CON:**
```python
# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Etiqueta DEMO si está activo
    if st.session_state.demo_mode:
        st.markdown("""
<div style="background-color: #FFD700; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">
🎯 DEMO MODE ACTIVO
</div>
        """, unsafe_allow_html=True)
    
    st.info("""
    **Guardian Efímero v1** te ayuda a:
    1. 🔍 Escanear 8 tipos de recursos zombis
    2. 🤖 Obtener recomendaciones del agente IA
    3. ✅ Revisar y aprobar cambios
    4. 📋 Generar comandos az CLI
    """)
    
    st.markdown("---")
    
    st.subheader("Filtros y Configuración")
    
    # Demo mode
    demo_mode_old = st.session_state.demo_mode
    st.session_state.demo_mode = st.checkbox(
        "🎯 DEMO MODE (umbrales agresivos)",
        value=st.session_state.demo_mode,
        help="Activa modo demo con valores bajos de snapshot_age_days para testear rápidamente"
    )
    
    # Resource Group filter
    st.session_state.resource_group_filter = st.text_input(
        "📁 Filtrar por Resource Group (opcional)",
        value=st.session_state.resource_group_filter,
        placeholder="Ej: HamidounElHabtiAdnan",
        help="Deja en blanco para escanear todas las suscripciones"
    )
    
    # Snapshot age days slider
    st.subheader("Snapshot Age Threshold")
    default_days = 0 if st.session_state.demo_mode else 90
    st.session_state.snapshot_age_days = st.slider(
        "📅 Snapshots más antiguos que (días)",
        min_value=0,
        max_value=365,
        value=st.session_state.snapshot_age_days if not st.session_state.demo_mode else 0,
        step=1,
        help="Default 90 días; en DEMO MODE recomendado usar 0-1 para testear"
    )
    
    if st.session_state.demo_mode and st.session_state.snapshot_age_days > 7:
        st.warning("⚠️ Demo mode con threshold alto (>7d) puede no detectar recursos de prueba")
    
    st.markdown("---")
    
    if st.button("🔄 Limpiar caché", use_container_width=True):
        st.session_state.scan_results = None
        st.session_state.ia_results = None
        st.session_state.selected_resources = {}
        st.cache_data.clear()
        st.rerun()
```

### 4. Línea ~170-210 — Actualizar Sección 1 (Escaneo)

**BUSCAR:**
```python
st.header("1️⃣ Escanear Azure")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("**Detecta los 10 tipos de recursos zombis en tu suscripción:**")
    st.markdown("""
    - 💾 Discos sin adjuntar
    - 📡 IPs públicas huérfanas
    - 💾 Bases de datos SQL offline
    - 🖥️ VMs no ejecutándose
    - 📦 Storage unavailable
    - 🏗️ App Service Plans vacíos
    - 🔗 Network Interfaces sin VM
    - 🔐 Key Vaults sin tenant
    - ⚖️ Load Balancers sin reglas
    - 📸 Snapshots antiguos (>90 días)
    """)

with col2:
    if st.button("🔍 Ejecutar escaneo", use_container_width=True, type="primary"):
        st.session_state.scanning = True

    if st.session_state.scanning:
        try:
            with st.spinner("Escaneando recursos en Azure... (puede tomar 1-2 minutos)"):
                st.session_state.scan_results = cached_full_scan()
                st.session_state.scanning = False
                st.success("✅ Escaneo completado")
        except Exception as e:
            st.error(f"❌ Error durante el escaneo: {str(e)}")
            st.session_state.scanning = False
```

**REEMPLAZAR CON:**
```python
st.header("1️⃣ Escanear Azure")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("**Detecta los 8 tipos de recursos zombis en tu suscripción (v1):**")
    st.markdown(f"""
    - 💾 Discos sin adjuntar
    - 📡 IPs públicas huérfanas
    - 🔗 Network Interfaces sin VM
    - 🖥️ VMs no ejecutándose (deallocated)
    - ⚖️ Load Balancers sin reglas
    - 🏗️ App Service Plans vacíos
    - 📸 Snapshots antiguos (>{st.session_state.snapshot_age_days} días)
    - 🔒 Network Security Groups sin asociar
    """)

with col2:
    if st.button("🔍 Ejecutar escaneo", use_container_width=True, type="primary"):
        st.session_state.scanning = True

    if st.session_state.scanning:
        try:
            with st.spinner("Escaneando recursos en Azure... (puede tomar 1-2 minutos)"):
                # Pasar snapshot_age_days a cached_full_scan
                st.session_state.scan_results = cached_full_scan(
                    snapshot_age_days=st.session_state.snapshot_age_days
                )
                st.session_state.scanning = False
                st.success("✅ Escaneo completado")
        except Exception as e:
            st.error(f"❌ Error durante el escaneo: {str(e)}")
            st.session_state.scanning = False
```

---

## ✅ Después de aplicar patches

```bash
# 1. Validar no hay errores syntax
python -m py_compile app.py
# Output esperado: (nada = OK)

# 2. Ejecutar
streamlit run app.py

# 3. En UI:
#    - Sidebar debe mostrar: ☑️ DEMO MODE, slider snapshot_age_days, input RG
#    - Sección 1 debe mostrar: 8 detectores (no 10)
#    - Etiqueta amarilla 🎯 DEMO MODE si está activado
```

---

## 🆘 Si ocurren errores

**Error: "module 'src.detectores' has no attribute 'full_scan"**
- Verificar: `from src.detectores import full_scan` en top de app.py
- Solución: `pip install -e .` o `python -m pip install -e .`

**Error: AttributeError en st.session_state**
- Verificar: Todos los `if "X" not in st.session_state` están en orden correcto
- Solución: Copiar toda la sección session_state (paso 2 arriba)

**Snapshot no se detectan en demo**
- Fix: En sidebar, baja snapshot_age_days a 0 (demo_mode debería hacerlo automático)

**UI sidebar sigue siendo vieja**
- Verify: Reemplazaste la sección SIDEBAR completa (no solo parte)
- Try: Ctrl+Shift+R (reload hard) en navegador browser
- Verify: `st.cache_data.clear()` ejecutado en sidebar

---

**¡Después de aplicar estos parches, Guardian Efímero v1 está 100% listo!** ✅
