.PHONY: test run clean agente

test:
	pytest tests/ -v

run:
	python src/guardian.py

agente:
	python src/ia_agente.py

clean:
	az disk delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
	az network public-ip delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
