import os
import shutil
import stat
import errno

import six

import _zerocopy

__version__ = "0.1.0"
version_info = tuple([int(num) for num in __version__.split('.')])
_HAS_SENDFILE = hasattr(_zerocopy, "sendfile")
_HAS_FCOPYFILE = hasattr(_zerocopy, "fcopyfile")

__all__ = [
    "SpecialFileError", "SameFileError"
    "copyfile"]

# =====================================================================
# --- shutil module compatibility between Python 2 and 3
# =====================================================================

if hasattr(shutil, "SpecialFileError"):
    class SpecialFileError(shutil.SpecialFileError):
        __doc__ = shutil.SpecialFileError.__doc__
else:
    class SpecialFileError(shutil.Error):
        """Raised when trying to do a kind of operation (e.g. copying)
        which is not supported on a special file (e.g. a named pipe)"""

if hasattr(shutil, "SameFileError"):
    class SameFileError(shutil.SameFileError):
        __doc__ = shutil.SameFileError.__doc__
else:
    class SameFileError(shutil.Error):
        """Raised when source and destination are the same file."""

class _GiveupOnZeroCopy(Exception):
    """Raised as a signal to fallback on using raw file copy
    when zero-copy functions fail to do so.
    """


def _samefile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))

# =====================================================================
# --- Implementation
# =====================================================================

def _zerocopy_osx(fsrc, fdst):
    raise NotImplementedError  # TODO


def _zerocopy_win(src, dst):
    raise NotImplementedError  # TODO


def _zerocopy_sendfile(fsrc, fdst):
    """Copy data from one regular mmap-like fd to another by using
    high-performance sendfile() method.
    This should work on Linux >= 2.6.33 and Solaris only.
    """
    global _HAS_SENDFILE
    try:
        infd = fsrc.fileno()
        outfd = fdst.fileno()
    except Exception as err:
        raise _GiveupOnZeroCopy(err)  # not a regular file

    # Hopefully the whole file will be copied in a single call.
    # sendfile() is called in a loop 'till EOF is reached (0 return)
    # so a bufsize smaller or bigger than the actual file size
    # should not make any difference, also in case the file content
    # changes while being copied.
    try:
        blocksize = max(os.fstat(infd).st_size, 2 ** 23)  # min 8MB
    except Exception:
        blocksize = 2 ** 27  # 128MB

    offset = 0
    while True:
        try:
            sent = _zerocopy.sendfile(outfd, infd, offset, blocksize)
        except OSError as err:
            if err.errno == errno.ENOTSOCK:
                # sendfile() on this platform (probably Linux < 2.6.33)
                # does not support copies between regular files (only
                # sockets).
                _HAS_SENDFILE = False
                raise _GiveupOnZeroCopy(err)

            if err.errno == errno.ENOSPC:  # filesystem is full
                six.raise_from(err, None)

            # Give up on first call and if no data was copied.
            if offset == 0 and os.lseek(outfd, 0, os.SEEK_CUR) == 0:
                raise _GiveupOnZeroCopy(err)

            six.raise_from(err, None)
        else:
            if sent == 0:
                break  # EOF
            offset += sent

def _copyfileobj2(fsrc, fdst):
    """Copy 2 regular mmap-like fds by using zero-copy sendfile(2)
    (Linux) and fcopyfile(2) (OSX) syscalls.
    In case of error fallback on using plain read()/write() if no
    data was copied.
    """
    # Note: copyfileobj() is left alone in order to not introduce any
    # unexpected breakage. Possible risks by using zero-copy calls
    # in copyfileobj() are:
    # - fdst cannot be open in "a"(ppend) mode
    # - fsrc and fdst may be open in "t"(ext) mode
    # - fsrc may be a BufferedReader (which hides unread data in a buffer),
    #   GzipFile (which decompresses data), HTTPResponse (which decodes
    #   chunks).
    # - possibly others
    if _HAS_SENDFILE:
        try:
            return _zerocopy_sendfile(fsrc, fdst)
        except _GiveupOnZeroCopy:
            pass

    if _HAS_FCOPYFILE:
        try:
            return _zerocopy_osx(fsrc, fdst)
        except _GiveupOnZeroCopy:
            pass

    return shutil.copyfileobj(fsrc, fdst)


def copyfile(src, dst, follow_symlinks=True):
    """Copy data from src to dst in the most efficient way possible.

    Internally, platform-specific zero-copy syscalls [1] are used by
    default on Linux, OSX and Windows.
    Fallback on using plain read() / write() variant in case the
    zero-copy operation fails.

    If follow_symlinks is not set and src is a symbolic link, a new
    symlink will be created instead of copying the file it points to.
    """
    if _samefile(src, dst):
        raise SameFileError("%r and %r are the same file" % (src, dst))

    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass
        else:
            # XXX What about other special files? (sockets, devices...)
            if stat.S_ISFIFO(st.st_mode):
                raise SpecialFileError("`%s` is a named pipe" % fn)

    if not follow_symlinks and os.path.islink(src):
        os.symlink(os.readlink(src), dst)
    else:
        if os.name == 'nt':
            _zerocopy_win(src, dst)
            return dst

        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                _copyfileobj2(fsrc, fdst)
    return dst
