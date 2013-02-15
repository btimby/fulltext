test:
	python tests.py

verify:
	pyflakes fulltext
	pep8 --exclude=migrations --ignore=E501,E225 fulltext

install:
	python setup.py install

publish:
	python setup.py register
	python setup.py sdist upload
