#!/usr/bin/env python
"""
Script de verificación para Guardian Efímero
Verifica que todo está bien configurado antes de ejecutar Streamlit
"""

import sys
import importlib
import os

def check_imports():
    """Verifica que todos los módulos necesarios se pueden importar"""
    print("🔍 Verificando importaciones...")
    print()
    
    required_modules = {
        "streamlit": "Streamlit (UI)",
        "pandas": "Pandas (Data)",
        "requests": "Requests (HTTP)",
        "rich": "Rich (Formatting)",
        "azure.identity": "Azure Identity",
        "azure.mgmt.resourcegraph": "Azure Resource Graph",
        "dotenv": "Python Dotenv",
    }
    
    errors = []
    for module_name, description in required_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {description:.<40} OK")
        except ImportError as e:
            print(f"  ❌ {description:.<40} MISSING")
            errors.append((module_name, str(e)))
    
    print()
    return errors

def check_project_structure():
    """Verifica que la estructura del proyecto es correcta"""
    print("🏗️  Verificando estructura del proyecto...")
    print()
    
    required_files = {
        "app.py": "Aplicación Streamlit",
        "src/__init__.py": "Paquete src",
        "src/detectores.py": "Detectores",
        "src/ia_agente.py": "Agente IA",
        "src/cli_generator.py": "Generador CLI",
        "src/tools/__init__.py": "Paquete tools",
        "src/tools/arg_detector.py": "Detector de Azure",
    }
    
    errors = []
    for file_path, description in required_files.items():
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"  ✅ {description:.<40} {file_path}")
        else:
            print(f"  ❌ {description:.<40} MISSING: {file_path}")
            errors.append((file_path, "Archivo no encontrado"))
    
    print()
    return errors

def check_imports_internal():
    """Verifica que los módulos internos se pueden importar correctamente"""
    print("🔗 Verificando importaciones internas...")
    print()
    
    try:
        print("  Importando src.detectores...", end=" ")
        from src.detectores import full_scan
        print("✅ OK")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return [("src.detectores", str(e))]
    
    try:
        print("  Importando src.ia_agente...", end=" ")
        from src.ia_agente import agente_main
        print("✅ OK")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return [("src.ia_agente", str(e))]
    
    try:
        print("  Importando src.cli_generator...", end=" ")
        from src.cli_generator import generate_az_command
        print("✅ OK")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return [("src.cli_generator", str(e))]
    
    print()
    return []

def main():
    """Función principal de verificación"""
    print("=" * 60)
    print("🛡️  Guardian Efímero - Verification Script")
    print("=" * 60)
    print()
    
    all_errors = []
    
    # Verificar importaciones
    errors = check_imports()
    all_errors.extend(errors)
    
    # Verificar estructura
    errors = check_project_structure()
    all_errors.extend(errors)
    
    # Verificar importaciones internas
    errors = check_imports_internal()
    all_errors.extend(errors)
    
    # Resumen
    print("=" * 60)
    if all_errors:
        print(f"❌ FAILED: {len(all_errors)} error(s) encontrado(s)")
        print()
        print("Errores:")
        for item, error in all_errors:
            print(f"  • {item}: {error}")
        print()
        print("Solución:")
        print("  1. Lee FIX_DEPENDENCIES.md")
        print("  2. Ejecuta: python install_dependencies.py")
        print("  3. Luego: streamlit run app.py")
        return 1
    else:
        print("✅ SUCCESS: ¡Todo está bien configurado!")
        print()
        print("Próximo paso:")
        print("  streamlit run app.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
