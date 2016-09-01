all:
	@echo "Please see Makefile"

ci-dependency:
	@pip install flake8
	@pip install flake8-print flake8-quotes flake8-blind-except pep8-naming
	@pip install nose appengine-sdk lxml pyyaml

ci-test:
	flake8 --inline-quotes '"' .
	python tests.py
