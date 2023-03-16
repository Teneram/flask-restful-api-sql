build:
	docker-compose create

create_db_with_test_data: build
	docker-compose up -d
	docker-compose exec app python -m cli create-db
	docker-compose exec app python -m cli fill-db
	docker-compose stop

start: build
	docker-compose up -d

createDB: start
	docker-compose exec app python -m cli create-db

fillDB: createDB
	docker-compose exec app python -m cli fill-db

flake8: start
	docker-compose run app flake8 . --exclude=test_app/,db/models/__init__.py,./app/app.py,*/site-packages/*

mypy: start
	docker-compose run app mypy .  --exclude=test_app/ --explicit-package-bases --ignore-missing-imports --disable-error-code union-attr

isort: start
	docker-compose run app isort .

test: start
	docker-compose run app pytest .
