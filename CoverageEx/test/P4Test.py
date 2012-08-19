__author__ = 'jason'

import unittest
from CoverageEx.p4.P4Client import P4Client

class P4ClientTest(unittest.TestCase):

    def testGetRepositoryInfo(self):

        repository_path = P4Client.get_repository_info()
        if repository_path is None:
            print "Can't find p4 command."
        else:
            print repository_path

