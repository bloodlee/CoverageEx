__author__ = 'jason'

import unittest
from CoverageEx.report.Parser import Parser
from CoverageEx.report.ScriptCovInfo import ScriptCovInfo
import os
from CoverageEx.db.TestCaseDB import TestCaseDB
from CoverageEx.common.Range import Range

DEFAULT_DB_NAME = 'test.sqlite'

class ReportParserTest(unittest.TestCase):

    #def tearDown(self):
    def setUp(self):
        self.fileContent = open('coverage.xml', 'r').read()

    def testReportOnlyOnePackage(self):
        result = Parser.parse(self.fileContent)

        self.assertEqual(len(result), 2)

        covInfo = result['hello.py']
        self.assertEqual(covInfo.getScriptName(), 'hello.py')
        self.assertEqual(covInfo.getAllLines(), {2,4,5,6,10,12,14,16,17,18})

    def testMerge(self):

        result = Parser.parse(self.fileContent)

        emptyLines = {
            'hello.py': [3,7,8,13,15,19]
        }

        scriptCoverRange = Parser.mergeEmptyLines(result, emptyLines)

        ranges = scriptCoverRange['hello.py']
        self.assertEqual(ranges[0], Range(2,8))
        self.assertEqual(ranges[1], Range(10, 10))
        self.assertEqual(ranges[2], Range(12,19))


    def testReportDataWithDb(self):
        db = TestCaseDB(DEFAULT_DB_NAME)

        result = Parser.parse(self.fileContent)

        db.refreshCoverageData(1, result)

        result2 = db.getCoverageData(1)

        self.assertEqual(len(result), len(result2))

        for fileName in result.keys():
            self.assertTrue(fileName in result2.keys())

            covInfo1 = result[fileName]
            covInfo2 = result2[fileName]

            self.assertTrue(covInfo1.getAllLines(), covInfo2.getAllLines())

