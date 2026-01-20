venv:
	python -m venv .venv
	source .venv/bin/activate && pip install pip-tools
	pip-compile requirements.in

test:
	source .venv/bin/activate && pytest

run:
	source .venv/bin/activate && python src/guardian.py

install-ollama:
	curl -fsSL https://ollama.com/install.sh | sh
	ollama pull llama3.1
