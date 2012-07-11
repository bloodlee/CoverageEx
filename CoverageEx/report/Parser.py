__author__ = 'jason'

from xml.etree import ElementTree
from CoverageEx.report.ScriptCovInfo import ScriptCovInfo

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
