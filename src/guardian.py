#!/usr/bin/env python3
"""
El Guardián Efímero v0.1.0
Fase 0 completa 
"""

from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold green]Ejecutable desde día 1 → demo clase[/bold green]",
        title="Estado MVP",
        border_style="green"
    ))
    console.input("\n[bold]Presiona Enter para continuar → Fase 1...[/bold]")

if __name__ == "__main__":
    main()
