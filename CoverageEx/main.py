__author__ = 'jason'

import subprocess
from CoverageEx.report.Parser import Parser
from CoverageEx.file import EmptyLineFinder
from CoverageEx.db.TestCaseDB import TestCaseDB
from CoverageEx.p4.P4Client import P4Client

def readSessionIds():
    print 'Read configuration file to get all session ids...'
    # read from some file
    return [1,2,3,4]

def reCalcCoverageInfo(sessionId):
    print 'Run session %d and re-calculate the coverage info...' % sessionId

    # run coverage first
    subprocess.Popen("coverage run xxx.py %d" % id)

    # parse the coverage report
    # default report file name is 'coverage.xml'
    fileContent = open('coverage.xml', 'r').read()

    coverageInfo = Parser.parse(fileContent)

    for scriptName in coverageInfo.keys():
        # get empty lines of each script name
        emptyLines = EmptyLineFinder.findEmptyLines(scriptName)

        coverageInfo[scriptName] =\
            Parser.mergeEmptyLines(coverageInfo[scriptName], emptyLines)

    return coverageInfo

if __name__ == "__main__":

    # initialize the database
    print 'Initialize the database for test cases'
    caseDB = TestCaseDB('casedb.sqlite')

    print 'Get latest changelist from perforce...'
    # read current p4 info
    latest_cl = P4Client.getCurrentCL()

    sessionIds = readSessionIds()

    for sessionId in sessionIds:

        caseInfo = caseDB.getCaseInfo(sessionId)

        # currentCoverageInfo = caseDB.getCoverageData(sessionId)

        if caseInfo is None:
            print "Can't find session {0} info in database. Need rebuild it".format(sessionId)
            coverageInfo = reCalcCoverageInfo(sessionId)
            caseDB.refreshCoverageData(sessionId, coverageInfo)

        else:
            # if there exists coverage info.
            pass

        caseDB.refreshCaseInfo(sessionId, latest_cl)



    pass