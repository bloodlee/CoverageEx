__author__ = 'jasonlee'

import unittest
from CoverageEx.common.Range import Range

class RangeTest(unittest.TestCase):

    def setUp(self):
        self.aRange = Range(1, 10)

    def testInit(self):
        self.assertEqual(self.aRange.getFirst(), 1)
        self.assertEqual(self.aRange.getLast(), 10)

    def testInRange(self):
        self.assertTrue(self.aRange.contains(1))
        self.assertTrue(self.aRange.contains(10))
        self.assertTrue(self.aRange.contains(5))
        self.assertFalse(self.aRange.contains(0))
        self.assertFalse(self.aRange.contains(11))


