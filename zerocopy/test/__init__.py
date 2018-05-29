import errno
import os
import random
import string
import sys
import warnings

try:
    from unittest import mock  # py3
except ImportError:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import mock  # NOQA - requires "pip install mock"


TESTFN = "$testfile"
TESTFN2 = TESTFN + "2"
OSX = sys.platform.startswith("darwin")
POSIX = os.name == "posix"
WINDOWS = os.name == "nt"
LINUX = sys.platform.startswith("linux")
PY3 = sys.version_info[0] == 3


# =====================================================================
# --- fs utils
# =====================================================================


def safe_remove(path):
    try:
        os.remove(path)
    except OSError as err:
        if err.errno != errno.ENOENT:
            raise


def write_file(path, content, binary=False):
    """Write *content* to a file located at *path*.

    If *path* is a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* is true, the file will be opened in binary
    mode.
    """
    if isinstance(path, tuple):
        path = os.path.join(*path)
    with open(path, 'wb' if binary else 'w') as fp:
        fp.write(content)


def write_test_file(path, size):
    """Create a test file with an arbitrary size and random text content."""
    def chunks(total, step):
        assert total >= step
        while total > step:
            yield step
            total -= step
        if total:
            yield total

    bufsize = min(size, 8192)
    chunk = b"".join([random.choice(string.ascii_letters).encode()
                      for i in range(bufsize)])
    with open(path, 'wb') as f:
        for csize in chunks(size, bufsize):
            f.write(chunk)
    assert os.path.getsize(path) == size


def read_file(path, binary=False):
    """Return contents from a file located at *path*.

    If *path* is a tuple instead of a string, os.path.join will be used to
    make a path.  If *binary* is true, the file will be opened in binary
    mode.
    """
    if isinstance(path, tuple):
        path = os.path.join(*path)
    with open(path, 'rb' if binary else 'r') as fp:
        return fp.read()


def assert_files_equal(src, dst):
    with open(src, "rb") as a:
        with open(dst, "rb") as b:
            if a.read() != b.read():
                raise AssertionError("%s and %s files are not equal")
