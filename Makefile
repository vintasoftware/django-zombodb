.PHONY: clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint: ## check linters
	isort -rc . --check-only
	prospector --messages-only

test: ## run tests quickly with the default Python
	python runtests.py

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source django_zombodb runtests.py
	coverage report -m
	coverage html
	open htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/django_zombodb.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ django_zombodb
	$(MAKE) -C docs clean
	DJANGO_SETTINGS_MODULE=example.example.settings $(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -q pip-tools
	pip-compile --upgrade -o requirements/dev.txt requirements/base.in requirements/dev.in requirements/quality.in
	pip-compile --upgrade -o requirements.txt requirements/base.in requirements/prod.in
	# Remove Django from requirements.txt
	sed '/django==/d' requirements.txt > requirements.tmp
	mv requirements.tmp requirements.txt
	# Make everything =>, not ==
	sed 's/==/>=/g' requirements.txt > requirements.tmp
	mv requirements.tmp requirements.txt
	pip-compile --upgrade -o requirements/doc.txt requirements/base.in requirements/doc.in
	pip-compile --upgrade -o requirements/quality.txt requirements/quality.in
	pip-compile --upgrade -o requirements/test.txt requirements/base.in requirements/test.in
	pip-compile --upgrade -o requirements/travis.txt requirements/travis.in
	# Let tox control the Django version for tests
	sed '/django==/d' requirements/test.txt > requirements/test.tmp
	mv requirements/test.tmp requirements/test.txt

requirements: ## install development environment requirements
	pip install -qr requirements/dev.txt -qr requirements/test.txt -qr requirements/quality.txt --exists-action w
	pip-sync requirements/dev.txt requirements/doc.txt requirements/quality.txt requirements/test.txt

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean ## package
	python setup.py sdist
	ls -l dist

selfcheck: ## check that the Makefile is well-formed
	@echo "The Makefile is well-formed."
