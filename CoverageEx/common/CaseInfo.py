__author__ = 'jason'

class CaseInfo(object):

    def __init__(self, seq, name, command, lastCL):

        self.seq = seq
        self.name = name
        self.command = command
        self.lastCL = lastCL

    def getSeq(self):
        return self.seq

    def getName(self):
        return self.name

    def getCommand(self):
        return self.command

    def getLastCL(self):
        return self.lastCL

    def __lt__(self, other):
        return self.seq < other.getSeq()
