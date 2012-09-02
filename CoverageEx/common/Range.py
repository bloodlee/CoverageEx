__author__ = 'jasonlee'

import re

PATTERN = re.compile(r"\((\d+)-(\d+)\)")

class Range(object):
    """
    an integer range
    """

    @staticmethod
    def parseFrom(strRange):
        """
        Parse a range string and generate a range object
        """

        matcher = PATTERN.match(strRange)

        if len(matcher.groups()) != 2:
            return None
        else:
            return Range(int(matcher.group(1)), int(matcher.group(2)))


    def __init__(self, first, last):

        if first > last:
            tmp = last
            last = first
            first = tmp

        self.first = first
        self.last = last

    def getFirst(self):
        return self.first

    def getLast(self):
        return self.last

    def join(self, aRange):
        """
        Join two ranges.
        If failed, None will be returned.
        Else, a new joined range will be returned.
        """
        if self.contain(aRange):
            return self
        elif aRange.contain(self):
            return aRange
        elif self.nextTo(aRange) or self.overlapped(aRange):
            return Range(min(self.first, aRange.first), max(self.last, aRange.last))
        else:
            return None

    def overlapped(self, aRange):
        return not (self.first > aRange.last or self.last < aRange.first)

    def nextTo(self, aRange):
        return self.first - aRange.last == 1 or aRange.first - self.last == 1

    def contain(self, aRange):
        return (self.first <= aRange.first) and (self.last >= aRange.last)

    def __eq__(self, other):
        return self.first == other.first and self.last == other.last

    def __lt__(self, other):
        return self.first > other.first

    def __str__(self):
        return "(%d-%d)" % (self.first, self.last)
