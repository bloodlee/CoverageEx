__author__ = 'jason'

from xml.etree import ElementTree
from CoverageEx.report.ScriptCovInfo import ScriptCovInfo
from CoverageEx.common.Range import Range
from CoverageEx.common.CoverageRange import CoverageRange

COV_CLASS_XPATH='packages/package/classes/class'
LINE_RELATIVE_XPATH='lines/line'
FILENAME_PROP='filename'
LINE_NUM_PROP='number'
HITS_PROP='hits'

class Parser:
    @staticmethod
    def parse(fileContent):
        """
        Parse the report file content
        Return the result dict (key, value) = (script name, CovInfo)

        If the fileContent is None or empty, empty dict will be return.
        """
        result = {}
        if not fileContent:
            return result

        # parse the given content
        root = ElementTree.fromstring(fileContent)

        classElements = root.findall(COV_CLASS_XPATH)
        for anElement in classElements:
            scriptName = anElement.attrib[FILENAME_PROP]
            covInfo = ScriptCovInfo(scriptName, set())

            lines = anElement.findall(LINE_RELATIVE_XPATH)
            for aLine in lines:
                if aLine.attrib[HITS_PROP] != '0':
                    covInfo.addLine(int(aLine.attrib[LINE_NUM_PROP]))
            result[scriptName] = covInfo

        return result

    @staticmethod
    def mergeEmptyLines(fileCoverageInfo, fileEmptyLines):

        scriptCoverRange = {}

        for scriptName in fileCoverageInfo.keys():
            emptyLines = []
            if fileEmptyLines.has_key(scriptName):
                emptyLines = fileEmptyLines[scriptName]
                emptyLines.sort()

            emptyLinesSet = set(emptyLines)

            coverageLines = []
            for x in fileCoverageInfo[scriptName].getAllLines(): coverageLines.append(x)
            coverageLines.sort()
            coverageLinesSet = set(coverageLines)

            searchedLines = set()
            coverageRange = []

            for startLine in coverageLines:

                if startLine in searchedLines:
                    continue

                lineCounter = startLine
                endLine = startLine

                # check if next line is a empty line or a coverage line
                lineCounter += 1
                while True:
                    isEmptyLine = lineCounter in emptyLinesSet
                    isCoverageLine = lineCounter in coverageLinesSet

                    if isCoverageLine:
                        endLine = lineCounter
                        searchedLines.add(lineCounter)
                    elif isEmptyLine:
                        endLine = lineCounter
                    else:
                        break

                    endLine = lineCounter
                    lineCounter += 1

                newRange = Range(startLine, endLine)

                coverageRange.append(newRange)

            scriptCoverRange[scriptName] = CoverageRange(scriptName, coverageRange)

        return scriptCoverRange
