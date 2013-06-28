#PATH := build/python/bin:$(PATH)
#VERSION = $(shell python setup.py --version)
#ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)

.PHONY: test clean

test:
	python -m unittest discover -p '*.py'

clean:
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true
	find * -name '*.pyc' -delete
	find * -name '*.pyo' -delete
	find * -name 'out' -delete

