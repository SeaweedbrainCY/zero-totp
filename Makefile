.DEFAULT_GOAL := run

install_frontend:
	cd frontend && npm install 

run_frontend:
	cd frontend && ng serve --host=127.0.0.1 --disable-host-check

install_api:
	rm -rf api/venv
	python3 -m venv api/venv
	api/venv/bin/pip install -r api/requirements.txt

run_api:
	. .env && . api/venv/bin/activate && cd api && python app.py


run: 
	echo "Starting frontend server ..."
	make run_frontend & \
	echo "Starting API ..." &&\
	make run_api



clean:
	rm -rf pycache 