__author__ = 'jasonlee'

import unittest
from CoverageEx.common.Range import Range

class RangeTest(unittest.TestCase):

    def setUp(self):
        self.aRange = Range(1, 10)

    def testInit(self):
        self.assertEqual(self.aRange.getBegin(), 1)
        self.assertEqual(self.aRange.getEnd(), 10)

    def testInRange(self):
        self.assertTrue(self.aRange.inRange(1))
        self.assertTrue(self.aRange.inRange(10))
        self.assertTrue(self.aRange.inRange(5))
        self.assertFalse(self.aRange.inRange(0))
        self.assertFalse(self.aRange.inRange(11))


