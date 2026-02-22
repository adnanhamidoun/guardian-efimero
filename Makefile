.PHONY: test run clean full_scan streamlit

test:
	pytest tests/ -v

run:
	python src/guardian.py

full_scan:
	python -c "from src.detectores import full_scan; import json; print(json.dumps(full_scan(), ensure_ascii=False, indent=2))"

streamlit:
	streamlit run app.py

clean:
	az disk delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
	az network public-ip delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true

full_scan:
	python -c "from src.detectores import full_scan; import json; print(json.dumps(full_scan(), ensure_ascii=False, indent=2))"

streamlit:
	streamlit run app.py

clean:
	az disk delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
	az network public-ip delete --resource-group HamidounElHabtiAdnan --name zombi-* --yes || true
