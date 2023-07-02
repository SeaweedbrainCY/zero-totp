.DEFAULT_GOAL := run

install_frontend:
	cd frontend && npm install 

run_frontend:
	cd frontend && ng serve


run: 
	echo "Starting frontend server ..."
	make run_frontend
