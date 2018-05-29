.. image:: https://img.shields.io/travis/giampaolo/zeroconf/master.svg?maxAge=3600&label=Linux%20/%20OSX
    :target: https://travis-ci.org/giampaolo/zeroconf
    :alt: Linux and OSX tests (Travis)

.. image:: https://img.shields.io/appveyor/ci/giampaolo/zeroconf/master.svg?maxAge=3600&label=Windows
    :target: https://ci.appveyor.com/project/giampaolo/zeroconf
    :alt: Windows tests (Appveyor)

.. image:: https://coveralls.io/repos/github/giampaolo/zeroconf/badge.svg?branch=master
    :target: https://coveralls.io/github/giampaolo/zeroconf?branch=master
    :alt: Test coverage (coverall.io)

.. image:: https://readthedocs.org/projects/zeroconf/badge/?version=latest
    :target: http://zeroconf.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/zeroconf.svg?label=pypi
    :target: https://pypi.org/project/zeroconf
    :alt: Latest version

.. image:: https://img.shields.io/github/stars/giampaolo/zeroconf.svg
    :target: https://github.com/giampaolo/zeroconf/
    :alt: Github stars

.. image:: https://img.shields.io/pypi/l/zeroconf.svg
    :target: https://pypi.org/project/zeroconf
    :alt: License

About
=====

zerocopy is a Python library which provides a more efficient way for copying
files in Python, speeding up `shutil.copy*` functions considerably.
Copy file:

.. code-block:: python

    >>> import zerocopy
    >>> zerocopy.copy('src', 'dst')

Patch shutil module (all `copy*` functions):

.. code-block:: python

    >>> import zerocopy
    >>> zerocopy.patch_shutil()
    >>> import shutil
    >>> shutil.copy('src', 'dst')  # uses fastest version
