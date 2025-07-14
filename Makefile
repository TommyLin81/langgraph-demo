.PHONY: all help install clean dev test test_watch integration_tests extended_tests lint format typecheck spell_check spell_fix docker_build docker_up docker_down docker_clean gen_aws_docs_index langgraph_dev langgraph_studio

# Default target executed when no arguments are given to make.
all: help

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests/

######################
# DEVELOPMENT
######################

install:
	uv sync

dev:
	uv run langgraph dev --port 2024

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/

######################
# TESTING
######################

test:
	uv run pytest $(TEST_FILE)

test_watch:
	uv run ptw --snapshot-update --now . -- -vv tests/unit_tests

integration_tests:
	uv run pytest tests/integration_tests 

extended_tests:
	uv run pytest --only-extended $(TEST_FILE)

######################
# CODE QUALITY
######################

lint:
	uv run ruff check .
	uv run pyright

format:
	uv run ruff format .
	uv run ruff check --select I --fix .

typecheck:
	uv run pyright

spell_check:
	uv run codespell --toml pyproject.toml

spell_fix:
	uv run codespell --toml pyproject.toml -w

######################
# DOCKER
######################

docker_build:
	docker compose -f ./deployment/docker/docker-compose.yml build

docker_up:
	docker compose -f ./deployment/docker/docker-compose.yml up -d

docker_down:
	docker compose -f ./deployment/docker/docker-compose.yml down

docker_clean:
	docker compose -f ./deployment/docker/docker-compose.yml down -v --remove-orphans
	docker system prune -f

gen_aws_docs_index:
	docker compose -f ./deployment/docker/docker-compose.yml exec langgraph-api python src/tools/indexer.py

######################
# LANGGRAPH
######################

langgraph_dev:
	uv run langgraph dev --port 2024

langgraph_studio:
	open https://smith.langchain.com/studio/?baseUrl=http://localhost:8123

######################
# HELP
######################

help:
	@echo '==================== LangGraph Demo Makefile ===================='
	@echo ''
	@echo 'Development:'
	@echo '  install                      - install dependencies with uv'
	@echo '  dev                          - start LangGraph development server'
	@echo '  clean                        - clean up build artifacts and cache'
	@echo ''
	@echo 'Testing:'
	@echo '  test                         - run unit tests'
	@echo '  test TEST_FILE=<test_file>   - run specific test file'
	@echo '  test_watch                   - run unit tests in watch mode'
	@echo '  integration_tests            - run integration tests'
	@echo '  extended_tests               - run extended test suite'
	@echo ''
	@echo 'Code Quality:'
	@echo '  lint                         - run linters (ruff + pyright)'
	@echo '  format                       - auto-format code with ruff'
	@echo '  typecheck                    - run type checker (pyright)'
	@echo '  spell_check                  - check spelling'
	@echo '  spell_fix                    - fix spelling issues'
	@echo ''
	@echo 'Docker:'
	@echo '  docker_build                 - build Docker images'
	@echo '  docker_up                    - start all services with Docker Compose'
	@echo '  docker_down                  - stop all services'
	@echo '  docker_clean                 - stop services and clean up volumes'
	@echo '  gen_aws_docs_index           - generate AWS documentation index'
	@echo ''
	@echo 'LangGraph:'
	@echo '  langgraph_dev                - start LangGraph development server'
	@echo '  langgraph_studio             - open LangGraph Studio in browser'
	@echo ''
	@echo '=================================================================='