# Shortcuts for various tasks (UNIX only).
# To use a specific Python version run: "make install PYTHON=python3.3"
# You can set the variables below from the command line.

PYTHON = python
TSCRIPT = zerocopy/test/test_zerocopy.py
ARGS =
# List of nice-to-have dev libs.
DEPS = \
	check-manifest \
	coverage \
	flake8 \
	mock==1.0.1 \
	pep8 \
	pyflakes \
	setuptools \
	sphinx \
	twine \
	unittest2

# In not in a virtualenv, add --user options for install commands.
INSTALL_OPTS = `$(PYTHON) -c "import sys; print('' if hasattr(sys, 'real_prefix') else '--user')"`
TEST_PREFIX = PYTHONWARNINGS=all

all: test

# ===================================================================
# Install
# ===================================================================

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
		tmp/

_:

build: _  ## Compile without installing.
	# make sure setuptools is installed (needed for 'develop' / edit mode)
	$(PYTHON) -c "import setuptools"
	PYTHONWARNINGS=all $(PYTHON) setup.py build
	@# copies compiled *.so files in ./fastcopy directory in order to allow
	@# "import fastcopy" when using the interactive interpreter from within
	@# this directory.
	PYTHONWARNINGS=all $(PYTHON) setup.py build_ext -i
	rm -rf tmp
	$(PYTHON) -c "import zerocopy"  # make sure it actually worked

install:  ## Install this package as current user in "edit" mode.
	${MAKE} build
	PYTHONWARNINGS=all $(PYTHON) setup.py develop $(INSTALL_OPTS)
	rm -rf tmp

uninstall:  ## Uninstall this package via pip.
	cd ..; $(PYTHON) -m pip uninstall -y -v fastcopy || true
	$(PYTHON) scripts/purge_installation.py

install-pip:  ## Install pip (no-op if already installed).
	$(PYTHON) -c \
		"import sys, ssl, os, pkgutil, tempfile, atexit; \
		sys.exit(0) if pkgutil.find_loader('pip') else None; \
		pyexc = 'from urllib.request import urlopen' if sys.version_info[0] == 3 else 'from urllib2 import urlopen'; \
		exec(pyexc); \
		ctx = ssl._create_unverified_context() if hasattr(ssl, '_create_unverified_context') else None; \
		kw = dict(context=ctx) if ctx else {}; \
		req = urlopen('https://bootstrap.pypa.io/get-pip.py', **kw); \
		data = req.read(); \
		f = tempfile.NamedTemporaryFile(suffix='.py'); \
		atexit.register(f.close); \
		f.write(data); \
		f.flush(); \
		print('downloaded %s' % f.name); \
		code = os.system('%s %s --user' % (sys.executable, f.name)); \
		f.close(); \
		sys.exit(code);"

setup-dev-env:  ## Install GIT hooks, pip, test deps (also upgrades them).
	${MAKE} install-git-hooks
	${MAKE} install-pip
	$(PYTHON) -m pip install $(INSTALL_OPTS) --upgrade pip
	$(PYTHON) -m pip install $(INSTALL_OPTS) --upgrade $(DEPS)

# ===================================================================
# Tests
# ===================================================================

test:  ## Run all tests.
	${MAKE} install
	$(TEST_PREFIX) $(PYTHON) $(TSCRIPT)

test-by-name:  ## e.g. make test-by-name ARGS=fastcopy.test.test_fastcopy.TestSomething
	${MAKE} install
	@$(TEST_PREFIX) $(PYTHON) -m unittest -v $(ARGS)

test-coverage:  ## Run test coverage.
	${MAKE} install
	# Note: coverage options are controlled by .coveragerc file
	rm -rf .coverage htmlcov
	$(TEST_PREFIX) $(PYTHON) -m coverage run $(TSCRIPT)
	$(PYTHON) -m coverage report
	@echo "writing results to htmlcov/index.html"
	$(PYTHON) -m coverage html
	$(PYTHON) -m webbrowser -t htmlcov/index.html

# ===================================================================
# Linters
# ===================================================================

pep8:  ## PEP8 linter.
	@git ls-files | grep \\.py$ | xargs $(PYTHON) -m pep8

pyflakes:  ## Pyflakes linter.
	@export PYFLAKES_NODOCTEST=1 && \
		git ls-files | grep \\.py$ | xargs $(PYTHON) -m pyflakes

flake8:  ## flake8 linter.
	@git ls-files | grep \\.py$ | xargs $(PYTHON) -m flake8

# ===================================================================
# GIT
# ===================================================================

git-tag-release:  ## Git-tag a new release.
	git tag -a release-`python -c "import setup; print(setup.get_version())"` -m `git rev-list HEAD --count`:`git rev-parse --short HEAD`
	git push --follow-tags

install-git-hooks:  ## Install GIT pre-commit hook.
	ln -sf ../../.git-pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

# ===================================================================
# Distribution
# ===================================================================

# --- create

sdist:  ## Create tar.gz source distribution.
	${MAKE} generate-manifest
	$(PYTHON) setup.py sdist

wheel:  ## Generate wheel.
	$(PYTHON) setup.py bdist_wheel

# --- upload

upload-src:  ## Upload source tarball on https://pypi.org/project/fastcopy/
	${MAKE} sdist
	$(PYTHON) setup.py sdist upload

# --- others

pre-release:  ## Check if we're ready to produce a new release.
	rm -rf dist
	${MAKE} install
	${MAKE} sdist
	$(PYTHON) -c "import subprocess, sys; out = subprocess.check_output('git diff --quiet && git diff --cached --quiet', shell=True).strip(); sys.exit('there are uncommitted changes:\n%s' % out) if out else 0 ;"

release:  ## Create a release (down/uploads tar.gz, wheels, git tag release).
	${MAKE} pre-release
	$(PYTHON) -m twine upload dist/*  # upload tar.gz and Windows wheels on PYPI
	${MAKE} git-tag-release

# ===================================================================
# Misc
# ===================================================================

grep-todos:  ## Look for TODOs in the source files.
	git grep -EIn "TODO|FIXME|XXX"

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
