#!/usr/bin/env python
"""
Script de instalación limpia para Guardian Efímero
Instala las dependencias necesarias sin conflictos
"""

import subprocess
import sys

# Paquetes necesarios
PACKAGES = [
    "azure-identity==1.25.1",
    "azure-mgmt-resourcegraph==8.0.1",
    "azure-mgmt-costmanagement==4.0.1",
    "pandas==2.3.3",
    "rich==14.2.0",
    "python-dotenv==1.2.1",
    "requests==2.32.5",
    "streamlit==1.41.1",
    "langchain-community==0.4.1",
    "langchain-ollama==1.0.1",
    "ollama==0.6.1",
    "pytest==7.4.4",
    "duckdb==1.4.3",
]

def install_packages():
    """Instala los paquetes de forma ordenada"""
    print("🛡️  Guardian Efímero - Clean Installation")
    print("=" * 50)
    print()
    
    # Actualizar pip
    print("1️⃣  Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    print()
    
    # Instalar paquetes
    print("2️⃣  Installing dependencies...")
    for i, package in enumerate(PACKAGES, 1):
        print(f"  [{i}/{len(PACKAGES)}] Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"    ⚠️  Warning: Failed to install {package}")
            print(f"       Error: {e}")
            continue
    
    print()
    print("✅ Dependencies installed")
    print()
    
    # Verificar instalación
    print("3️⃣  Verifying installation...")
    try:
        import streamlit
        import pandas
        import azure.identity
        import requests
        print("✅ All packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print()
    print("🎉 Installation complete!")
    print()
    print("Next steps:")
    print("1. Verify Azure login: az login")
    print("2. Run: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    try:
        success = install_packages()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
