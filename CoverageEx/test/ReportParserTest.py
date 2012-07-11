__author__ = 'jason'

import unittest
from CoverageEx.report.Parser import Parser
from CoverageEx.report.ScriptCovInfo import ScriptCovInfo

class ReportParserTest(unittest.TestCase):

    def testReportOnlyOnePackage(self):
        fileContent = open('coverage.xml', 'r').read()

        result = Parser.parse(fileContent)

        self.assertEqual(len(result), 2)

        covInfo = result['hello.py']
        self.assertEqual(covInfo.getScriptName(), 'hello.py')
        self.assertEqual(covInfo.getAllLines(), {2,4,5,6,10,12,14,16,17,18})

        print covInfo

        covInfo = result['hello1.py']
        print covInfo