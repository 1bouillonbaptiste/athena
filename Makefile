

setup:
	pip install pipx
	pipx install --force pre-commit poetry==1.8.3
	pre-commit install
	poetry install
