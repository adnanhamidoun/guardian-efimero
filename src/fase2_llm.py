import requests
import subprocess
import re
import json
import sys

def fase1_zombis():
    result = subprocess.run([sys.executable, "src/guardian.py"], capture_output=True, text=True)
    # Regex tu tabla EXACTA
    discos = re.findall(r'│\s*(\w+-\w+)\s*│\s*hamidounelhabtiadnan\s*│', result.stdout)
    return [{"nombre": d, "rg": "hamidounelhabtiadnan", "size_gb": 30, "location": "westeurope"} for d in discos]

def ollama_ia(zombi):
    prompt = f"""Azure FinOps agente real:
Disco: {zombi['nombre']} ({zombi['size_gb']}GB)
RG: {zombi['rg']}
Coste: 2.4€/mes [web:466]

3 opciones (delete/snapshot/keep):
1. [ACCIÓN] - Pros: X Cons: Y"""
    
    resp = requests.post('http://localhost:11434/api/generate', 
        json={"model": "llama3.1", "prompt": prompt, "stream": False},
        timeout=30)
    return resp.json()['response']

print("🧠 IA_AGENTE: Fase1 + Ollama real")
zombis = fase1_zombis()
if zombis:
    for zombi in zombis:
        print(f"\n📊 Zombi: {zombi['nombre']}")
        print(ollama_ia(zombi))
else:
    print("No zombis. Crea: az disk create ...")

print("✅ Dinámico!")
