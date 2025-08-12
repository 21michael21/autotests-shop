.PHONY: test clean allure

VENV=./venv
PY=$(VENV)/bin/python
PYTEST=$(PY) -m pytest

clean:
	@rm -rf allure-results allure-report || true

test: clean
	$(PYTEST) -q --alluredir=allure-results

allure:
	@rm -rf allure-report || true
	allure serve allure-results || echo "Install allure locally to view reports"


