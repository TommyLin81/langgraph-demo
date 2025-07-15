.PHONY: all help install clean dev test test_watch integration_tests extended_tests lint format typecheck spell_check spell_fix docker_build docker_up docker_down docker_clean gen_index k8s_check k8s_build k8s_helm_setup k8s_deploy k8s_secrets k8s_status k8s_clean k8s_port_forward langgraph_dev langgraph_studio

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

gen_index:
	docker compose -f ./deployment/docker/docker-compose.yml exec langgraph-api python src/tools/indexer.py

######################
# KUBERNETES
######################

k8s_build:
	docker build -f ./deployment/docker/Dockerfile -t langgraph-demo:latest .

k8s_helm_setup:
	helm repo add langchain https://langchain-ai.github.io/helm/ || true
	helm repo update

k8s_secrets:
	@if [ -z "$$OPENAI_API_KEY" ] || [ -z "$$LANGSMITH_API_KEY" ]; then \
		echo "OPENAI_API_KEY or LANGSMITH_API_KEY not set. Please update deployment/k8s/secrets.yaml"; \
	else \
		sed -e "s/your-openai-api-key-here/$$OPENAI_API_KEY/" -e "s/your-langsmith-api-key-here/$$LANGSMITH_API_KEY/" deployment/k8s/secrets.yaml | kubectl apply -f -; \
	fi

k8s_pvc:
	kubectl apply -f deployment/k8s/vector-store-pvc.yaml

k8s_deploy: k8s_check k8s_build k8s_helm_setup k8s_secrets k8s_pvc
	helm upgrade --install langgraph-demo langchain/langgraph-cloud \
		--values deployment/k8s/values.yaml \
		--create-namespace \
		--namespace langgraph-demo

k8s_gen_index:
	kubectl exec -n langgraph-demo -it $$(kubectl get pods -n langgraph-demo -l app.kubernetes.io/component=langgraph-demo-langgraph-cloud-api-server -o jsonpath='{.items[0].metadata.name}') -- python src/tools/indexer.py

k8s_port_forward:
	kubectl port-forward -n langgraph-demo service/langgraph-demo-langgraph-cloud-api-server 8123:80

k8s_clean:
	helm uninstall langgraph-demo -n langgraph-demo

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
	@echo '  gen_index           - generate AWS documentation index'
	@echo ''
	@echo 'Kubernetes:'
	@echo '  k8s_check                    - check Kubernetes requirements'
	@echo '  k8s_build                    - build Docker image for Kubernetes'
	@echo '  k8s_deploy                   - full deployment to Kubernetes cluster'
	@echo '  k8s_secrets                  - deploy secrets to Kubernetes'
	@echo '  k8s_status                   - check Kubernetes deployment status'
	@echo '  k8s_clean                    - remove Kubernetes deployment'
	@echo '  k8s_port_forward             - port forward to access application locally'
	@echo ''
	@echo 'LangGraph:'
	@echo '  langgraph_dev                - start LangGraph development server'
	@echo '  langgraph_studio             - open LangGraph Studio in browser'
	@echo ''
	@echo '=================================================================='