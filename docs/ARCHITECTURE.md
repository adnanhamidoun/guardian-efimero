# ARCHITECTURE

Componentes principales:

- `src/detectores.py`: lógica de detección de recursos zombis en Azure (API/ResourceGraph/SDK)
- `src/ia_agente.py`: agente híbrido que combina heurísticas y Ollama para recomendaciones
- `src/cli_generator.py`: genera comandos `az` a partir de recursos y recomendaciones
- `app.py`: interfaz Streamlit (scan → recomendaciones → aprobación → comandos)
- `tests/`: conjunto de pruebas unitarias

Flujo:
1. `full_scan()` detecta recursos zombis y devuelve lista de dicts.
2. El agente (híbrido) analiza cada recurso y devuelve acción/confianza/razón.
3. El usuario revisa y selecciona recursos.
4. `build_script()` genera comandos `az` listos para ejecutar manualmente.

Notas:
- El agente usa heurísticas por defecto y llama a Ollama solo en casos ambiguos.
- Los comandos nunca se ejecutan automáticamente desde la app.
