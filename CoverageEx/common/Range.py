__author__ = 'jasonlee'

class Range:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def getBegin(self):
        return self.begin

    def getEnd(self):
        return self.end

    def inRange(self, num):
        return num >= self.begin and num <= self.end

    def __eq__(self, other):
        return self.begin == other.getBegin() and self.end == other.getEnd()


