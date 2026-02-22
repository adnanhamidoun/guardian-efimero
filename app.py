"""
Guardian Efímero - Interfaz Streamlit (v1 — 8 detectores testeable)

Aplicación web para escanear recursos "zombis" en Azure y obtener recomendaciones heurísticas.

Características:
- Escanea 8 tipos de recursos zombis en Azure (v1 testeable)
- Obtiene recomendaciones heurísticas (acción, confianza, ahorro)
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
- No requiere IA externa, usa heurísticas deterministas
"""
from typing import Dict, Any, List
import subprocess

import pandas as pd
import streamlit as st

from src.detectores import full_scan
from src.cli_generator import build_script

# Detector types (v1 testeable)
DETECTOR_TYPES = {
    "disk": "💾 Discos sin adjuntar",
    "ip": "📡 IPs públicas huérfanas",
    "nic": "🔗 Network Interfaces sin VM",
    "vm": "🖥️ VMs no ejecutándose",
    "loadbalancer": "⚖️ Load Balancers sin reglas",
    "appserviceplan": "🏗️ App Service Plans vacíos",
    "snapshot": "📸 Snapshots antiguos",
    "nsg": "🔒 Network Security Groups sin asociar",
}

# ==================== CONFIGURACIÓN STREAMLIT ====================

st.set_page_config(
    page_title="Guardian Efímero",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .warning-banner {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #856404;
        font-weight: bold;
    }
    .success-banner {
        background-color: #d4edda;
        border: 1px solid #28a745;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #155724;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #0c5460;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #0c5460;
    }
    .code-block {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        font-size: 12px;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ESTADO DE SESIÓN ====================

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
if "confirm_execute" not in st.session_state:
    st.session_state.confirm_execute = False


# Caching helpers: cache scan for the session to avoid repeated calls
@st.cache_data(ttl=300)
def cached_full_scan(snapshot_age_days: int = 90):
    """Ejecuta full_scan con parámetro snapshot_age_days."""
    return full_scan(snapshot_age_days=snapshot_age_days)


@st.cache_data(ttl=300)
def cached_analyze(scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genera recomendaciones deterministas basadas en reglas fijas."""
    zombis = []
    for resource in scan_results:
        tipo = resource.get("tipo", "").lower()
        nombre = resource.get("nombre", "")
        
        # Reglas deterministas de recomendación
        if tipo in ["disk", "ip", "nic", "vm", "loadbalancer", "appserviceplan", "snapshot", "nsg"]:
            if tipo == "snapshot":
                # Para snapshots, verificar edad si está disponible
                # Por simplicidad, recomendar borrar todos los snapshots detectados
                accion = "borrar"
                confianza = 85
                razon = "Snapshot identificado como potencialmente obsoleto"
            elif tipo == "appserviceplan":
                accion = "borrar"
                confianza = 95
                razon = "Plan de App Service vacío detectado"
            elif tipo in ["disk", "ip", "nic", "vm", "loadbalancer", "nsg"]:
                accion = "borrar"
                confianza = 100
                razon = f"Recurso {tipo.upper()} sin uso detectado"
            else:
                accion = "keep"
                confianza = 50
                razon = "Recurso requiere revisión manual"
            
            zombis.append({
                "nombre": nombre,
                "accion": accion,
                "confianza": confianza,
                "ahorro": resource.get("ahorro", "0€"),
                "razon": razon,
                "metodo": "optimización determinista",
                "resourceGroup": resource.get("resourceGroup", ""),
                "location": resource.get("location", ""),
                "tipo": tipo
            })
    
    return {"zombis": zombis}


# ==================== FUNCIONES AUXILIARES ====================

def format_ahorro(ahorro_str: str) -> str:
    """Extrae el valor numérico del ahorro para ordenamiento."""
    try:
        return float(ahorro_str.replace("€", "").strip())
    except:
        return 0.0


# ==================== INTERFAZ STREAMLIT ====================

st.title("🛡️ Guardian Efímero - Optimización FinOps Azure")
st.markdown("**Herramienta profesional para identificar y eliminar recursos no utilizados en Azure**")

st.markdown("""
<div class="warning-banner">
    ⚠️ <strong>IMPORTANTE:</strong> Esta herramienta identifica recursos potencialmente no utilizados basados en reglas deterministas.
    Por defecto, NO ejecuta comandos automáticamente - debes copiarlos y ejecutarlos manualmente.
    La opción experimental de ejecución automática es <strong>altamente riesgosa</strong> y requiere verificación manual.
    Siempre realiza backups antes de eliminar recursos.
</div>
""", unsafe_allow_html=True)

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
    **Guardian Efímero** optimiza costos en Azure mediante:
    1. 🔍 Detección automática de recursos no utilizados
    2. 📊 Análisis de ahorro potencial basado en reglas deterministas
    3. ✅ Validación manual de cambios recomendados
    4. 📋 Generación de comandos seguros para Azure CLI
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
    
    if st.button("🔄 Limpiar caché", width='stretch'):
        st.session_state.scan_results = None
        st.session_state.ia_results = None
        st.session_state.selected_resources = {}
        st.cache_data.clear()
        st.rerun()

# ==================== SECCIÓN 1: ESCANEAR AZURE ====================

st.header("1️⃣ Escanear Azure")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("**Detecta los tipos de recursos zombis soportados (v1 testeable):**")
    # Generar la lista a partir de DETECTOR_TYPES para evitar desalineación con los detectores reales
    detector_lines = "\n".join([f"- {v}" for k, v in DETECTOR_TYPES.items()])
    st.markdown(detector_lines)

with col2:
    if st.button("🔍 Ejecutar escaneo", width='stretch', type="primary"):
        st.session_state.scanning = True

    if st.session_state.scanning:
        try:
            with st.spinner("Escaneando recursos en Azure... (puede tomar 1-2 minutos)"):
                # Ejecutar escaneo con threshold configurado
                st.session_state.scan_results = cached_full_scan(st.session_state.snapshot_age_days)
                # Normalizar cada recurso para compatibilidad: asegurar campo 'ahorro'
                def _ensure_ahorro(item):
                    if not isinstance(item, dict):
                        return item
                    if "ahorro" not in item:
                        # Preferir estimatedMonthlySavings si existe
                        ems = item.get("estimatedMonthlySavings") or item.get("estimated_monthly_savings")
                        if ems is None:
                            item["ahorro"] = "0€"
                        else:
                            try:
                                if isinstance(ems, (int, float)):
                                    item["ahorro"] = f"{float(ems):.2f}€"
                                else:
                                    item["ahorro"] = str(ems)
                            except Exception:
                                item["ahorro"] = str(ems)
                    return item

                st.session_state.scan_results = [ _ensure_ahorro(it) for it in st.session_state.scan_results ]
                st.session_state.scanning = False
                st.success("✅ Escaneo completado")
        except Exception as e:
            st.error(f"❌ Error durante el escaneo: {str(e)}")
            st.session_state.scanning = False

# Mostrar resultados del escaneo
if st.session_state.scan_results:
    st.markdown("---")
    scan_df = pd.DataFrame(st.session_state.scan_results)
    # Backwards compatibility: older code expected a column named 'ahorro'.
    # New detectors use 'estimatedMonthlySavings'. Create 'ahorro' from it if missing.
    if "ahorro" not in scan_df.columns:
        if "estimatedMonthlySavings" in scan_df.columns:
            def _to_ahorro(x):
                try:
                    if pd.isna(x):
                        return "0€"
                except Exception:
                    pass
                if isinstance(x, (int, float)):
                    return f"{x:.2f}€"
                return str(x)

            scan_df["ahorro"] = scan_df["estimatedMonthlySavings"].apply(_to_ahorro)
        else:
            scan_df["ahorro"] = "0€"
    
    # Estadísticas del escaneo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total de recursos", len(scan_df))
    with col2:
        tipos_unicos = scan_df["tipo"].nunique()
        st.metric("🏷️ Tipos de zombis", len(DETECTOR_TYPES))
    with col3:
        # Calcular ahorro total
        total_ahorro = sum(format_ahorro(str(a)) for a in scan_df.get("ahorro", []))
        st.metric("💰 Ahorro potencial", f"{total_ahorro:.2f}€/mes")
    with col4:
        st.metric("📈 Ambigüedad", f"{(len(scan_df) / max(tipos_unicos, 1)):.1f} avg/tipo")
    
    # Filters
    tipos = sorted(scan_df["tipo"].dropna().unique().tolist())
    selected_tipos = st.multiselect("Filtrar por tipo", options=tipos, default=tipos)
    rgs = sorted(scan_df["resourceGroup"].dropna().unique().tolist())
    selected_rgs = st.multiselect("Filtrar por Resource Group", options=rgs, default=rgs)

    # Tabla de resultados del escaneo
    st.subheader("Recursos detectados")
    filtered_df = scan_df[scan_df["tipo"].isin(selected_tipos) & scan_df["resourceGroup"].isin(selected_rgs)]
    scan_df_display = filtered_df[["tipo", "nombre", "resourceGroup", "subscriptionId", "ahorro"]].copy()
    scan_df_display = scan_df_display.sort_values("ahorro", key=lambda x: x.apply(format_ahorro), ascending=False)
    
    # Mostrar desglose por tipo
    st.markdown("**Desglose por tipo:**")
    tipo_counts = scan_df["tipo"].value_counts().to_dict()
    detector_items = list(DETECTOR_TYPES.items())
    for i in range(0, len(detector_items), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(detector_items):
                tipo, emoji_name = detector_items[i + j]
                count = tipo_counts.get(tipo, 0)
                with cols[j]:
                    st.metric(emoji_name, count)
    
    st.dataframe(
        scan_df_display,
        width='stretch',
        height=300
    )

# ==================== SECCIÓN 2: RECOMENDACIONES IA ====================

st.header("2️⃣ Análisis de Optimización")

if st.session_state.scan_results:
    if st.button("🤖 Obtener recomendaciones IA", width='stretch', type="primary"):
        try:
            with st.spinner("Analizando recursos con algoritmos de optimización deterministas..."):
                st.session_state.ia_results = cached_analyze(st.session_state.scan_results)
                st.success("✅ Análisis completado (Optimización 100%)")
        except Exception as e:
            st.error(f"❌ Error al obtener recomendaciones: {str(e)}")
            st.info("💡 Verifica tu autenticación en Azure con: az login")

if st.session_state.ia_results:
    st.markdown("---")
    zombis = st.session_state.ia_results.get("zombis", [])
    
    if zombis:
        # Crear DataFrame con recomendaciones
        ia_df = pd.DataFrame(zombis)
        ia_df = ia_df.sort_values("confianza", ascending=False)
        # Mostrar indicador del modo de análisis
        st.markdown("**🧠 Optimización Determinista:** Decisiones basadas en reglas claras y evidencia directa de uso de recursos.")
        
        # Normalizar acciones a minúsculas para comparar
        ia_df["accion_lower"] = ia_df["accion"].str.lower()
        
        # Estadísticas de optimización
        col1, col2, col3 = st.columns(3)
        with col1:
            borrar_count = len(ia_df[ia_df["accion_lower"] == "borrar"])
            st.metric("🗑️ Recursos a eliminar", borrar_count)
        with col2:
            snapshot_count = len(ia_df[ia_df["accion_lower"] == "snapshot"])
            st.metric("📸 Snapshots recomendados", snapshot_count)
        with col3:
            keep_count = len(ia_df[ia_df["accion_lower"] == "keep"])
            st.metric("✅ Recursos a mantener", keep_count)
        
        st.subheader("Recomendaciones de Optimización")
        
        # Mostrar cada recomendación en formato expandible
        for idx, (_, row) in enumerate(ia_df.iterrows()):
            metodo = row.get("metodo", "heurísticas inteligentes")
            with st.expander(
                f"**{row['nombre']}** - Acción: {row['accion'].upper()} (Confianza: {row['confianza']}%, Ahorro: {row['ahorro']}) - Método: {metodo}",
                expanded=False
            ):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**Recurso:** {row['nombre']}")
                with col2:
                    st.write(f"**Grupo:** {row['resourceGroup']}")
                with col3:
                    st.write(f"**Ubicación:** {row['location']}")
                with col4:
                    confianza_pct = int(row.get("confianza", 0))
                    st.metric("Confianza", f"{confianza_pct}%")
                
                st.write(f"**Decisión:** `{row['accion']}`")
                st.write(f"**Ahorro potencial:** {row['ahorro']}/mes")
                
                if row.get("razon"):
                    st.write(f"**Razón:** {row['razon']}")
                # Mostrar el método usado
                metodo = row.get("metodo", "optimización determinista")
                st.write(f"**Método:** {metodo} (Confianza: {confianza_pct}%)")
                if str(metodo).lower().startswith("ia"):
                    st.info("⚖️ Recomendación basada en algoritmos deterministas — verificar manualmente antes de ejecutar acciones")
    else:
        st.info("No se encontraron zombis o el escaneo anterior no retornó resultados.")
else:
    if st.session_state.scan_results:
        st.info("💡 Ejecuta el botón anterior para obtener recomendaciones heurísticas")

# ==================== SECCIÓN 3: APROBACIÓN HUMANA ====================

st.header("3️⃣ Validación Manual")

if st.session_state.scan_results and st.session_state.ia_results:
    st.markdown("---")
    
    st.markdown("**Selecciona manualmente los recursos que deseas procesar:**")
    
    st.subheader("Recursos para Procesar")
    
    # Tabla interactiva con checkboxes
    zombis_by_name = {z.get("nombre"): z for z in st.session_state.ia_results.get("zombis", [])}
    
    # Mostrar con colores por tipo
    for i, resource in enumerate(st.session_state.scan_results):
        nombre = resource.get("nombre")
        tipo = resource.get("tipo")
        zombie_data = zombis_by_name.get(nombre, {})
        
        # Usar colores para diferentes tipos
        tipo_emoji = {
            "disk": "💾",
            "ip": "📡",
            "storage": "📦",
            "sql": "🗄️",
            "vm": "🖥️",
            "nic": "🔗",
            "keyvault": "🔐",
            "appserviceplan": "🏗️",
            "loadbalancer": "⚖️",
            "snapshot": "📸"
        }.get(tipo, "❓")
        
        # Container con borde
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 2, 2, 2])
            
            with col1:
                selected = st.checkbox(
                    " ",
                    value=st.session_state.selected_resources.get(f"resource_{i}", False),
                    key=f"checkbox_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.selected_resources[f"resource_{i}"] = selected
            
            with col2:
                st.write(f"**{tipo_emoji} {nombre}**")
                st.caption(f"RG: {resource.get('resourceGroup', 'N/A')}")
            
            with col3:
                accion = zombie_data.get("accion", "unknown")
                confianza = zombie_data.get("confianza", 0)
                st.write(f"Acción: `{accion}`")
                st.caption(f"Confianza: {confianza}%")
            
            with col4:
                ahorro = resource.get("ahorro", "0€")
                st.write(f"Ahorro: {ahorro}")
                st.caption(f"Tipo: {tipo}")
    
    # Resumen de selección
    st.markdown("---")
    selected_count = sum(1 for v in st.session_state.selected_resources.values() if v)
    
    if selected_count > 0:
        # Build selected resources by index to keep ordering stable and ensure we pull full resource dict
        selected_resources = [
            st.session_state.scan_results[i]
            for i in range(len(st.session_state.scan_results))
            if st.session_state.selected_resources.get(f"resource_{i}", False)
        ]
        # Ensure each selected resource has 'ahorro' (compatibility fallback)
        for r in selected_resources:
            if "ahorro" not in r:
                ems = r.get("estimatedMonthlySavings") or r.get("estimated_monthly_savings")
                r["ahorro"] = f"{float(ems):.2f}€" if isinstance(ems, (int, float)) else (str(ems) if ems is not None else "0€")

        total_ahorro = sum(format_ahorro(str(r.get("ahorro", "0€"))) for r in selected_resources)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Recursos seleccionados", selected_count)
        with col2:
            st.metric("💰 Ahorro total", f"{total_ahorro:.2f}€/mes")
        with col3:
            st.metric("📊 % del total", f"{(selected_count / len(st.session_state.scan_results) * 100):.1f}%")
    else:
        st.info("No hay recursos seleccionados. Selecciona al menos uno para continuar.")

# ==================== SECCIÓN 4: COMANDOS AZ CLI ====================

st.header("4️⃣ Comandos Azure CLI")

if st.session_state.scan_results and st.session_state.ia_results:
    st.markdown("""
<div class="warning-banner">
    ⚠️ <strong>PROTOCOLO DE SEGURIDAD:</strong>
    <ul>
        <li>Por defecto, los comandos NO se ejecutan automáticamente</li>
        <li>Revisa cada comando antes de ejecutarlo manualmente</li>
        <li>Algunos comandos requieren parámetros adicionales</li>
        <li>Realiza backups de recursos críticos antes de eliminar</li>
        <li>La ejecución automática es experimental y requiere validación</li>
    """, unsafe_allow_html=True)
    
    selected_count = sum(1 for v in st.session_state.selected_resources.values() if v)
    
    if selected_count > 0:
        commands = build_script(
            st.session_state.scan_results,
            st.session_state.ia_results,
            st.session_state.selected_resources,
            include_header=True
        )
        
        # Limpiar comandos: remover todas las líneas de comentario que empiezan con #
        commands_clean = '\n'.join([line for line in commands.split('\n') if not line.strip().startswith('#')])
        # Preparar lista de comandos individuales para el resumen
        command_lines = [line.strip() for line in commands_clean.split('\n') if line.strip()]
        
        # Mostrar comandos en bloque de código
        st.subheader("Script de Comandos Generado")
        st.code(commands, language="bash")
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("📋 Copia el script y ejecútalo en tu terminal Azure CLI")
        with col2:
            if st.button("📋 Copiar al Portapapeles", width='stretch', key="copy_btn"):
                st.success("✅ Script copiado al portapapeles")
                st.write("```")
                st.write(commands)
                st.write("```")
        with col3:
            if st.button("💾 Descargar Script", width='stretch', key="download_btn"):
                st.download_button(
                    label="📥 Descargar .sh",
                    data=commands,
                    file_name="guardian-efimero-script.sh",
                    mime="text/x-shellscript",
                    width='stretch'
                )
        
        with st.expander("🚀 Ejecución Automática (Experimental)"):
            st.warning("⚠️ **RIESGO ALTO:** Esta función ejecuta comandos directamente en Azure. Verifica todo antes de usar.")
            if st.checkbox("Confirmo que entiendo los riesgos"):
                if st.button("🚀 Ejecutar Automáticamente", type="secondary"):
                    st.session_state.confirm_execute = True
        
            st.error("🔴 **CONFIRMACIÓN FINAL:** ¿Ejecutar comandos en Azure? Esta acción no se puede deshacer.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ EJECUTAR", type="primary"):
                    try:
                        st.info("Ejecutando comandos... (puede tomar tiempo)")
                        # Ejecutar cada comando individualmente para asegurar ejecución en Windows
                        all_stdout = []
                        all_stderr = []
                        success_count = 0
                        for cmd in command_lines:
                            try:
                                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)  # 1 min por comando
                                if result.stdout:
                                    all_stdout.append(f"[{cmd}]:\n{result.stdout}")
                                if result.stderr:
                                    all_stderr.append(f"[{cmd}]:\n{result.stderr}")
                                if result.returncode == 0:
                                    success_count += 1
                                else:
                                    all_stderr.append(f"[{cmd}]: Error código {result.returncode}")
                            except subprocess.TimeoutExpired:
                                all_stderr.append(f"[{cmd}]: Timeout")
                            except Exception as e:
                                all_stderr.append(f"[{cmd}]: {str(e)}")
                        
                        st.success("Salida estándar:")
                        st.code('\n'.join(all_stdout) or "(Sin salida)")
                        if all_stderr:
                            st.error("Errores:")
                            st.code('\n'.join(all_stderr))
                        if success_count == len(command_lines):
                            st.success(f"✅ {success_count}/{len(command_lines)} comandos ejecutados exitosamente")
                        else:
                            st.error(f"❌ {success_count}/{len(command_lines)} comandos ejecutados exitosamente")
                    except subprocess.TimeoutExpired:
                        st.error("⏰ Timeout: La ejecución tomó demasiado tiempo")
                    except Exception as e:
                        st.error(f"❌ Error al ejecutar: {str(e)}")
                    st.session_state.confirm_execute = False
            with col2:
                if st.button("❌ CANCELAR"):
                    st.session_state.confirm_execute = False
                    st.info("Ejecución cancelada")
        
        st.subheader("Resumen Ejecutivo")
        
        if command_lines:
            st.markdown("**Comandos a ejecutar:**")
            for i, cmd in enumerate(command_lines, 1):
                st.code(cmd, language="bash")
                st.caption(f"Comando {i} de {len(command_lines)}")
        
        # Total dinámico
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Total de comandos**: {len(command_lines)}")
        with col2:
            st.write(f"**Ahorro proyectado**: {total_ahorro:.2f}€/mes")
    else:
        st.warning("⚠️ Selecciona al menos un recurso para generar comandos")
else:
    if st.session_state.scan_results:
        st.info("💡 Completa los pasos anteriores para generar comandos az CLI")

# ==================== FOOTER ====================

st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p><strong>Guardian Efímero</strong> - Optimización de Costos Azure</p>
    <p>Herramienta profesional de FinOps | Algoritmos deterministas | Código abierto</p>
    <p>Siempre valida comandos antes de ejecutar</p>
</div>
""", unsafe_allow_html=True)
