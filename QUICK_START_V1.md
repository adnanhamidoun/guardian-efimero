🚀 QUICK START — Guardian Efímero v1
====================================

**5 minutos a un escaneo funcional**

---

## ⚡ Setup (1 min)

```bash
# 1. Entorno Python
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell

# 2. Dependencias
pip install -r requirements.txt

# 3. Autenticación Azure
az login
```

---

## 🎯 Demo Completa (3 min)

```powershell
# PowerShell terminal

# Crear 8 recursos demo
.\scripts\demo_setup.ps1
# → Espera "✓ Setup completado"

# Verificar que se crearon
.\scripts\demo_verify.ps1
# → Ver "Encontrados 8 recurso(s) de demo"
```

---

## 🌐 Ejecutar UI (1 min)

```bash
# Terminal con entorno activado
streamlit run app.py
```

**En la UI (http://localhost:8501):**

1. **Sidebar** (izq):
   - ☑️ Activa "🎯 DEMO MODE"
   - Baja "📅 snapshot_age_days" a 0
   - Click "🔄 Limpiar caché"

2. **Sección "1️⃣ Escanear Azure"**:
   - Click "🔍 Ejecutar escaneo"
   - Espera 30-60s
   - Verás: **8 tipos detectados**, **>70€/mes ahorro**

3. **Sección "2️⃣ Recomendaciones IA"** (opcional):
   - Click "🤖 Obtener recomendaciones"
   - Si Ollama: IA mejorada; si no: 100% heurística funciona igual

4. **Sección "3️⃣ Aprobación Humana"**:
   - Checkboxes: ☑️ "Seleccionar todos"
   - Verás: "✅ 8 recursos seleccionados", ahorro total

5. **Sección "4️⃣ Comandos az CLI"**:
   - Botón "💾 Descargar script.sh"
   - O copia los 8 comandos `az delete`

---

## 🧹 Limpiar (1 min)

```powershell
.\scripts\demo_cleanup.ps1
# → Escribe "yes" para confirmar
# → Ver "✓ Eliminación iniciada"
```

---

## 📊 Qué esperar

**Recursos demo creados:**
- ✅ 1 Disco sin adjuntar
- ✅ 1 IP pública huérfana
- ✅ 1 NIC sin VM
- ✅ 1 VM deallocated
- ✅ 1 Load Balancer sin reglas
- ✅ 1 App Service Plan vacío
- ✅ 1 Snapshot "antiguo"
- ✅ 1 NSG sin asociar

**Escaneo detectará:** 8/8 tipos ✅

**Ahorro potencial:** ~75-85€/mes

---

## 🐛 Si algo falla

| Problema | Solución |
|----------|----------|
| "No autenticado" | `az login` nuevamente |
| "ResourceGroup existía" | Scripts son idempotentes, reintenta |
| Streamlit no se abre | Copia URL (`http://localhost:8501`) en navegador |
| 0 recursos detectados | Baja `snapshot_age_days` a 0 en sidebar |
| Ollama no disponible | OK, heurística pura funciona (sin IA mejorada) |

---

## 📚 Documentación Completa

- **README_V1.md** → Guía detallada + todas las queries KQL
- **IMPLEMENTATION_REPORT.md** → Detalles técnicos (7 archivos modificados, 8 queries exactas, etc.)
- **scripts/update_app_ui.py** → Si UI sidebar no se actualizó auto

---

## ✅ Checklist

- [ ] `python -m venv venv` y activar
- [ ] `pip install -r requirements.txt`
- [ ] `az login` exitoso
- [ ] `.\scripts\demo_setup.ps1` completado (8 recursos)
- [ ] `streamlit run app.py` funcionando
- [ ] Escaneo detecta 8 tipos
- [ ] Ahorro > 70€/mes mostrado
- [ ] Comandos az listos para copiar
- [ ] `.\scripts\demo_cleanup.ps1` ha limpiado recursos

---

**¡Listo! Guardian Efímero v1 está operativo.** 🛡️

Próximos pasos: Ver README_V1.md para detalles, o README (antiguo) para funcionalidades IA.
