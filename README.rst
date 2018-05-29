About
=====

zerocopy is a Python library which provides a more efficient way for copying
files in Python, speeding up `shutil.copy*` considerably.
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
