# 📚 ÍNDICE DE DOCUMENTACIÓN - Guardian Efímero

## 🎯 ¿Dónde Empezar?

### 1️⃣ **Si no sabes nada del proyecto**
→ Lee [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) (5 min)

### 2️⃣ **Si quieres usarlo rápido**
→ Lee [QUICK_START.md](QUICK_START.md) (10 min)

### 3️⃣ **Si quieres conocerlo a fondo**
→ Lee [GUIA_USUARIO.md](GUIA_USUARIO.md) (30 min)

### 4️⃣ **Si necesitas desarrollar/mantener**
→ Lee [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) (45 min)

---

## 📖 Todos los Documentos

### 🏆 Documentación Principal (NUEVA - Fase 3)

| Doc | Propósito | Tiempo | Audiencia |
|-----|-----------|--------|-----------|
| [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) | Overview ejecutivo de Fase 3 | 5 min | Ejecutivos/Managers |
| [QUICK_START.md](QUICK_START.md) | Cómo empezar en 5 minutos | 10 min | Usuarios nuevos |
| [GUIA_USUARIO.md](GUIA_USUARIO.md) | Manual completo del usuario | 30 min | Usuarios |
| [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) | Arquitectura y detalles técnicos | 45 min | Developers |

### 🔧 Documentación de Cambios (NUEVA - Fase 3)

| Doc | Propósito | Tiempo |
|-----|-----------|--------|
| [FIX_STORAGE_DASHBOARD.md](FIX_STORAGE_DASHBOARD.md) | Resumen de cambios Fase 3 | 10 min |
| [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) | Resultados de pruebas | 5 min |
| [CHECKLIST_VALIDACION.md](CHECKLIST_VALIDACION.md) | Checklist completo | 10 min |

### 📋 Documentación Existente

| Doc | Contenido |
|-----|-----------|
| [README.md](README.md) | README original (desactualizado) |
| [README_NUEVO.md](README_NUEVO.md) | README mejorado |
| [FIX_DEPENDENCIES.md](FIX_DEPENDENCIES.md) | Solución de dependencias (Fase 2) |
| [FIX_SUMMARY.md](FIX_SUMMARY.md) | Resumen de fixes anteriores |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumen de implementación (Fase 1) |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Referencia rápida |
| [STREAMLIT_IMPLEMENTATION.md](STREAMLIT_IMPLEMENTATION.md) | Detalles Streamlit |
| [QUICK_FIX.md](QUICK_FIX.md) | Fixes rápidos |
| [START_HERE.md](START_HERE.md) | Punto de entrada alternativo |

---

## 🗺️ Mapa de Documentación por Rol

### 👨‍💼 **Ejecutivo / Manager**
```
1. RESUMEN_EJECUTIVO.md (5 min)
   ↓
2. GUIA_USUARIO.md → "Casos de Uso" (5 min)
   ↓
3. Listo para presentar ROI
```

### 👤 **Usuario Final**
```
1. QUICK_START.md (10 min)
   ↓
2. Ejecutar: streamlit run app.py
   ↓
3. Usar dashboard (auto-explicativo)
```

### 👨‍💻 **Developer / DevOps**
```
1. DOCUMENTACION_TECNICA.md (45 min)
   ↓
2. Revisar: src/detectores.py, app.py
   ↓
3. Leer: tests/test_detectores.py
   ↓
4. Extender: crear nuevo detector
```

### 🧪 **QA / Tester**
```
1. CHECKLIST_VALIDACION.md
   ↓
2. VERIFICACION_FINAL.md
   ↓
3. Ejecutar: pytest tests/test_detectores.py
   ↓
4. Verificar: test_storage_detection.py
```

---

## 🎯 Por Objetivo

### "Quiero Usar la App"
```
QUICK_START.md
    ↓
GUIA_USUARIO.md (si necesito ayuda)
    ↓
streamlit run app.py
```

### "Quiero Entender la Arquitectura"
```
DOCUMENTACION_TECNICA.md
    ↓
src/ (revisar código)
    ↓
tests/ (ver ejemplos)
```

### "Quiero Agregar un Nuevo Detector"
```
DOCUMENTACION_TECNICA.md → "Arquitectura"
    ↓
src/detectores.py (estudiar ejemplo)
    ↓
Crear nueva función: def detect_mi_zombie()
    ↓
Agregar a full_scan()
    ↓
tests/test_detectores.py (crear test)
```

### "Quiero Verificar que Todo Funciona"
```
VERIFICACION_FINAL.md
    ↓
CHECKLIST_VALIDACION.md
    ↓
pytest tests/test_detectores.py -v
    ↓
python test_storage_detection.py
```

### "Quiero Ver los Cambios de Fase 3"
```
FIX_STORAGE_DASHBOARD.md
    ↓
RESUMEN_EJECUTIVO.md
    ↓
src/detectores.py (línea 150)
    ↓
app.py (líneas 190-429)
```

---

## 📊 Matriz de Documentación

```
AUDIENCIA vs TÓPICO

                   Inicio  Uso    Técnico Cambios  Tests
Ejecutivos         ●     ○      ○       ●       ○
Usuarios           ●     ●      ○       ○       ○
Developers         ●     ○      ●       ●       ●
QA/Testers         ○     ●      ●       ●       ●
DevOps             ○     ●      ●       ●       ●

● = Importante
○ = Opcional
```

---

## 🚀 Lectura Recomendada

### Semana 1 (Onboarding)
```
Día 1: RESUMEN_EJECUTIVO.md (5 min)
Día 2: QUICK_START.md (10 min)
Día 3: GUIA_USUARIO.md (30 min)
       → Ejecuta app.py (20 min)
Día 4: DOCUMENTACION_TECNICA.md (30 min)
       → Revisa código (30 min)
Día 5: CHECKLIST_VALIDACION.md (10 min)
       → Ejecuta tests (10 min)
```

### Rápida (5 minutos)
```
RESUMEN_EJECUTIVO.md
```

### Estándar (30 minutos)
```
QUICK_START.md
    ↓
Ejecuta app.py
```

### Completa (2 horas)
```
RESUMEN_EJECUTIVO.md
    ↓
GUIA_USUARIO.md
    ↓
DOCUMENTACION_TECNICA.md
    ↓
Revisa código fuente
    ↓
Ejecuta tests
```

---

## 📞 ¿Dónde Encontrar...?

### "Cómo empezar"
→ [QUICK_START.md](QUICK_START.md#1️⃣-verificación-previa)

### "Cómo usar el dashboard"
→ [GUIA_USUARIO.md](GUIA_USUARIO.md#🎨-interfaz-de-usuario)

### "Cómo agregar un detector"
→ [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md#🏗️-arquitectura)

### "Cómo reportar bugs"
→ [GUIA_USUARIO.md](GUIA_USUARIO.md#📞-soporte)

### "Cómo ejecutar tests"
→ [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md#🧪-pruebas-ejecutadas)

### "Qué cambió en Fase 3"
→ [FIX_STORAGE_DASHBOARD.md](FIX_STORAGE_DASHBOARD.md)

### "State del proyecto"
→ [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)

### "Troubleshooting"
→ [GUIA_USUARIO.md](GUIA_USUARIO.md#🐛-solución-de-problemas)
→ [QUICK_START.md](QUICK_START.md#🐛-troubleshooting)

---

## 🎓 Orden de Lectura Sugerido

### Para Ejecutivos
```
1. RESUMEN_EJECUTIVO.md (5 min)
2. GUIA_USUARIO.md - "Características" (5 min)
3. GUIA_USUARIO.md - "Casos de Uso" (5 min)
Total: 15 minutos
```

### Para Usuarios
```
1. QUICK_START.md (10 min)
2. Ejecutar app.py (20 min)
3. GUIA_USUARIO.md si tienes dudas (20 min)
Total: 50 minutos
```

### Para Developers
```
1. RESUMEN_EJECUTIVO.md (5 min)
2. DOCUMENTACION_TECNICA.md (45 min)
3. Revisar src/ (30 min)
4. Revisar tests/ (15 min)
5. Ejecutar: pytest (5 min)
Total: 100 minutos
```

---

## ✨ Highlights de Documentación

### 🌟 Mejor para entender rápido
→ [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)

### 🌟 Mejor para empezar
→ [QUICK_START.md](QUICK_START.md)

### 🌟 Mejor para usar la app
→ [GUIA_USUARIO.md](GUIA_USUARIO.md)

### 🌟 Mejor para desarrollar
→ [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)

### 🌟 Mejor para verificar
→ [CHECKLIST_VALIDACION.md](CHECKLIST_VALIDACION.md)

---

## 📚 Índice por Sección

### Documentos sobre Fase 3
- [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) - Resultados
- [FIX_STORAGE_DASHBOARD.md](FIX_STORAGE_DASHBOARD.md) - Cambios técnicos
- [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) - Tests
- [CHECKLIST_VALIDACION.md](CHECKLIST_VALIDACION.md) - Validación

### Documentos sobre Uso
- [QUICK_START.md](QUICK_START.md) - Cómo empezar
- [GUIA_USUARIO.md](GUIA_USUARIO.md) - Manual completo
- [README_NUEVO.md](README_NUEVO.md) - README

### Documentos sobre Desarrollo
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) - Arquitectura
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Referencia rápida

---

## 🎯 Próximo Paso

```
¿Quién eres?

1. Ejecutivo/Manager       → RESUMEN_EJECUTIVO.md
2. Usuario nuevo           → QUICK_START.md
3. Usuario experimentado   → GUIA_USUARIO.md
4. Developer               → DOCUMENTACION_TECNICA.md
5. QA/Tester              → CHECKLIST_VALIDACION.md
6. DevOps                 → DOCUMENTACION_TECNICA.md + VERIFICACION_FINAL.md
```

---

## 📞 Contacto

- **Dudas de uso**: Ver [GUIA_USUARIO.md](GUIA_USUARIO.md#🐛-solución-de-problemas)
- **Dudas técnicas**: Ver [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)
- **Dudas de instalación**: Ver [QUICK_START.md](QUICK_START.md#🐛-troubleshooting)
- **Verificar estado**: Ver [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md)

---

**¡Bienvenido a Guardian Efímero! 🛡️**

Elige tu nivel y comienza:
- ⏱️ **5 minutos**: [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
- ⏱️ **10 minutos**: [QUICK_START.md](QUICK_START.md)
- ⏱️ **30 minutos**: [GUIA_USUARIO.md](GUIA_USUARIO.md)
- ⏱️ **1 hora**: [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)

---

**Última actualización**: 2026-02-04
**Versión**: 3.0
