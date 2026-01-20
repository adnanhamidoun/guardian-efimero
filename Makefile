ifeq ($(OS),Windows_NT)
	ACTIVATE = .venv/Scripts/activate
else
	ACTIVATE = .venv/bin/activate
endif

venv:
	python -m venv .venv
	@echo Activando entorno y instalando pip-tools...
	source $(ACTIVATE) && pip install pip-tools
	pip-compile requirements.in

test:
	source $(ACTIVATE) && pytest

run:
	source $(ACTIVATE) && python src/guardian.py

install-ollama:
	curl -fsSL https://ollama.com/install.sh | sh
	ollama pull llama3.1
