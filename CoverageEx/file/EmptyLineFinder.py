__author__ = 'jasonlee'

import os.path
import string

def findEmptyLines(filename):
    """
    File the emtpy lines in files.
    'filename' is the given absolute file name.
    """

    if not os.path.exists(filename):
        return []

    # open file
    scriptFile = open(filename, 'r')

    emptyLines = []

    lineIndex = 1
    content = scriptFile.readlines(50)
    while content:
        for aLine in content:
            aLine = string.strip(aLine)

            if not aLine:
                emptyLines.append(lineIndex)

            lineIndex += 1

        content = scriptFile.readlines(50)

    return emptyLines