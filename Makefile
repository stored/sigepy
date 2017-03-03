.PHONY: install clean test coverage docs

install:
	pip install -e .[docs,test]
	pip install bumpversion twine wheel

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

test:
	py.test -vvv

coverage:
	py.test --cov=sigep --cov-report=term-missing --cov-report=html

docs:
	phinx-apidoc sigep -o docs/source
	$(MAKE) -C docs html

release:
	pip install twine wheel
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload -s dist/*