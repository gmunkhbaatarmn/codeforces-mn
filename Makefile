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

ci-dependency:
	@pip install flake8
	@pip install flake8-print flake8-quotes flake8-blind-except pep8-naming
	@pip install nose appengine-sdk jinja2 lxml pyyaml

ci-test:
	flake8 --max-line-length=100 --inline-quotes '"' .
	python tests.py
	python packages/natrix.py --check-only
