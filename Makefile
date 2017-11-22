test:
	python tests.py

check:
	pyflakes fulltext
	pycodestyle --exclude=migrations --ignore=E501,E225 fulltext

lint: check

install:
	python setup.py install

publish:
	python setup.py register
	python setup.py sdist upload
