.PHONY: up down logs ps db-init seed data verify test lint clean reset

-include .env
export

COMPOSE = docker compose -p masteryloop

up: ## start the full stack
	$(COMPOSE) up -d --build
	@echo "stack up — run 'make ps' to check health"

down: ## stop containers, keep volumes
	$(COMPOSE) down

reset: ## stop and wipe all volumes
	$(COMPOSE) down -v

ps: ## container health
	$(COMPOSE) ps

logs: ## tail all logs
	$(COMPOSE) logs -f --tail=100

db-init: ## re-apply schema (idempotent)
	$(COMPOSE) exec -T postgres psql -U $${DB_USER:-mastery} -d $${DB_NAME:-masteryloop} -f /docker-entrypoint-initdb.d/01_init.sql

seed: ## load reference + demo data
	python scripts/seed_db.py

data: ## download raw datasets
	python scripts/download_datasets.py

verify: ## M1 acceptance checks
	python scripts/verify_m1.py

test: ## unit tests for the domain library
	pytest tests/ -v

lint: ## format and lint
	black . && flake8 .

clean:
	find . -name '__pycache__' -type d -exec rm -rf {} +
