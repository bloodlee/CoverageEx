__author__ = 'jason'

import unittest

from CoverageEx.report.ScriptCovInfo import ScriptCovInfo

class ScriptCovInfoTest(unittest.TestCase):

    def testConstructor1(self):
        info = ScriptCovInfo("script1", set())

        self.assertEqual(info.getScriptName(), "script1")
        self.assertEqual(info.getAllLines(), set())
        self.assertEqual(info.lineCount(), 0)

    def testConstructor2(self):
        info = ScriptCovInfo("script2", {1,1,3,4,5,5})

        self.assertEqual(info.getScriptName(), "script2")
        self.assertEqual(info.getAllLines(), {1,3,4,5})
        self.assertEqual(info.lineCount(), 4)