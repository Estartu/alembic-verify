.PHONY: ruff-fix ruff-check ruff-format ruff-format-check lint format test install-tox-uv tox
.PHONY: ty install-reqs docker-test-db-run build publish-test publish bump-version update-lock
.PHONY: alembic-upgrade alembic-downgrade alembic-revision alembic-history

# Misc

MODULE_NAME=src/alembicverify
TEST_MODULE_NAME=test

# Database

DB_TEST_USER?=postgres
DB_TEST_PASSWORD?=postgres
DB_TEST_PORT?=5433
DB_TEST_HOST?=localhost
POSTGRES_CONTAINER_NAME?=postgres

# Linting and formatting

ruff-fix:
	uv run ruff check $(MODULE_NAME) $(TEST_MODULE_NAME) --fix

ruff-check:
	uv run $(UV_ARGS) ruff check $(MODULE_NAME) $(TEST_MODULE_NAME)

ruff-format:
	uv run ruff format $(MODULE_NAME) $(TEST_MODULE_NAME)

ruff-format-check:
	uv run $(UV_ARGS) ruff format --check $(MODULE_NAME) $(TEST_MODULE_NAME)

lint: ruff-check ruff-format-check

format: ruff-format ruff-fix

# type checking
ty: UV_ARGS?=
ty:
	uv run $(UV_ARGS) ty check

# requirements

update-lock:
	uv lock --upgrade

install-reqs:
	uv pip install -U -e ."[all]"

install-tox-uv:
	uv tool install tox --with tox-uv

tox:
	uv tool run tox

# Tests
test: UV_ARGS?=
test: ARGS?=
test:
	uv run $(UV_ARGS) coverage run -m pytest test $(ARGS) \
		--db-user=$(DB_TEST_USER) \
		--db-password=$(DB_TEST_PASSWORD) \
		--db-host=$(DB_TEST_HOST) \
		--db-port=$(DB_TEST_PORT)
	uv run $(UV_ARGS) coverage report
	uv run $(UV_ARGS) coverage html

# Docker
docker-test-db-run:
	docker start $(POSTGRES_CONTAINER_NAME)-test \
		|| docker run -d --name $(POSTGRES_CONTAINER_NAME)-test -p $(DB_TEST_PORT):5432 \
		-e POSTGRES_USER=$(DB_TEST_USER) \
		-e POSTGRES_PASSWORD=$(DB_TEST_PASSWORD) \
		-e POSTGRES_INITDB_ARGS="--encoding=UTF8 --lc-collate=en_US.utf8 --lc-ctype=en_US.utf8" \
		postgres:18.1

# Build and Publish

bump-version: ARGS?=patch
bump-version:
	uv version --bump $(ARGS)

build:
	rm -rf dist
	rm -rf .pdm-build
	uv build

publish-test: build
	uv publish --index testpypi ${ARGS}

publish: build
	uv publish ${ARGS}

## Alembic
alembic-upgrade: ARGS?=head
alembic-upgrade:
	uv run alembic upgrade $(ARGS)

alembic-downgrade:
	uv run alembic downgrade $(ARGS)

alembic-revision:
	uv run alembic revision --autogenerate $(ARGS)

alembic-history:
	uv run alembic history $(ARGS)
