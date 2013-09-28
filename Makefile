#PATH := build/python/bin:$(PATH)
#VERSION = $(shell python setup.py --version)
#ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)

.PHONY: test clean pack

test:
	python3 -m unittest discover -s test -p "*.py"

clean:
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true
	find * -name '*.pyc' -delete
	find * -name '*.pyo' -delete
	find * -name 'out' -delete

# find bb -name "*.pyo" | cpio -p /usr/local/lib/python3.2/dist-packages
# python -O -c "from bb.web import main; main(8000, 8100)"
# python -O -m bb.web
pack:
	python3 -OO -m compileall -b -q bb
