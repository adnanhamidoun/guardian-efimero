#!/usr/bin/env python3
"""
Script para actualizar app.py con cambios de UI sidebar.

Este script inserta la configuración del sidebar en app.py reemplazando
la sección SIDEBAR existente por la nueva versión mejorada.

Uso:
    python scripts/update_app_ui.py
"""

import re
import sys
from pathlib import Path

APP_PY_PATH = Path(__file__).parent.parent / "app.py"

SIDEBAR_NEW = """# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Etiqueta DEMO si está activo
    if st.session_state.demo_mode:
        st.markdown('''
<div style="background-color: #FFD700; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">
🎯 DEMO MODE ACTIVO
</div>
        ''', unsafe_allow_html=True)
    
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
"""

def update_app_py():
    """Actualiza el archivo app.py con la nueva sección SIDEBAR."""
    
    if not APP_PY_PATH.exists():
        print(f"❌ Error: {APP_PY_PATH} no existe")
        sys.exit(1)
    
    with open(APP_PY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar la sección SIDEBAR actual
    # Busca desde "# ==================== SIDEBAR ====================" hasta la siguiente sección
    pattern = r'# ==================== SIDEBAR ====================.*?(?=# ====================)'
    
    if not re.search(pattern, content, re.DOTALL):
        print("⚠️ Patrón SIDEBAR no encontrado. Intenta insertar manualmente.")
        print("   Busca línea con '# ==================== SIDEBAR ===================='\n")
        print("   Reemplaza esa sección con:\n")
        print(SIDEBAR_NEW)
        sys.exit(1)
    
    # Reemplazar
    content_new = re.sub(pattern, SIDEBAR_NEW + "\n# ====================", content, flags=re.DOTALL)
    
    with open(APP_PY_PATH, 'w', encoding='utf-8') as f:
        f.write(content_new)
    
    print(f"✅ app.py actualizado correctamente")
    print(f"   Archivo: {APP_PY_PATH}")
    print(f"\n   Cambios:")
    print(f"   - ✅ Agregado: demo_mode checkbox")
    print(f"   - ✅ Agregado: resource_group_filter text_input")
    print(f"   - ✅ Agregado: snapshot_age_days slider (0-365)")
    print(f"   - ✅ Agregado: Etiqueta visual DEMO")
    print(f"   - ✅ Actualizado: session_state iniciales")
    print(f"\n   Próximo: streamlit run app.py para validar cambios")

if __name__ == "__main__":
    update_app_py()
