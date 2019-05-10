# Unit-testing, docs.

VIRTUALENV?=python3 -m venv

all: test flakes pep8

env:
	mkdir -p .download_cache
	rm -rf env/
	$(VIRTUALENV) --clear env
	env/bin/pip3 install --cache-dir=.download_cache pyparsing sphinx pyflakes pep8
	@echo ">> Run 'source env/bin/activate'" 

test:
	env/bin/python3 -m unittest discover -v

doc:
	cd doc && make html

flakes:
	-env/bin/pyflakes loggerglue

pep8:
	# E501 line too long
	-env/bin/pep8 --repeat --statistics --ignore=E501 loggerglue

.PHONY: env doc
