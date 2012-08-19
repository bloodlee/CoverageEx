__author__ = 'jasonlee'

import unittest
import os
import CoverageEx.file.EmptyLineFinder as finder


class EmptyLineFinderTest(unittest.TestCase):

    FILE_NAME = "test.test"

    def setUp(self):
        fileObj = open(EmptyLineFinderTest.FILE_NAME, 'w')

        fileObj.write('\t\n')
        fileObj.write('    \n')
        fileObj.write('abcdefg\n')
        fileObj.write('\n')

    def tearDown(self):
        os.remove(EmptyLineFinderTest.FILE_NAME)

    def testFind(self):

        lines = finder.findEmptyLines(EmptyLineFinderTest.FILE_NAME)

        self.assertEqual(lines, [1,2,4])
