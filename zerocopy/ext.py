"""Expose low level _zerocopy C extension module APIs."""

import os

if os.name == 'posix':
    from _zerocopy import *  # NOQA
