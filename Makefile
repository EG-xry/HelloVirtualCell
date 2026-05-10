.PHONY: setup all pipeline app test clean

PY ?= python3
VENV ?= .venv
ACT = . $(VENV)/bin/activate

setup:
	$(PY) -m venv $(VENV)
	$(ACT) && pip install --upgrade pip && pip install -r requirements.txt
	@echo "✅ Environment ready. Activate with: source $(VENV)/bin/activate"

all: pipeline

pipeline:
	$(ACT) && python -m openvcell.pipeline

app:
	$(ACT) && streamlit run openvcell/app.py

test:
	$(ACT) && pytest -q tests/

clean:
	rm -rf artifacts __pycache__ */__pycache__ .pytest_cache
