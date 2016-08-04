all:
	@echo "Please see Makefile"

ci-dependency:
	@# next: upgrade flake8 to 3.x
	@pip install flake8==2.6.2
	@pip install flake8-print flake8-quotes flake8-blind-except pep8-naming
	@pip install nose appengine-sdk lxml pyyaml

ci-test:
	flake8 --inline-quotes '"' .
	python tests.py
