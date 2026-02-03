#!/usr/bin/env python3
"""
Herramienta detección zombis Azure Resource Graph.
Fase 1: Discos no adjuntos + IPs públicas huérfanas
"""

import logging
from typing import List, Dict, Any

from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest
from rich.table import Table
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class ARGDetector:
    def __init__(self):
        """Inicializa cliente con credenciales por defecto."""
        try:
            self.credential = DefaultAzureCredential()
            self.client = ResourceGraphClient(self.credential)
        except Exception as e:
            # Log con etiqueta fija para tests
            logger.error(f"Error ARG: Error inicializando ARG: {e}")
            self.credential = None
            self.client = None

    # ---------- helper interno para evitar deserialización rara ----------

    def _run_query(self, kql: str) -> List[Dict[str, Any]]:
        """Ejecuta una query de Resource Graph y devuelve lista de dicts.

        Intenta usar el SDK; si no devuelve filas (o falla), hace fallback a `az graph query`.
        """
        if not self.client:
            # Si no hay cliente (p. ej. error de autenticación al inicializar DefaultAzureCredential),
            # no hacemos llamadas externas ni fallback — devolvemos vacío y dejamos que el caller maneje.
            return []

        request = QueryRequest(
            query=kql,
            options={"result_format": "table"},
        )

        try:
            response = self.client.resources(request)
            data = response.data
            # Si hay filas, parseamos y devolvemos
            if getattr(data, "rows", None):
                columns = [c.name for c in data.columns]
                resultados: List[Dict[str, Any]] = []
                for row in data.rows:
                    item = {col: val for col, val in zip(columns, row)}
                    resultados.append(item)
                return resultados
        except Exception as e:
            console.print(f"[yellow]SDK ARG warning: {e} — intentar fallback con az CLI[/yellow]")

        # --- fallback con Azure CLI ---
        try:
            import subprocess
            import json
            import shutil
            az_exe = shutil.which('az') or shutil.which('az.cmd')
            # Compactar la query para evitar problemas de parsing por newlines al pasar argumentos
            kql_compact = " ".join([line.strip() for line in kql.splitlines() if line.strip()])
            if az_exe:
                proc = subprocess.run([az_exe, "graph", "query", "-q", kql_compact, "-o", "json"], capture_output=True, text=True, check=True)
            else:
                # último recurso usar shell=True (PowerShell) para resolver el comando
                proc = subprocess.run("az graph query -q \"" + kql_compact.replace('"','\"') + "\" -o json", capture_output=True, text=True, check=True, shell=True)
            out = proc.stdout
            parsed = json.loads(out)
            # la CLI devuelve {'count':..., 'data': [...]}
            data_list = parsed.get("data") if isinstance(parsed, dict) else parsed
            if isinstance(data_list, list):
                return data_list
        except Exception as e:
            console.print(f"[red]Fallback az error: {e}[/red]")

        # No hay resultados
        return []

    # --------------------- detección de recursos -------------------------

    def detect_disks_unattached(self) -> List[Dict[str, Any]]:
        """Discos no adjuntos (top waste). Más permisiva y robusta contra nulos/case."""
        query = """
resources
| where type == "microsoft.compute/disks"
| extend diskState = tostring(properties.diskState)
| where tolower(diskState) == "unattached" or isempty(tostring(managedBy)) or tostring(managedBy) == ""
| project 
    name,
    resourceGroup,
    location,
    subscriptionId,
    diskState,
    managedBy,
    diskSizeGB = tostring(properties.diskSizeGB),
    timeCreated = tostring(properties.timeCreated)
| order by timeCreated asc
| limit 20
"""
        return self._run_query(query)

    def detect_disk_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Devuelve información completa de un disco por nombre (uso para depuración).

        Usa `_run_query` (incluye fallback con `az`) para obtener el recurso.
        """
        query = f"""
resources
| where name =~ '{name}'
| project name, type, resourceGroup, location, subscriptionId, diskState = tostring(properties.diskState), managedBy, properties
| limit 10
"""
        # `_run_query` ya hace fallback a 'az' si el SDK no devuelve datos
        return self._run_query(query)

    def detect_ips_orphaned(self) -> List[Dict[str, Any]]:
        """IPs públicas sin asociación."""
        query = """
resources
| where type == "microsoft.network/publicipaddresses"
| where isnull(properties.ipConfiguration) or tostring(properties.ipConfiguration) == ""
| project 
    name,
    resourceGroup,
    location,
    subscriptionId,
    sku = tostring(sku.name),
    ipAddress = tostring(properties.ipAddress)
| limit 20
"""
        return self._run_query(query)


    # ----------------------------- salida --------------------------------

    def print_zombis(self, zombis: List[Dict[str, Any]], title: str):
        """Imprime lista de recursos o 'Ninguno' si está vacía."""
        if not zombis:
            console.print(f"[yellow]{title}: Ninguno[/yellow]\n")
            return

        table = Table(title=title)
        table.add_column("Nombre", style="cyan")
        table.add_column("Resource Group")
        table.add_column("Location")
        table.add_column("Sub ID")

        for z in zombis:
            sub = z.get("subscriptionId") or "N/A"
            if isinstance(sub, str) and len(sub) > 8:
                sub = sub[:8] + "..."
            table.add_row(
                str(z.get("name", "N/A")),
                str(z.get("resourceGroup", "N/A")),
                str(z.get("location", "N/A")),
                sub,
            )

        console.print(table)
        console.print(f"[bold green]{len(zombis)} zombis detectados![/bold green]\n")


def main():
    console.print("[bold blue]FASE 1: LÓGICA FINOPS ACTIVA[/bold blue]\n")

    detector = ARGDetector()
    detector.print_zombis(
        detector.detect_disks_unattached(),
        "🧟 DISCOS ZOMBIS",
    )
    detector.print_zombis(
        detector.detect_ips_orphaned(),
        "🌐 IPs HÚRFANAS",
    )

    console.print("[bold green]✅ Fase 1 completa: Lógica FinOps limpia[/bold green]")
    console.print("[dim]Siguiente: Fase 2 LLM insights → explicar zombis[/dim]")


if __name__ == "__main__":
    main()
