#!/bin/bash

set -e
set -x

uname -a
python -c "import sys; print(sys.version)"

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

    case "${PYVER}" in
        py27)
            pyenv install 2.7.10
            pyenv virtualenv 2.7.10 zerocopy
            ;;
        py34)
            pyenv install 3.4.3
            pyenv virtualenv 3.4.3 zerocopy
            ;;
    esac
    pyenv rehash
    pyenv activate zerocopy
fi

if [[ $TRAVIS_PYTHON_VERSION == '2.6' ]] || [[ $PYVER == 'py26' ]]; then
    pip install -U unittest2 mock==1.0.1
elif [[ $TRAVIS_PYTHON_VERSION == '2.7' ]] || [[ $PYVER == 'py27' ]]; then
    pip install -U mock
fi

pip install -U coverage coveralls flake8 pep8 setuptools
