from rich.panel import Panel
from rich.console import Console
from tools.arg_detector import ARGDetector

console = Console()

def main():
    console.print(Panel("FASE 1: LÓGICA FINOPS ACTIVA", style="blue"))
    
    detector = ARGDetector()
    detector.print_zombis(detector.detect_disks_unattached(), " DISCOS ZOMBIS")
    detector.print_zombis(detector.detect_ips_orphaned(), " IPs HÚRFANAS")
    
    console.print("[bold green]✅ Fase 1 completa: Zombis reales detectados![/bold green]")
    console.print("[dim]Siguiente: Fase 2 LLM insights → make run[/dim]")

if __name__ == "__main__":
    main()
