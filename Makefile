.PHONY: all format lint test tests test_watch integration_tests docker_tests help extended_tests typecheck spell_check spell_fix

# Default target executed when no arguments are given to make.
all: help

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests/

test:
	uv run pytest $(TEST_FILE)

integration_tests:
	uv run pytest tests/integration_tests 

test_watch:
	uv run ptw --snapshot-update --now . -- -vv tests/unit_tests

test_profile:
	uv run pytest -vv tests/unit_tests/ --profile-svg

extended_tests:
	uv run pytest --only-extended $(TEST_FILE)

typecheck:
	uv run pyright

######################
# LINTING AND FORMATTING
######################

# Define a variable for Python and notebook files.
PYTHON_FILES=src/
lint format: PYTHON_FILES=.
lint_diff format_diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d main | grep -E '\.py$$|\.ipynb$$')
lint_package: PYTHON_FILES=src
lint_tests: PYTHON_FILES=tests

lint lint_diff lint_package lint_tests:
	uv run ruff check .
	[ "$(PYTHON_FILES)" = "" ] || uv run ruff format $(PYTHON_FILES) --diff
	[ "$(PYTHON_FILES)" = "" ] || uv run ruff check --select I $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || uv run pyright $(PYTHON_FILES)

format format_diff:
	uv run ruff format $(PYTHON_FILES)
	uv run ruff check --select I --fix $(PYTHON_FILES)

spell_check:
	uv run codespell --toml pyproject.toml

spell_fix:
	uv run codespell --toml pyproject.toml -w

######################
# DOCKER
######################
gen_dockerfile:
	uv run langgraph dockerfile ./deployment/docker/Dockerfile

docker_build:
	docker compose -f ./deployment/docker/docker-compose.yml build

docker_up:
	docker compose -f ./deployment/docker/docker-compose.yml up -d

docker_down:
	docker compose -f ./deployment/docker/docker-compose.yml down

gen_aws_docs_index:
	docker compose -f ./deployment/docker/docker-compose.yml exec langgraph-api python src/tools/indexer.py

######################
# Development
######################
langgraph_studio:
	open https://smith.langchain.com/studio/?baseUrl=http://localhost:8123


######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'test                         - run unit tests'
	@echo 'tests                        - run unit tests'
	@echo 'test TEST_FILE=<test_file>   - run all tests in file'
	@echo 'test_watch                   - run unit tests in watch mode'
	@echo 'typecheck                    - run type checker (pyright)'
	@echo 'spell_check                  - check spelling'
	@echo 'spell_fix                    - fix spelling issues'

