.. image:: https://img.shields.io/travis/giampaolo/zerocopy/master.svg?maxAge=3600&label=Linux%20/%20OSX
    :target: https://travis-ci.org/giampaolo/zerocopy
    :alt: Linux and OSX tests (Travis)

.. image:: https://img.shields.io/appveyor/ci/giampaolo/zerocopy/master.svg?maxAge=3600&label=Windows
    :target: https://ci.appveyor.com/project/giampaolo/zerocopy
    :alt: Windows tests (Appveyor)

.. image:: https://coveralls.io/repos/github/giampaolo/zerocopy/badge.svg?branch=master
    :target: https://coveralls.io/github/giampaolo/zerocopy?branch=master
    :alt: Test coverage (coverall.io)

.. image:: https://readthedocs.org/projects/zerocopy/badge/?version=latest
    :target: http://zerocopy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/zerocopy.svg?label=pypi
    :target: https://pypi.org/project/zerocopy
    :alt: Latest version

.. image:: https://img.shields.io/github/stars/giampaolo/zerocopy.svg
    :target: https://github.com/giampaolo/zerocopy/
    :alt: Github stars

.. image:: https://img.shields.io/pypi/l/zerocopy.svg
    :target: https://pypi.org/project/zerocopy
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
