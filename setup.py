#!/usr/bin/env python

import os
import sys
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        import setuptools
        from setuptools import setup
    except ImportError:
        setuptools = None
        from distutils.core import setup

    if os.name == 'posix':
        try:
            from setuptools import Extension
        except ImportError:
            Extension = None


if sys.version_info < (2, 7):
    sys.exit('python >= 2.7 only')

HERE = os.path.abspath(os.path.dirname(__file__))


def get_version():
    with open(os.path.join(HERE, 'zerocopy', '__init__.py'), 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                ret = eval(line.strip().split(' = ')[1])
                assert ret.count('.') == 2, ret
                for num in ret.split('.'):
                    assert num.isdigit(), ret
                return ret
        else:
            raise ValueError("couldn't find version string")


def get_description():
    with open(os.path.join(HERE, 'README.rst'), 'r') as f:
        return f.read()


VERSION = get_version()


def main():
    if os.name != 'posix':
        ext_modules = []
    else:
        ext_modules = [Extension('_zerocopy', ['zerocopy/_zerocopymodule.c'])]

    setup(
        name='zerocopy',
        version=VERSION,
        description='Provides efficient zero-copy capabilities for '
                    'shutil.copy* functions',
        long_description=get_description(),
        license='MIT',
        platforms='Platform Independent',
        author="Giampaolo Rodola'",
        author_email='g.rodola@gmail.com',
        url='https://github.com/giampaolo/zerocopy',
        ext_modules=ext_modules,
        install_requires=['six'],
        keywords=['zerocopy', 'sendfile', 'copyfile'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python',
            'Topic :: Security',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Libraries',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: Filesystems',
            'Topic :: Utilities',
        ],
    )


if __name__ == '__main__':
    main()
