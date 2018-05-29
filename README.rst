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
In this early stage it starts as a backport of https://bugs.python.org/issue33671
for Python 2.7. Future development will probably include a backport of
`socket.sendfile()` https://bugs.python.org/issue17552.

What we have now
================

Copy file:

.. code-block:: python

    >>> import zerocopy
    >>> zerocopy.copy('src', 'dst')

What we may have tomorrow
=========================

Patch shutil module (all `copy*` functions):

.. code-block:: python

    >>> import zerocopy
    >>> zerocopy.patch_shutil()
    >>> import shutil
    >>> shutil.copy('src', 'dst')  # uses fastest version

Efficiently send file over socket (also on Windows via `TransmitFile`):

.. code-block:: python

    >>> import zerocopy, socket
    >>> sock = socket.create_connection(("127.0.0.1", 8000))
    >>> file = open('somefile', 'rb')
    >>> zerocopy.sendfile(sock, file)

Instantaneous CoW (Copy on Write) copy on filesystems supporting it:

.. code-block:: python

    >>> import zerocopy
    >>> zerocopy.cowcopy('src', 'dst')

Expose zero-copy low-level syscalls (...with `zerocopy` being the namespace
for higher-level wrappers around them):

.. code-block:: python

    >>> import zerocopy.ext
    >>> zerocopy.ext.sendfile
    <built-in function sendfile>
    >>> zerocopy.ext.copy_file_range  # Linux
    <built-in function copy_file_range>
    >>> zerocopy.ext.splice  # Linux
    <built-in function splice>
    >>> zerocopy.ext.tee  # Linux
    <built-in function tee>
    >>> zerocopy.ext.copyfile  # OSX
    <built-in function copyfile>
    >>> zerocopy.ext.fcopyfile  # OSX
    <built-in function fcopyfile>
    >>> zerocopy.ext.CopyFileW  # Windows
    <built-in function CopyFileW>
    >>> zerocopy.ext.TransmitFile  # Windows
    <built-in function TransmitFile>

