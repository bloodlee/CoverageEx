__author__ = 'jason'

from CoverageEx.common.Range import Range

class ScriptCovInfo:
    """
    Class which is used to store the information of script coverage.
    """
    def __init__(self, scriptName, lines):
        """
        Constructor of script info.
        Initialize the lines as a set.
        """
        self.scriptName = scriptName
        self.lines = lines
        self.ranges = []

    def getScriptName(self):
        """
        Get the script name.
        """
        return self.scriptName

    def addLine(self, lineNo):
        """
        Add a new line number.
        """
        self.lines.add(lineNo)

    def addRange(self, range):
        """
        Add a coverage range.
        """
        self.ranges.add(range)

    def containLine(self, lineNo):
        """
        Test whether the give line number is contained.
        """
        return lineNo in self.lines

    def getAllLines(self):
        """
        Get all lines.
        """
        return self.lines

    def getAllRanges(self):
        return self.ranges

    def lineCount(self):
        """
        Get the line count
        """
        return len(self.lines)

    def __str__(self):
        return "Script Name: {0} Coverage Lines: {1}".format(self.scriptName, self.getAllLines())

