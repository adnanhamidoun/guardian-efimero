"""
Agente IA para Guardian Efímero — Fase 2
- Intenta usar directamente las funciones de Fase1 (si están disponibles)
- Si no, parsea la salida de `src/guardian.py` (tabla) de forma robusta
- Llama a Ollama en localhost:11434, y si falla hace un fallback heurístico
- Devuelve JSON estructurado: {"zombis": [{nombre, accion, confianza, ahorro}]}
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import List, Dict, Any, Optional

import requests


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
        from tools.arg_detector import ARGDetector  # type: ignore
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


def call_ollama(zombi: Dict[str, Any], timeout: int = 45) -> Optional[Dict[str, Any]]:
    """Llama a Ollama y devuelve dict (o None si hubo fallo de red o formato inesperado)."""
    prompt = (
        f"Analiza este disco zombi para FinOps y responde solo JSON con keys: accion, confianza, razon, ahorro.\n"
        f"disco: {zombi.get('nombre')}, size_gb: {zombi.get('size_gb')}, rg: {zombi.get('resourceGroup')}, location: {zombi.get('location')}"
    )
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "format": "json", "stream": False}
    try:
        r = requests.post(OOLLAMA_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        body = r.json()

        # Debug breve (no ruidoso) — útil al depurar localmente
        # print(f"Ollama response body: {body}")

        # Algunos endpoints devuelven {'response': '<json-as-string>'}
        parsed = None
        if isinstance(body, dict) and "response" in body:
            resp = body["response"]
            if isinstance(resp, str):
                try:
                    parsed = json.loads(resp)
                except Exception:
                    parsed = None
            elif isinstance(resp, dict):
                parsed = resp
        elif isinstance(body, dict):
            # Si ya tiene las keys esperadas, acéptalo
            parsed = body if any(k in body for k in ("accion", "confianza", "ahorro", "razon")) else None

        # Validar estructura mínima: accion + confianza
        if not parsed or not isinstance(parsed, dict):
            return None

        accion = parsed.get("accion")
        confianza = parsed.get("confianza")
        # chequeos de tipo/bounds
        if not isinstance(accion, str) or accion.strip() == "":
            return None
        if not (isinstance(confianza, int) or (isinstance(confianza, float) and confianza.is_integer())):
            # intentar convertir
            try:
                confianza = int(confianza)
            except Exception:
                return None

        # Normalizar y devolver
        parsed["accion"] = accion.strip()
        parsed["confianza"] = int(confianza)
        return parsed
    except Exception:
        return None


def fallback_decision(zombi: Dict[str, Any]) -> Dict[str, Any]:
    """Decisión heurística cuando Ollama no está disponible.

    Basada en tamaño y estado: discos unattached grandes => borrar, medianos => snapshot, pequeños => keep.
    Calcula ahorro aproximado usando FALLBACK_PRICE_PER_GB.
    """
    # Si es IP, usar heurística de coste por IP
    if zombi.get("type") == "ip":
        accion = "borrar"
        confianza = 6
        ahorro = round(FALLBACK_PRICE_PER_IP, 2)
        return {"accion": accion, "confianza": confianza, "ahorro": f"{ahorro}€", "razon": "Heurística local: coste por IP pública"}

    size = int(zombi.get("size_gb") or 0)
    if size >= 30:
        accion = "borrar"
        confianza = 8
    elif size >= 10:
        accion = "snapshot"
        confianza = 6
    else:
        accion = "keep"
        confianza = 4
    ahorro = round(size * FALLBACK_PRICE_PER_GB, 2)
    return {"accion": accion, "confianza": confianza, "ahorro": f"{ahorro}€", "razon": "Heurística local: coste por GB"}


def agente_main(print_json: bool = True) -> Dict[str, Any]:
    zombis = fetch_zombis()
    results = []
    for z in zombis:
        decision = call_ollama(z)
        if decision is None:
            decision = fallback_decision(z)
            decision["fallback"] = True
        else:
            decision["fallback"] = False
        # Normalizar keys
        results.append({
            "nombre": z.get("nombre"),
            "resourceGroup": z.get("resourceGroup"),
            "location": z.get("location"),
            "accion": decision.get("accion"),
            "confianza": decision.get("confianza"),
            "ahorro": decision.get("ahorro"),
            "razon": decision.get("razon"),
            "fallback": decision.get("fallback", False),
        })
    out = {"zombis": results}
    if print_json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


if __name__ == "__main__":
    agente_main()
