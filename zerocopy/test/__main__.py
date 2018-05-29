#!/usr/bin/env python

import os
import unittest
import sys

HERE = os.path.abspath(os.path.dirname(__file__))


def get_suite():
    testmods = [os.path.splitext(x)[0] for x in os.listdir(HERE)
                if x.endswith('.py') and x.startswith('test_')]
    suite = unittest.TestSuite()
    for tm in testmods:
        # ...so that the full test paths are printed on screen
        tm = "zerocopy.test.%s" % tm
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(tm))
    return suite


def run_suite():
    result = unittest.TextTestRunner(verbosity=2).run(get_suite())
    success = result.wasSuccessful()
    sys.exit(0 if success else 1)


run_suite()
