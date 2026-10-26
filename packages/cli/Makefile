.PHONY: lint build format test clean install

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

build:
	@echo "__build_time__ = \"$(shell date +%Y.%m.%d.%H.%M.%S)\"" > src/grobid/_version.py
	pyinstaller --onefile --name grobid src/grobid/main.py
	@rm -f src/grobid/_version.py

test:
	pytest tests -v

install:
	pip uninstall -y grobid || true
	pip install -e .
