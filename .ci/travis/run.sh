#!/bin/bash

set -e
set -x

PYVER=`python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'`

# setup OSX
if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate zerocopy
fi

# install zerocopy
make clean
python setup.py build
python setup.py develop

# run tests (with coverage)
if [[ $PYVER == '2.7' ]] && [[ "$(uname -s)" != 'Darwin' ]]; then
    python -Wa -m coverage run zerocopy/test/test_zerocopy.py
else
    python -Wa zerocopy/test/test_zerocopy.py
fi

if [ "$PYVER" == "2.7" ] || [ "$PYVER" == "3.6" ]; then
    # run linter (on Linux only)
    if [[ "$(uname -s)" != 'Darwin' ]]; then
        python -m flake8
    fi
fi
