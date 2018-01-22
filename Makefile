PYTHON = python3

# In not in a virtualenv, add --user options for install commands.
INSTALL_OPTS = `$(PYTHON) -c "import sys; print('' if hasattr(sys, 'real_prefix') else '--user')"`
SYSDEPS = \
	antiword \
	libjpeg-dev \
	poppler-utils \
	tesseract-ocr abiword \
	unrtf \
	pstotext \
	libimage-exiftool-perl \
	unrar \
	python-setuptools \
	python3-setuptools \
	python-dev \
	python3-dev \
	python-pip \
	python3-pip
TEST_PREFIX = PYTHONWARNINGS=all FULLTEXT_TESTING=1
PASSWORD =

test:  ## Run tests.
	${MAKE} install-git-hooks
	$(TEST_PREFIX) $(PYTHON) fulltext/test/__init__.py

ci:  ## Run CI tests.
	${MAKE} sysdeps
	${MAKE} pydeps
	${MAKE} test
	${MAKE} lint

lint:  ## Run linters.
	${MAKE} install-git-hooks
	@git ls-files | grep \\.py$ | xargs $(PYTHON) -m flake8

install:  ## Install this package as current user in "edit" mode.
	${MAKE} install-git-hooks
	PYTHONWARNINGS=all $(PYTHON) setup.py develop $(INSTALL_OPTS)

pydeps:  ## Install third party python libs.
	$(PYTHON) -m pip install $(INSTALL_OPTS) --upgrade -r requirements.txt
	$(PYTHON) -m pip install $(INSTALL_OPTS) --upgrade flake8

sysdeps:  ## Install system deps (Ubuntu).
	sudo apt-get install -y $(SYSDEPS)
	sudo apt-get install python
	sudo pip2 install --pre --upgrade pyhwp

clean:  ## Remove all build files.
	rm -rf `find . -type d -name __pycache__ \
		-o -type f -name \*.bak \
		-o -type f -name \*.orig \
		-o -type f -name \*.pyc \
		-o -type f -name \*.pyd \
		-o -type f -name \*.pyo \
		-o -type f -name \*.rej \
		-o -type f -name \*.so \
		-o -type f -name \*.~ \
		-o -type f -name \*\$testfn`
	rm -rf \
		*.core \
		*.egg-info \
		*\$testfn* \
		.coverage \
		.tox \
		build/ \
		dist/ \
		docs/_build/ \
		htmlcov/ \
		venv \
		tmp/

install-git-hooks:  ## Install GIT pre-commit hook.
	@ln -sf ../../.git-pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- distribution

sdist:  ## Create a tar.gz distribution.
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py --version

priv-pypi-upload:  ## Upload source distribution on private PYPI repo.
	# Note: to reference the uploaded distribution, requirements.txt will
	# need an entry like this:
	#   --extra-index-url http://pypi.dev.veristack.com/root/veristack-fulltext/+simple/
	#   fulltext==0.8.315.b00117c
	${MAKE} sdist
	venv/bin/pip install devpi-client
ifndef PASSWORD
	venv/bin/python -m devpi login root
else
	venv/bin/python -m devpi login root --password=$(PASSWORD)
endif
	# Create index (done once)
	# venv/bin/python -m devpi index --create root/veristack-fulltext
	venv/bin/python -m devpi use http://pypi.dev.veristack.com/root/veristack-fulltext
	venv/bin/python -m devpi upload -v dist/fulltext-`$(PYTHON) setup.py --version`.tar.gz

publish:  ## Upload package on PYPI.
	$(PYTHON) setup.py register
	$(PYTHON) setup.py sdist upload
