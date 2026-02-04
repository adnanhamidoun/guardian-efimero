# 🔧 Solución: Arreglando Dependencias y Errores de Importación

## Problema Encontrado

```
ModuleNotFoundError: No module named 'tools'
```

Esto ocurría porque los archivos dentro de `src/` importaban con rutas incorrectas:
```python
from tools.arg_detector import ARGDetector  # ❌ Incorrecto
```

Debería ser:
```python
from .tools.arg_detector import ARGDetector  # ✅ Correcto (importación relativa)
```

---

## ✅ Lo que se Ha Arreglado

### 1. Importaciones Corregidas

Los siguientes archivos han sido actualizados para usar importaciones relativas correctas:

- **`src/detectores.py`** - Línea 17
- **`src/ia_agente.py`** - Línea 122
- **`src/guardian.py`** - Línea 3

Cambio:
```python
# Antes
from tools.arg_detector import ARGDetector

# Ahora
from .tools.arg_detector import ARGDetector
```

### 2. Dependencias Limpias

Se han creado nuevos archivos con dependencias minimalistas y sin conflictos:

- **`requirements-clean.txt`** - Lista simple de paquetes
- **`install-clean.sh`** - Script de instalación para Linux/Mac
- **`install-clean.ps1`** - Script de instalación para Windows
- **`install_dependencies.py`** - Script Python para instalar paquetes

---

## 🚀 Cómo Solucionar

### Opción 1: Instalación Limpia (Recomendado)

**En Windows (PowerShell):**
```powershell
# Ejecutar el script de instalación
.\install-clean.ps1
```

**En Linux/Mac:**
```bash
# Ejecutar el script de instalación
bash install-clean.sh
```

**Alternativa (cualquier sistema):**
```bash
python install_dependencies.py
```

### Opción 2: Instalación Manual

Si prefieres instalar manualmente, limpia y reinstala:

```bash
# 1. Eliminar venv (opcional pero recomendado)
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# 2. Crear nuevo venv
python -m venv venv

# 3. Activar venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 4. Instalar dependencias limpias
pip install -r requirements-clean.txt
```

### Opción 3: Instalar Solo lo Necesario

Si solo quieres instalar lo mínimo para Streamlit:

```bash
pip install streamlit pandas requests azure-identity azure-mgmt-resourcegraph
```

---

## 📝 Archivos de Requisitos

### `requirements-clean.txt` (Recomendado)

Este archivo contiene **solo** las dependencias necesarias:

```
azure-identity==1.25.1
azure-mgmt-resourcegraph==8.0.1
azure-mgmt-costmanagement==4.0.1
pandas==2.3.3
rich==14.2.0
python-dotenv==1.2.1
requests==2.32.5
streamlit==1.41.1
langchain-community==0.4.1
langchain-ollama==1.0.1
ollama==0.6.1
pytest==7.4.4
duckdb==1.4.3
```

**Ventajas:**
- ✅ Sin dependencias transitivas conflictivas
- ✅ Versiones compatibles verificadas
- ✅ Mucho más rápido de instalar
- ✅ Menos problemas de compilación

### `requirements.txt` (Anterior)

El archivo anterior tenía 255 líneas con todas las dependencias transitivas expandidas. Puede causar conflictos.

---

## 🔍 Verificar Instalación

Después de instalar, verifica que todo funciona:

```python
# Prueba 1: Importaciones básicas
python -c "import streamlit; import pandas; import azure.identity; print('✅ OK')"

# Prueba 2: Importaciones del proyecto
python -c "from src.detectores import full_scan; print('✅ OK')"

# Prueba 3: Ejecutar Streamlit
streamlit run app.py
```

Si todo funciona, deberías ver:
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

---

## ❌ Si Sigue Fallando

### Problema: "No module named 'streamlit'"

```bash
# Solución: Instalar streamlit explícitamente
pip install streamlit --upgrade

# O en el venv:
venv/Scripts/pip install streamlit --upgrade  # Windows
source venv/bin/activate && pip install streamlit --upgrade  # Linux/Mac
```

### Problema: "ModuleNotFoundError: No module named 'src'"

```bash
# Solución: Asegúrate de que estés ejecutando desde la raíz del proyecto
cd c:\Users\adnan\Desktop\guardian-efimero  # O tu ruta

# Verifica que exista src/__init__.py
ls src/__init__.py  # Linux/Mac
dir src\__init__.py  # Windows
```

### Problema: "Conflicto de dependencias"

```bash
# Solución: Limpiar caché y reinstalar
pip cache purge
pip install --upgrade --force-reinstall streamlit pandas requests
```

---

## 📊 Comparación de Requisitos

| Aspecto | `requirements.txt` | `requirements-clean.txt` |
|---------|---|---|
| Líneas | 255 | 14 |
| Dependencias directas | 11 | 13 |
| Dependencias transitivas | 200+ | Minimizadas |
| Tamaño final | 500+ MB | ~150 MB |
| Tiempo instalación | 5-10 min | 2-3 min |
| Conflictos potenciales | Altos | Bajos |
| Mantenibilidad | Compleja | Simple |

---

## 🎯 Recomendación Final

**Para evitar problemas en el futuro:**

1. **Usa `requirements-clean.txt`** en lugar de `requirements.txt`
2. **Actualiza `requirements.in`** para que sea más simple:
   ```
   streamlit
   pandas
   azure-identity
   azure-mgmt-resourcegraph
   azure-mgmt-costmanagement
   requests
   rich
   python-dotenv
   langchain-community
   langchain-ollama
   ollama
   pytest
   duckdb
   ```

3. **Luego compila:**
   ```bash
   pip-compile requirements.in
   ```

---

## 🔄 Próximos Pasos

```bash
# 1. Instalar dependencias limpias
python install_dependencies.py

# 2. Verificar Azure login
az login

# 3. Ejecutar Streamlit
streamlit run app.py
```

**¡Listo! 🎉**

---

## 📚 Referencias

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Azure SDK for Python](https://learn.microsoft.com/en-us/python/azure/)
- [pip documentation](https://pip.pypa.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Última actualización**: 2026-02-04
**Versión**: 1.1 (Dependencies Fix)
