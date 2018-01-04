all:
	@echo "Please see Makefile"

run:
	concurrently \
		"dev_appserver.py . --port=9090 --admin_port=9000 --datastore_path=.datastore.dump" \
		"stylus --watch static/app.css.styl --out static/app.css -u nib -u rupture --include-css"

deploy:
	appcfg.py update .

dev-deploy:
	appcfg.py update . --version=dev

ci-init:
	@pip install flake8
	@pip install flake8-print flake8-quotes flake8-blind-except pep8-naming
	@pip install flake8-builtins flake8-commas flake8-comprehensions
	@pip install nose
	@pip install appengine-sdk jinja2 lxml pyyaml

ci-test:
	flake8 --max-line-length=100 --inline-quotes '"' .
	python tests.py
	python packages/natrix.py --check-only
