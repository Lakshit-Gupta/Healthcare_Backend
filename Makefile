.PHONY: lint test migrate lint-migrations security-check serve check

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy apps/

test:
	uv run pytest --cov=apps --cov-report=term-missing

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

lint-migrations:
	uv run python manage.py lintmigrations --include-apps accounts patients doctors mappings

security-check:
	uv run python manage.py check --deploy --settings=config.settings.production

serve:
	uv run granian --interface asgi --workers 4 --runtime-mode mt \
		--runtime-threads 2 --loop uvloop --backpressure 128 \
		config.asgi:application

check: lint lint-migrations security-check test
	@echo "All checks passed ✓"
