__author__ = 'jasonlee'

class Range:
    def __init__(self, first, last):
        self.first = first
        self.last = last

    def getFirst(self):
        return self.first

    def getLast(self):
        return self.last

    def contains(self, num):
        return num >= self.first and num <= self.last

    def hasInsect(self, otherRange):
        return not (self.last > otherRange.getFirst() or self.first < otherRange.getLast())

    def __eq__(self, other):
        return self.first == other.getFirst() and self.last == other.getLast()

    def __lt__(self, other):
        return self.first > other.getFirst

    def __str__(self):
        if self.first == self.last:
            return self.first
        else:
            return "%d-%d" % (self.first, self.last)

