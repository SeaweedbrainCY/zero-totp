.DEFAULT_GOAL := run

install_frontend:
	echo "Installing frontend dependencies ..."
	cd frontend && npm install

run_frontend:
	echo "Starting frontend server ..."
	cd frontend && ng serve "zero-totp" --host=127.0.0.1  --proxy-config proxy.conf.json

install_api: clean
	echo "Installing API dependencies ..."
	cd api && uv sync --locked

update_api_deps:
	echo "Upgrading API dependencies within pyproject.toml constraints ..."
	cd api && uv lock --upgrade && uv sync

run_api:
	echo "Starting API server ..."
	cd api && uv run python app.py

run_database:
	echo "Starting docker database container ..."
	docker-compose up database

test:
	echo "Running tests ..."
	mv api/config/config.yml api/config/.secret/config.yml
	cp api/tests/ressources/test-config.yml api/config/config.yml
	cd api && uv run python -m pytest --cov=. --cov-report=term --cov-report=html -s
	mv -f api/config/.secret/config.yml api/config/config.yml

run:
	make run_database & \
	make run_frontend & \
	make run_api

clean:
	echo "Cleaning up ..."
	rm -rf api/.venv api/venv
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "pycache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +


run_ios:
	echo "Building and running iOS application"
	cd frontend && ng build zero-totp --configuration mobile-development --subresource-integrity
	cd mobile && npx cap sync ios && npx cap open ios

run_rescue:
	echo "Starting rescue frontend server ..."
	cd frontend && ng serve rescue --host=127.0.0.1

update_i18n:
	echo "Updating en-uk i18n file"
	cd frontend && npx ngx-translate-extract --input ./src --output ./src/assets/i18n/en-uk.json  --sort -f "json"
