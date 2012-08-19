__author__ = 'jason'

class FileChange(object):

    ADD = 0x01
    CHANGE = 0x10
    DELETE = 0x11

    def __init__(self, srcRange, destRange, changeMode):
        self.srcRange = srcRange
        self.destRange = destRange
        self.changeMode = changeMode

    def getSrcRange(self):
        return self.srcRange

    def getDestRange(self):
        return self.destRange

    def getChangeMode(self):
        return self.changeMode