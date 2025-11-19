run_master:
	python3 src/master/master.py

run_router:
	python3 src/router/router.py

run_client:
	python3 src/client/client.py

install:
	pip install -r requirements.txt

tests:
	pytest -v

clean:
	find . -name "*.pyc" -delete
