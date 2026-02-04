"""
Módulo auxiliar: Generador de comandos az CLI

Proporciona funciones para convertir recursos detectados en comandos
de Azure CLI listos para ejecutar.

Uso:
    from src.cli_generator import generate_az_command, build_script
    cmd = generate_az_command(resource, "delete")
    script = build_script([resource1, resource2], ia_results, selected)
"""

from typing import List, Dict, Any


def generate_az_command(resource: Dict[str, Any], action: str) -> str:
    """
    Genera un comando az CLI basado en el tipo de recurso y la acción sugerida.
    
    Esta función es la base para generar comandos de Azure CLI de forma estructurada.
    
    Args:
        resource: Dict con información del recurso (tipo, id, resourceGroup, nombre)
                  Campos esperados:
                    - tipo: str - Tipo de recurso (disk, ip, sql, vm, etc.)
                    - nombre: str - Nombre del recurso
                    - resourceGroup: str - Grupo de recursos
                    - location: str (opcional) - Ubicación
                    
        action: str - Acción sugerida (borrar, snapshot, keep, etc.)
    
    Returns:
        str: Comando az CLI formateado, o comentario si no es posible generarlo
        
    Ejemplos:
        >>> generate_az_command({"tipo": "disk", "nombre": "d1", "resourceGroup": "rg1"}, "delete")
        "az disk delete --resource-group 'rg1' --name 'd1' --yes"
        
        >>> generate_az_command({"tipo": "disk", "nombre": "d1", "resourceGroup": "rg1"}, "snapshot")
        "az snapshot create --resource-group 'rg1' --name 'd1-snapshot' --source 'd1'"
    """
    tipo = resource.get("tipo", "").lower()
    rg = resource.get("resourceGroup", "")
    nombre = resource.get("nombre", "")
    
    # Si no hay información suficiente, devolver comando genérico
    if not rg or not nombre:
        return f"# Falta información para generar comando: {nombre}"
    
    # Mapeo de acciones y tipos a comandos az CLI
    if action.lower() == "borrar" or action.lower() == "delete":
        if tipo == "disk":
            return f"az disk delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "ip":
            return f"az network public-ip delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "sql":
            # SQL database: az sql db delete
            # Nota: requiere --server <server-name>
            return f"az sql db delete --resource-group '{rg}' --server <server-name> --name '{nombre}' --yes"
        elif tipo == "vm":
            return f"az vm delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "storage":
            return f"az storage account delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "appserviceplan":
            return f"az appservice plan delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "nic":
            return f"az network nic delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "keyvault":
            return f"az keyvault delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "loadbalancer":
            return f"az network lb delete --resource-group '{rg}' --name '{nombre}' --yes"
        elif tipo == "snapshot":
            return f"az snapshot delete --resource-group '{rg}' --name '{nombre}' --yes"
        else:
            return f"az resource delete --ids <resource-id> --yes"
    
    elif action.lower() == "snapshot":
        # Crear snapshot de un disco
        if tipo == "disk":
            return f"az snapshot create --resource-group '{rg}' --name '{nombre}-snapshot' --source '{nombre}'"
        else:
            return f"# Snapshot no disponible para tipo: {tipo}"
    
    elif action.lower() == "keep":
        # No hacer nada
        return f"# Conservar recurso: {nombre}"
    
    else:
        return f"# Acción no reconocida: {action}"


def build_script(
    scan_results: List[Dict[str, Any]],
    ia_results: Dict[str, Any],
    selected: Dict[str, bool],
    include_header: bool = True
) -> str:
    """
    Construye un script bash completo con los comandos az CLI seleccionados.
    
    Esta función toma los resultados del escaneo, las recomendaciones del agente IA,
    y la selección del usuario para generar un script bash listo para ejecutar.
    
    Args:
        scan_results: List[Dict] - Resultados del escaneo de recursos
        ia_results: Dict - Resultados del agente IA con recomendaciones
        selected: Dict[str, bool] - Mapping resource_id -> bool indicando selección
        include_header: bool - Si incluir header y comentarios de seguridad (default: True)
    
    Returns:
        str: Script bash formateado, listo para copiar y ejecutar
        
    Notas:
        - El script NO se ejecuta automáticamente
        - El usuario debe revisar manualmente antes de ejecutar
        - Algunos comandos pueden requerir parámetros adicionales
    """
    commands = []
    
    if include_header:
        commands.append("#!/bin/bash")
        commands.append("# Comandos generados por Guardian Efímero")
        commands.append("# ADVERTENCIA: Ejecuta estos comandos bajo tu responsabilidad")
        commands.append("# ANTES DE EJECUTAR: revisa cada comando y realiza copias de seguridad")
        commands.append("# Algunos comandos pueden requerir parámetros adicionales")
        commands.append("")
    
    # Mapeo: nombre de recurso -> datos del agente IA
    zombis_by_name = {z.get("nombre"): z for z in ia_results.get("zombis", [])}
    
    selected_count = 0
    for i, resource in enumerate(scan_results):
        if selected.get(f"resource_{i}", False):
            nombre = resource.get("nombre")
            zombie_data = zombis_by_name.get(nombre, {})
            action = zombie_data.get("accion", "keep")
            
            cmd = generate_az_command(resource, action)
            if cmd and not cmd.startswith("#"):
                commands.append(cmd)
                selected_count += 1
            else:
                commands.append(cmd)
    
    commands.append("")
    commands.append(f"# Total de recursos a procesar: {selected_count}")
    
    return "\n".join(commands)


def generate_resource_summary(resource: Dict[str, Any], ia_data: Dict[str, Any] = None) -> str:
    """
    Genera un resumen textual de un recurso con su recomendación IA.
    
    Útil para logueo, reportes, o interfaces.
    
    Args:
        resource: Dict - Datos del recurso
        ia_data: Dict (opcional) - Recomendación del agente IA
        
    Returns:
        str: Resumen formateado
    """
    nombre = resource.get("nombre", "desconocido")
    tipo = resource.get("tipo", "desconocido")
    rg = resource.get("resourceGroup", "desconocido")
    ahorro = resource.get("ahorro", "0€")
    
    summary = f"{tipo.upper()}: {nombre}\n"
    summary += f"  Grupo: {rg}\n"
    summary += f"  Ahorro: {ahorro}\n"
    
    if ia_data:
        action = ia_data.get("accion", "unknown")
        confidence = ia_data.get("confianza", 0)
        reason = ia_data.get("razon", "")
        
        summary += f"  Acción: {action} (Confianza: {confidence}%)\n"
        if reason:
            summary += f"  Razón: {reason}\n"
    
    return summary
