
test: 
    poetry run pytest tests/ 

run:
    poetry run python -m dblingo.dblingo

get-token:
    poetry run python src/dblingo/tools/duolingo_jwt.py
