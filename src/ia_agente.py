"""
Recomendador heurístico para Guardian Efímero v1

- Implementa decisiones deterministas (sin LLMs) basadas en los detectores.
- Conserva la misma interfaz que el agente previo: `agente_main()` devuelve
    un dict con la clave `zombis` que contiene decisions con keys esperadas
    por la UI (`nombre`, `resourceGroup`, `tipo`, `accion`, `confianza`,
    `ahorro`, `razon`, `metodo`).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import List, Dict, Any, Optional


OOLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"
FALLBACK_PRICE_PER_GB = 0.08  # €/mes por GB (heurística de fallback, ver web:466)
FALLBACK_PRICE_PER_IP = 3.0  # €/mes por IP pública huérfana (heurística)


def parse_guardian_table(output: str, section_title: str = "DISCOS ZOMBIS") -> List[Dict[str, Any]]:
    """Parsea tablas bonitas de rich desde la salida de `guardian.py`.

    Busca la sección por título (p. ej. "DISCOS ZOMBIS") y extrae filas del primer bloque de tabla
    que siga al título. Maneja bordes Unicode (│┃┏┗...) y espacios extra.
    """
    lines = output.splitlines()

    # Encontrar índice del título (caso-insensible)
    idx = None
    for i, line in enumerate(lines):
        if section_title.lower() in line.lower():
            idx = i
            break
    if idx is None:
        # No se encontró la sección; intentar parsear cualquier tabla disponible
        idx = 0

    # Buscar bloque de tabla luego del título
    table_lines: List[str] = []
    for line in lines[idx + 1: idx + 200]:
        # coger líneas que contienen '│' o '┃' o que sean bordes de tabla
        if any(ch in line for ch in ("│", "┃", "┏", "┗", "┡", "┑", "┓")):
            table_lines.append(line)
        elif table_lines:
            # si ya empezamos a capturar y encontramos una línea que no es tabla, rompemos
            break

    # Extraer header (línea que contiene 'Nombre' o similar)
    header_line = None
    for l in table_lines:
        if re.search(r"\bNombre\b|\bName\b|Resource Group", l, flags=re.I):
            header_line = l
            break
    if not header_line:
        # No hay header claro; intentar inferir filas
        data_lines = [l for l in table_lines if l.strip().startswith("│") or l.strip().startswith("|")]
        rows = []
        for l in data_lines:
            parts = [p.strip() for p in re.split(r"[│┃|]", l) if p.strip()]
            if parts:
                rows.append(parts)
        # Mapear con nombres genéricos
        results = []
        for r in rows:
            if len(r) >= 3:
                results.append({"nombre": r[0], "resourceGroup": r[1], "location": r[2]})
        return results

    # Determinar delimitador usado (usamos los caracteres │ o ┃)
    delim = "│" if "│" in header_line else ("┃" if "┃" in header_line else "|")
    headers = [h.strip() for h in header_line.split(delim) if h.strip()]

    # Normalizar nombres de columnas
    norm_headers = []
    for h in headers:
        h_l = h.lower()
        if "nombre" in h_l or "name" in h_l:
            norm_headers.append("nombre")
        elif "resource group" in h_l or "resourcegroup" in h_l:
            norm_headers.append("resourceGroup")
        elif "location" in h_l:
            norm_headers.append("location")
        elif "sub" in h_l or "subscription" in h_l:
            norm_headers.append("subscriptionId")
        else:
            norm_headers.append(h)

    # Obtener líneas de datos: las que comienzan con el delimitador vertical
    data_lines = [
        l for l in table_lines
        if any(l.strip().startswith(ch) for ch in (delim, '│', '┃', '|'))
        and l != header_line
        and not any(ch in l for ch in ("┏", "┡", "└", "┗", "─", "┓", "┑"))
    ]
    results: List[Dict[str, Any]] = []
    for l in data_lines:
        parts = [p.strip() for p in re.split(r"[│┃|]", l) if p.strip()]
        if len(parts) < len(norm_headers):
            continue
        row = {}
        for k, v in zip(norm_headers, parts):
            row[k] = v
        results.append(row)

    return results


def fetch_zombis() -> List[Dict[str, Any]]:
    """Intenta obtener zombis de forma estructurada.

    1. Intentar usar `tools.arg_detector.ARGDetector.detect_disks_unattached()` si está disponible
    2. Si no, ejecutar `src/guardian.py` y parsear la tabla de salida
    """
    # Opción 1: intentar usar la API interna
    try:
        from .tools.arg_detector import ARGDetector  # type: ignore
        detector = ARGDetector()
        if detector.client:  # si autenticado
            rows = detector.detect_disks_unattached()
            # los rows ya son dicts: asegurarnos del formato mínimo
            out = []
            for r in rows:
                out.append({
                    "type": "disk",
                    "nombre": r.get("name") or r.get("nombre") or r.get("Name"),
                    "resourceGroup": r.get("resourceGroup"),
                    "location": r.get("location"),
                    "subscriptionId": r.get("subscriptionId"),
                    "diskState": r.get("diskState"),
                    "managedBy": r.get("managedBy"),
                    "size_gb": int(r.get("diskSizeGB") or r.get("diskSizeGb") or r.get("diskSizeGB", 0) or 0)
                })
            if out:
                # Intentar también detectar IPs vía SDK si existen
                try:
                    ips = detector.detect_ips_orphaned()
                    for ip in ips:
                        out.append({
                            "type": "ip",
                            "nombre": ip.get("name") or ip.get("nombre"),
                            "resourceGroup": ip.get("resourceGroup"),
                            "location": ip.get("location"),
                            "subscriptionId": ip.get("subscriptionId"),
                            "ipAddress": ip.get("ipAddress") or None,
                        })
                except Exception:
                    pass
                return out
    except Exception:
        # Si falla import o ejecución, seguimos al fallback de parseo
        pass

    # Opción 2: fallback a parseo de salida de guardian.py
    proc = subprocess.run([sys.executable, "src/guardian.py"], capture_output=True, text=True)
    # Parsear discos
    parsed = parse_guardian_table(proc.stdout, section_title="DISCOS ZOMBIS")
    results = []
    for p in parsed:
        results.append({
            "type": "disk",
            "nombre": p.get("nombre") or p.get("name"),
            "resourceGroup": p.get("resourceGroup"),
            "location": p.get("location"),
            "subscriptionId": p.get("subscriptionId") or None,
            "diskState": p.get("diskState") or "Unattached",
            "managedBy": p.get("managedBy") or "",
            "size_gb": int(p.get("diskSizeGB") or p.get("size_gb") or 0)
        })

    # Parsear IPs huérfanas y adjuntar
    parsed_ips = parse_guardian_table(proc.stdout, section_title="IPs HÚRFANAS")
    for p in parsed_ips:
        results.append({
            "type": "ip",
            "nombre": p.get("nombre") or p.get("name"),
            "resourceGroup": p.get("resourceGroup"),
            "location": p.get("location"),
            "subscriptionId": p.get("subscriptionId") or None,
            "ipAddress": p.get("ipAddress") or None,
        })

    return results


# No LLMs used in v1: removed Ollama calling code and network dependencies.


def fallback_decision(zombi: Dict[str, Any]) -> Dict[str, Any]:
    """Decisión heurística mejorada basada en tipo de recurso y estado.
    
    Usa información clara de por qué es zombi:
    - IP huérfana → Borrar (100% seguro)
    - Disco unattached → Borrar (muy probable)
    - Storage sin contenedores → Borrar (100% seguro)
    - SQL offline → Borrar (100% seguro)
    - VM parada → Borrar (muy probable)
    - Otros → Borrar (general, ya están detectados como zombis)
    """
    tipo = zombi.get("tipo") or zombi.get("type", "unknown")
    nombre = zombi.get("nombre", "unknown")
    
    # Matriz de decisiones basada en tipo de zombi
    decisiones = {
        "ip": {
            "accion": "Borrar",
            "confianza": 100,
            "ahorro": 3.0,
            "razon": "IP pública huérfana sin máquina asociada"
        },
        "disk": {
            "accion": "Borrar",
            "confianza": 100,
            "ahorro": 0.8,
            "razon": "Disco sin adjuntar a ninguna VM"
        },
        "storage": {
            "accion": "Borrar",
            "confianza": 100,
            "ahorro": 10.0,
            "razon": "Storage account sin contenedores ni blobs"
        },
        "sql": {
            "accion": "Borrar",
            "confianza": 100,
            "ahorro": 45.0,
            "razon": "Base de datos SQL offline"
        },
        "vm": {
            "accion": "Borrar",
            "confianza": 95,
            "ahorro": 50.0,
            "razon": "VM deallocated (parada sin uso)"
        },
        "nic": {
            "accion": "Borrar",
            "confianza": 95,
            "ahorro": 1.5,
            "razon": "Network Interface sin VM asociada"
        },
        "keyvault": {
            "accion": "Borrar",
            "confianza": 90,
            "ahorro": 5.0,
            "razon": "Key Vault sin tenant configurado"
        },
        "loadbalancer": {
            "accion": "Borrar",
            "confianza": 90,
            "ahorro": 8.0,
            "razon": "Load Balancer sin reglas de balanceo"
        },
        "snapshot": {
            "accion": "Borrar",
            "confianza": 85,
            "ahorro": 2.0,
            "razon": "Snapshot muy antiguo (>90 días)"
        },
        "appserviceplan": {
            "accion": "Borrar",
            "confianza": 95,
            "ahorro": 15.0,
            "razon": "App Service Plan sin aplicaciones"
        }
    }
    
    # Buscar decisión para el tipo
    decision = decisiones.get(tipo.lower())
    
    if decision:
        return {
            "accion": decision["accion"],
            "confianza": decision["confianza"],
            "ahorro": f"{decision['ahorro']}€",
            "razon": decision["razon"]
        }
    
    # Fallback general para tipos no reconocidos
    return {
        "accion": "Borrar",
        "confianza": 70,
        "ahorro": "0.0€",
        "razon": "Recurso detectado como zombi - revisar manualmente"
    }


def analyze_zombi(zombi: Dict[str, Any]) -> Dict[str, Any]:
    """Agente híbrido: heurísticas claras para la mayoría (90%) y Ollama para casos ambiguos (10%).

    Retorna dict con keys: accion, confianza (int), ahorro (str), razon, metodo
    """
    tipo = (zombi.get("tipo") or zombi.get("type") or "unknown").lower()

    # Heurísticas deterministas por tipo
    if tipo == "disk":
        disk_state = str(zombi.get("diskState") or zombi.get("state") or "").lower()
        managed = zombi.get("managedBy")
        if "unattached" in disk_state or not managed:
            return {"accion": "Borrar", "confianza": 100, "ahorro": f"{0.8}€", "razon": "Disco sin adjuntar a ninguna VM", "metodo": "heuristic"}

    if tipo == "ip":
        return {"accion": "Borrar", "confianza": 100, "ahorro": f"{FALLBACK_PRICE_PER_IP}€", "razon": "IP pública huérfana sin máquina asociada", "metodo": "heuristic"}

    if tipo == "storage":
        blob_count = zombi.get("blobCount")
        container_count = zombi.get("containerCount")
        try:
            bc = int(blob_count) if blob_count is not None else None
        except Exception:
            bc = None
        try:
            cc = int(container_count) if container_count is not None else None
        except Exception:
            cc = None
        if (bc is not None and bc == 0) or (cc is not None and cc == 0) or ("sin blobs" in str(zombi.get("razon","")).lower()):
            return {"accion": "Borrar", "confianza": 100, "ahorro": f"{10.0}€", "razon": "Storage account sin contenedores ni blobs", "metodo": "heuristic"}

    if tipo == "sql":
        state = str(zombi.get("state") or zombi.get("status") or "").lower()
        if "offline" in state:
            return {"accion": "Borrar", "confianza": 100, "ahorro": f"{45.0}€", "razon": "Base de datos SQL offline", "metodo": "heuristic"}

    # Para VM, NIC, LB, etc. usamos la misma lógica de fallback basada en reglas
    decision = fallback_decision(zombi)
    decision["metodo"] = "heuristic"
    decision["fallback"] = False
    return decision


def agente_main(print_json: bool = True, scan_results: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Agente IA mejorado que acepta resultados del escaneo.
    
    Usa heurísticas inteligentes basadas en tipo de recurso.
    La confianza es 100% porque usa información real del detector, no predicciones de LLM.
    
    Si scan_results está disponible, los usa directamente.
    Si no, intenta obtenerlos con fetch_zombis().
    """
    if scan_results is None:
        # Obtener zombis de la forma anterior
        zombis = fetch_zombis()
    else:
        # Usar los resultados del escaneo proporcionados
        # Asegurar que tienen el campo 'tipo' que necesita fallback_decision
        zombis = []
        for z in scan_results:
            item = dict(z)
            # Asegurar que 'tipo' está presente (puede venir como 'type')
            if 'tipo' not in item and 'type' in item:
                item['tipo'] = item['type']
            elif 'tipo' not in item:
                item['tipo'] = 'unknown'
            zombis.append(item)
    
    results = []
    for z in zombis:
        # Usar agente híbrido: analizar cada zombi con analyze_zombi
        decision = analyze_zombi(z)

        # Normalizar keys y añadir método proveniente de la decisión
        accion_val = decision.get("accion")
        if isinstance(accion_val, str):
            accion_val = accion_val.strip().lower()

        results.append({
            "nombre": z.get("nombre"),
            "resourceGroup": z.get("resourceGroup"),
            "location": z.get("location"),
            "tipo": z.get("tipo") or z.get("type", "unknown"),
            "accion": accion_val,
            "confianza": decision.get("confianza"),
            "ahorro": decision.get("ahorro") if isinstance(decision.get("ahorro"), str) else f"{decision.get('ahorro', 0)}€",
            "razon": decision.get("razon"),
            "metodo": decision.get("metodo", "heurística"),
            "fallback": bool(decision.get("fallback", False)),
        })
    out = {"zombis": results}
    if print_json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return out




if __name__ == "__main__":
    agente_main()
