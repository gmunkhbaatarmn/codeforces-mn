all:
	@echo "Please see Makefile"

deploy:
	appcfg.py update .

dev-deploy:
	appcfg.py update . --version=dev

ci-dependency:
	@pip install flake8
	@pip install flake8-print flake8-quotes flake8-blind-except pep8-naming
	@pip install nose appengine-sdk jinja2 lxml pyyaml

ci-test:
	flake8 --inline-quotes '"' .
	python tests.py
	python packages/natrix.py --check-only
