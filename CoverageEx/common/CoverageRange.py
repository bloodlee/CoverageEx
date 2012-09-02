__author__ = 'jason'

class CoverageRange(object):

    def __init__(self, scriptName, ranges=list()):

        self.scriptName = scriptName
        self.ranges = ranges

    def addRange(self, aRange):

        self.ranges.append(aRange)

    def getAllRanges(self):

        return self.ranges

    def inRange(self, aRange):

        # TODO: we can improve performance in future
        for bRange in self.ranges:
            if bRange.overlapped(aRange):
                return True

        return False

    def getScriptName(self):

        return self.scriptName