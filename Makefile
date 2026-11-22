.PHONY: test lint run

test:
	python -m pytest -v

lint:
	python -m ruff check src tests

run:
	python -m src.configlang.cli examples/web_server.conf
