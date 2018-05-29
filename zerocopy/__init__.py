from zerocopy._copyfile import copyfile  # NOQA
from zerocopy._copyfile import SameFileError  # NOQA
from zerocopy._copyfile import SpecialFileError  # NOQA

__version__ = "0.1.0"
version_info = tuple([int(num) for num in __version__.split('.')])
__all__ = [
    "SpecialFileError", "SameFileError"
    "copyfile"]
