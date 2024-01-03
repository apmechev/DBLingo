test: 
    poetry run pytest tests/ 

run:
    poetry run python -m dblingo.dblingo

get-token:
    poetry run python src/dblingo/tools/duolingo_jwt.py

install:
    poetry install

lint: 
    poetry run ruff src tests

lint-fix:
    poetry run ruff src tests --fix
