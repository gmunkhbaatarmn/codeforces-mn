all:
	@echo "Please see Makefile"

deploy:
	appcfg.py update .

dev-deploy:
	appcfg.py update . --version=dev

ci-dependency:
	@pip install flake8
	@pip install flake8-print flake8-quotes flake8-blind-except pep8-naming
	@pip install nose appengine-sdk lxml pyyaml

ci-test:
	flake8 --inline-quotes '"' .
	python tests.py
	@#todo: upgrade and check natrix.py version
