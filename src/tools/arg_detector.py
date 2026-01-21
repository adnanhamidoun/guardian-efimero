#!/usr/bin/env python3
"""
Herramienta detección zombis Azure Resource Graph.
Fase 1: Discos no adjuntos + IPs públicas huérfanas
"""

import logging
from typing import List, Dict, Any
from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from rich.table import Table
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

class ARGDetector:
    def __init__(self):
        """Inicializa cliente con credenciales por defecto"""
        try:
            self.credential = DefaultAzureCredential()
            self.client = ResourceGraphClient(self.credential)
        except Exception as e:
            logger.error(f"Error ARG: {e}")
            self.credential = None
            self.client = None
    
    def detect_disks_unattached(self) -> List[Dict[str, Any]]:
        """Discos no adjuntos (top waste)"""
        if not self.client:
            return []
        
        query = """
        Resources
        | where type =~ 'microsoft.compute/disks'
        | where isnull(properties.managedBy)
        | where properties.diskState =~ 'Unattached'
        | project 
            name,
            resourceGroup,
            location,
            subscriptionId,
            tags,
            createdTime = properties.createdTime
        | order by createdTime asc
        | limit 20
        """
        try:
            response = self.client.resources(
                query, 
                query_options={"result_format": "table"}
            )
            # Devuelve lista de dicts, vacía si no hay datos
            return [r.as_dict() for r in response.data] if response.data else []
        except Exception as e:
            console.print(f"[red]ARG Error detect_disks_unattached: {e}[/red]")
            return []
    
    def detect_ips_orphaned(self) -> List[Dict[str, Any]]:
        """IPs públicas sin asociación"""
        if not self.client:
            return []
        
        query = """
        Resources
        | where type =~ 'microsoft.network/publicipaddresses'
        | where isnull(properties.ipConfiguration)
        | project 
            name,
            resourceGroup,
            location,
            subscriptionId,
            ipAddress
        | limit 20
        """
        try:
            response = self.client.resources(
                query, 
                query_options={"result_format": "table"}
            )
            return [r.as_dict() for r in response.data] if response.data else []
        except Exception as e:
            console.print(f"[red]ARG Error detect_ips_orphaned: {e}[/red]")
            return []
    
    def print_zombis(self, zombis: List[Dict[str, Any]], title: str):
        """Imprime lista de recursos o 'Ninguno' si está vacía"""
        if not zombis:
            console.print(f"[yellow]{title}: Ninguno[/yellow]\n")
            return
        
        table = Table(title=title)
        table.add_column("Nombre", style="cyan")
        table.add_column("Resource Group")
        table.add_column("Location")
        table.add_column("Sub ID")
        
        for z in zombis:
            table.add_row(
                z.get("name", "N/A"),
                z.get("resourceGroup", "N/A"),
                z.get("location", "N/A"),
                z.get("subscriptionId", "N/A")[:8] + "..." if z.get("subscriptionId") else "N/A"
            )
        console.print(table)
        console.print(f"[bold green]{len(zombis)} zombis detectados![/bold green]\n")


def main():
    console.print("[bold blue]FASE 1: LÓGICA FINOPS ACTIVA[/bold blue]\n")
    detector = ARGDetector()
    detector.print_zombis(detector.detect_disks_unattached(), " DISCOS ZOMBIS")
    detector.print_zombis(detector.detect_ips_orphaned(), " IPs HÚRFANAS")
    console.print("[dim]Siguiente: Fase 2 LLM insights → make run[/dim]")

if __name__ == "__main__":
    main()
