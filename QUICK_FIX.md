# 🚨 Quick Troubleshooting Guide

## El Error que Tenía

```
ModuleNotFoundError: No module named 'tools'
```

**Causa**: Importaciones con rutas incorrectas en `src/detectores.py`, `src/ia_agente.py`, `src/guardian.py`

**Solución**: ✅ **YA ESTÁ ARREGLADO** - Se han corregido todas las importaciones

---

## ✅ Lo que Tienes que Hacer Ahora

### Paso 1: Limpiar e Reinstalar Dependencias

```bash
# En Windows
pip cache purge
python install_dependencies.py

# O manualmente
pip install -r requirements-clean.txt --force-reinstall
```

### Paso 2: Verificar la Instalación

```bash
python verify_installation.py
```

Deberías ver:
```
✅ STREAMLIT: OK
✅ PANDAS: OK
✅ AZURE IDENTITY: OK
...
✅ SUCCESS: ¡Todo está bien configurado!
```

### Paso 3: Ejecutar Streamlit

```bash
streamlit run app.py
```

---

## 🔧 Si Sigue Fallando...

### Error: `ModuleNotFoundError: No module named 'streamlit'`

```bash
# Solución rápida
pip install streamlit --upgrade

# O reinstalar todo
python install_dependencies.py
```

### Error: `ModuleNotFoundError: No module named 'tools'` (de nuevo)

Esto significa que el archivo aún tiene la importación vieja. Verifica:

```bash
# Ver contenido del archivo
type src\detectores.py | find "from .tools"  # Windows
grep "from .tools" src/detectores.py  # Linux/Mac

# Debería mostrar: from .tools.arg_detector import ARGDetector
```

Si muestra `from tools.arg_detector` (sin el punto), necesitas actualizar manualmente:

```python
# Cambiar esta línea:
from tools.arg_detector import ARGDetector

# Por esta:
from .tools.arg_detector import ARGDetector
```

### Error: `ModuleNotFoundError: No module named 'azure'`

```bash
pip install azure-identity azure-mgmt-resourcegraph azure-mgmt-costmanagement
```

### Error: Port 8501 en uso

```bash
# Cambiar puerto
streamlit run app.py --server.port 8502

# O liberar el puerto
# Windows: netstat -ano | find "8501"
# Linux/Mac: lsof -i :8501
```

### Lentitud o congelamiento

```bash
# Streamlit puede tomar tiempo para iniciar
# Espera 30-60 segundos

# Si sigue congelado:
# 1. Cierra con Ctrl+C
# 2. Ejecuta: streamlit cache clear
# 3. Intenta de nuevo
```

---

## ✨ Comandos Útiles

```bash
# Ver qué versión de Python tienes
python --version

# Ver qué versión de streamlit está instalada
python -c "import streamlit; print(streamlit.__version__)"

# Ver todas las importaciones disponibles
python -c "import sys; print('\n'.join(sys.path))"

# Limpiar caché de pip
pip cache purge

# Reinstalar todo
pip install -r requirements-clean.txt --force-reinstall --no-cache-dir

# Ver el log de Streamlit en detalle
streamlit run app.py --logger.level=debug

# Configurar puerto diferente
streamlit run app.py --server.port 8502

# Desabilitar el navegador automático
streamlit run app.py --server.headless true
```

---

## 📋 Checklist Rápido

- [ ] Ejecuté: `python verify_installation.py` sin errores
- [ ] Ejecuté: `python install_dependencies.py` correctamente
- [ ] Ejecuté: `az login` para Azure
- [ ] Verifiqué que `from .tools` aparece en los archivos src/
- [ ] Ejecuté: `streamlit run app.py` sin errores
- [ ] Vi en el navegador: `http://localhost:8501`

---

## 🆘 Si Nada Funciona

**Nuclear Option** (Reinstalar todo):

```bash
# 1. Eliminar venv
rmdir /s /q venv  # Windows
rm -rf venv  # Linux/Mac

# 2. Crear nuevo venv
python -m venv venv

# 3. Activar venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 4. Instalar dependencias limpias
python install_dependencies.py

# 5. Verificar
python verify_installation.py

# 6. Ejecutar
streamlit run app.py
```

---

## 📞 Información de Debug

Si sigues teniendo problemas, proporciona:

```bash
# Copia la salida de estos comandos:
python --version
pip --version
pip list
python verify_installation.py

# En Windows PowerShell:
Get-Content src\detectores.py | Select-String "from .tools"
```

---

**Última actualización**: 2026-02-04
