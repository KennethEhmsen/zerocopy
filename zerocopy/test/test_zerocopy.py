import contextlib
import errno
import io
import os
import random
import shutil
import string
import sys
import tempfile
import unittest
import warnings

try:
    from unittest import mock  # py3
except ImportError:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import mock  # NOQA - requires "pip install mock"

import zerocopy
import _zerocopy
from zerocopy import _GiveupOnZeroCopy


TESTFN = "$testfile"
TESTFN2 = TESTFN + "2"
OSX = sys.platform.startswith("darwin")


# =====================================================================
# --- utils
# =====================================================================

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


def safe_remove(path):
    try:
        os.remove(path)
    except OSError as err:
        if err.errno != errno.ENOENT:
            raise

def supports_file2file_sendfile():
    # ...apparently Linux and Solaris are the only ones
    if not hasattr(_zerocopy, "sendfile"):
        return False
    srcname = None
    dstname = None
    try:
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            srcname = f.name
            f.write(b"0123456789")

        with open(srcname, "rb") as src:
            with tempfile.NamedTemporaryFile("wb", delete=False) as dst:
                dstname = f.name
                infd = src.fileno()
                outfd = dst.fileno()
                try:
                    _zerocopy.sendfile(outfd, infd, 0, 2)
                except OSError:
                    return False
                else:
                    return True
    finally:
        if srcname is not None:
            safe_remove(srcname)
        if dstname is not None:
            safe_remove(dstname)


SUPPORTS_SENDFILE = supports_file2file_sendfile()

# =====================================================================
# --- copyfiles() tests
# =====================================================================

class _ZeroCopyFileTest(object):
    """Tests common to all zero-copy APIs."""
    FILESIZE = (10 * 1024 * 1024)  # 10 MiB
    FILEDATA = b""
    PATCHPOINT = ""

    @classmethod
    def setUpClass(cls):
        write_test_file(TESTFN, cls.FILESIZE)
        with open(TESTFN, 'rb') as f:
            cls.FILEDATA = f.read()
            assert len(cls.FILEDATA) == cls.FILESIZE

    @classmethod
    def tearDownClass(cls):
        safe_remove(TESTFN)

    def tearDown(self):
        safe_remove(TESTFN2)

    @contextlib.contextmanager
    def get_files(self):
        with open(TESTFN, "rb") as src:
            with open(TESTFN2, "wb") as dst:
                yield (src, dst)

    def zerocopy_fun(self, *args, **kwargs):
        raise NotImplementedError("must be implemented in subclass")

    # ---

    def test_regular_copy(self):
        with self.get_files() as (src, dst):
            self.zerocopy_fun(src, dst)
        self.assertEqual(read_file(TESTFN2, binary=True), self.FILEDATA)

    @unittest.skipIf(os.name == 'nt', 'POSIX only')
    def test_non_regular_file_src(self):
        with io.BytesIO(self.FILEDATA) as src:
            with open(TESTFN2, "wb") as dst:
                with self.assertRaises(_GiveupOnZeroCopy):
                    self.zerocopy_fun(src, dst)
                shutil.copyfileobj(src, dst)

        self.assertEqual(read_file(TESTFN2, binary=True), self.FILEDATA)

    @unittest.skipIf(os.name == 'nt', 'POSIX only')
    def test_non_regular_file_dst(self):
        with open(TESTFN, "rb") as src:
            with io.BytesIO() as dst:
                with self.assertRaises(_GiveupOnZeroCopy):
                    self.zerocopy_fun(src, dst)
                shutil.copyfileobj(src, dst)
                dst.seek(0)
                self.assertEqual(dst.read(), self.FILEDATA)

    def test_non_existent_src(self):
        name = tempfile.mktemp()
        with self.assertRaises(IOError) as cm:
            zerocopy.copyfile(name, "new")
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        self.assertEqual(cm.exception.filename, name)

    def test_empty_file(self):
        srcname = TESTFN + 'src'
        dstname = TESTFN + 'dst'
        self.addCleanup(lambda: safe_remove(srcname))
        self.addCleanup(lambda: safe_remove(dstname))
        with open(srcname, "wb"):
            pass

        with open(srcname, "rb") as src:
            with open(dstname, "wb") as dst:
                self.zerocopy_fun(src, dst)

        self.assertEqual(read_file(dstname, binary=True), b"")

    def test_unhandled_exception(self):
        with mock.patch(self.PATCHPOINT,
                        side_effect=ZeroDivisionError):
            self.assertRaises(ZeroDivisionError,
                              zerocopy.copyfile, TESTFN, TESTFN2)

    @unittest.skipIf(os.name == 'nt', 'POSIX only')
    def test_exception_on_first_call(self):
        # Emulate a case where the first call to the zero-copy
        # function raises an exception in which case the function is
        # supposed to give up immediately.
        with mock.patch(self.PATCHPOINT,
                        side_effect=OSError(errno.EINVAL, "yo")):
            with self.get_files() as (src, dst):
                with self.assertRaises(_GiveupOnZeroCopy):
                    self.zerocopy_fun(src, dst)

    def test_filesystem_full(self):
        # Emulate a case where filesystem is full and sendfile() fails
        # on first call.
        with mock.patch(self.PATCHPOINT,
                        side_effect=OSError(errno.ENOSPC, "yo")):
            with self.get_files() as (src, dst):
                self.assertRaises(OSError, self.zerocopy_fun, src, dst)


@unittest.skipIf(not SUPPORTS_SENDFILE, 'sendfile() not supported')
class TestZeroCopySendfile(_ZeroCopyFileTest, unittest.TestCase):
    PATCHPOINT = "_zerocopy.sendfile"

    def zerocopy_fun(self, *args, **kwargs):
        return zerocopy._zerocopy_sendfile(*args, **kwargs)

    def test_exception_on_second_call(self):
        def sendfile(*args, **kwargs):
            if not flag:
                flag.append(None)
                return orig_sendfile(*args, **kwargs)
            else:
                raise OSError(errno.EBADF, "yo")

        flag = []
        orig_sendfile = _zerocopy.sendfile
        with mock.patch('_zerocopy.sendfile', create=True,
                        side_effect=sendfile):
            with self.get_files() as (src, dst):
                with self.assertRaises(OSError) as cm:
                    zerocopy._zerocopy_sendfile(src, dst)
        assert flag
        self.assertEqual(cm.exception.errno, errno.EBADF)

    def test_cant_get_size(self):
        # Emulate a case where src file size cannot be determined.
        # Internally bufsize will be set to a small value and
        # sendfile() will be called repeatedly.
        with mock.patch('os.fstat', side_effect=OSError) as m:
            with self.get_files() as (src, dst):
                zerocopy._zerocopy_sendfile(src, dst)
                assert m.called
        self.assertEqual(read_file(TESTFN2, binary=True), self.FILEDATA)

    def test_small_chunks(self):
        # Force internal file size detection to be smaller than the
        # actual file size. We want to force sendfile() to be called
        # multiple times, also in order to emulate a src fd which gets
        # bigger while it is being copied.
        mock_ = mock.Mock()
        mock_.st_size = 65536 + 1
        with mock.patch('os.fstat', return_value=mock_) as m:
            with self.get_files() as (src, dst):
                zerocopy._zerocopy_sendfile(src, dst)
                assert m.called
        self.assertEqual(read_file(TESTFN2, binary=True), self.FILEDATA)

    def test_big_chunk(self):
        # Force internal file size detection to be +100MB bigger than
        # the actual file size. Make sure sendfile() does not rely on
        # file size value except for (maybe) a better throughput /
        # performance.
        mock_ = mock.Mock()
        mock_.st_size = self.FILESIZE + (100 * 1024 * 1024)
        with mock.patch('os.fstat', return_value=mock_) as m:
            with self.get_files() as (src, dst):
                zerocopy._zerocopy_sendfile(src, dst)
                assert m.called
        self.assertEqual(read_file(TESTFN2, binary=True), self.FILEDATA)

    def test_blocksize_arg(self):
        with mock.patch('_zerocopy.sendfile',
                        side_effect=ZeroDivisionError) as m:
            self.assertRaises(ZeroDivisionError,
                              zerocopy.copyfile, TESTFN, TESTFN2)
            blocksize = m.call_args[0][3]
            # Make sure file size and the block size arg passed to
            # sendfile() are the same.
            self.assertEqual(blocksize, os.path.getsize(TESTFN))
            # ...unless we're dealing with a small file.
            safe_remove(TESTFN2)
            write_file(TESTFN2, b"hello", binary=True)
            self.addCleanup(safe_remove, TESTFN2 + '3')
            self.assertRaises(ZeroDivisionError,
                              zerocopy.copyfile, TESTFN2, TESTFN2 + '3')
            blocksize = m.call_args[0][3]
            self.assertEqual(blocksize, 2 ** 23)


@unittest.skipIf(not OSX, 'OSX only')
class TestZeroCopyOSX(_ZeroCopyFileTest, unittest.TestCase):
    PATCHPOINT = "_zerocopy.fcopyfile"

    def zerocopy_fun(self, *args, **kwargs):
        return zerocopy._zerocopy_osx(*args, **kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
