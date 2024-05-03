.DEFAULT_GOAL := run

install_frontend:
	echo "Installing frontend dependencies ..."
	cd frontend && npm install

run_frontend:
	echo "Starting frontend server ..."
	cd frontend && ng serve --host=127.0.0.1 --disable-host-check

install_api: clean
	echo "Installing API dependencies ..."
	python3.11 -m venv api/venv
	api/venv/bin/pip install -r api/requirements.txt

run_api:
	echo "Starting API server ..."
	. .env && . api/venv/bin/activate && cd api && python app.py

run_database:
	echo "Starting docker database container ..."
	docker-compose up database

test:
	echo "Running tests ..."
	. .env && . api/venv/bin/activate && cd api && python3 -m pytest -vvv

run:
	make run_database & \
	make run_frontend & \
	make run_api

clean:
	echo "Cleaning up ..."
	rm -rf api/venv
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "pycache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
