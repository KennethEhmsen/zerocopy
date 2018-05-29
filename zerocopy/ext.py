"""Expose low level _zerocopy C extension module APIs."""

import os as _os

if _os.name == 'posix':
    from _zerocopy import *  # NOQA
