.PHONY: test run clean agente full_scan

test:
	pytest tests/ -v

run:
	python src/guardian.py

agente:
	python src/ia_agente.py

full_scan:
	python -c "from src.detectores import full_scan; import json; print(json.dumps(full_scan(), ensure_ascii=False, indent=2))"

clean:
	az disk delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
	az network public-ip delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
