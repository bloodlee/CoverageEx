__author__ = 'jason'

import subprocess
from CoverageEx.report.Parser import Parser
from CoverageEx.file import EmptyLineFinder
from CoverageEx.db.TestCaseDB import TestCaseDB
from CoverageEx.common.FileChange import FileChange
from CoverageEx.common.Range import Range
from CoverageEx.common.CoverageRange import CoverageRange
import CoverageEx.p4 as p4

import os,os.path
import argparse
from Pexpect import pexpect
import string
import re
import sys
import Queue
import thread

DEBUG = False

def debug(info):
    if DEBUG:
        print '>>> %s' % info

def readSessionIds():
    print 'Read configuration file to get all session ids...'
    # read from some file
    return [1,2,3,4]

def genCoverageRcFileName(caseInfo):
    return 'coveragerc_%d' % caseInfo.getSeq()

def fillCoverageRcFile(rcFilename):

    rcFile = open(rcFilename, 'w')
    rcFile.write('[run]\n')
    rcFile.write('data_file = .coverage_%d' % caseInfo.getSeq())
    rcFile.close()

def removeAllRcFile():
    os.system('rm -rf coveragerc_*')

def runCase(caseInfo, pathRoot):

    command = caseInfo.getCommand()
    if command[0] != '/':
        command = os.path.join(pathRoot, command)

    rcFilename = genCoverageRcFileName(caseInfo)
    fillCoverageRcFile(rcFilename)

    # run coverage first
    finalCommand = 'coverage run --rcfile=%s %s' % (rcFilename, command)

    # redirect script output to log files
    logFile = open('case_log_%d.log' % caseInfo.getSeq(), 'w')

    return subprocess.Popen(finalCommand, stdout=logFile, stderr=logFile, shell=True)

def reCalcCoverageInfo(caseInfo):

    rcFilename = genCoverageRcFileName(caseInfo)

    coverageXmlFile = 'coverage_%d.xml' % caseInfo.getSeq()

    # generate coverage report
    os.system("coverage xml --rcfile=%s -o %s" % (rcFilename, coverageXmlFile))

    # parse the coverage report
    # default report file name is 'coverage.xml'
    fileContent = open(coverageXmlFile, 'r').read()

    coverageInfo = Parser.parse(fileContent)

    emptyLines = {}
    for scriptName in coverageInfo.keys():
        # get empty lines of each script name
        lines = EmptyLineFinder.findEmptyLines(scriptName)
        emptyLines[scriptName] = lines

    coverageInfo = Parser.mergeEmptyLines(coverageInfo, emptyLines)

    os.remove(rcFilename)
    os.remove(coverageXmlFile)

    return coverageInfo

def p4login(passwd):
    """
    Perforce login and get the ticket, which is valid for next 24 hours.
    """

    p = pexpect.spawn('p4 login -p')
    index = p.expect(["Enter password:", pexpect.EOF])
    if index == 0:
        debug('send password...')
        p.sendline(passwd)
        p.expect(pexpect.EOF)

    ticket = p.before

    if string.find(ticket, 'invalid') != -1:
        return None
    else:
        return ticket.strip()

def p4CounterChange(ticket):
    """
    Perforce counter change
    """
    command = 'p4 -P %s counter change' % ticket

    debug(command)

    p = pexpect.spawn(command)
    p.expect(pexpect.EOF)
    counterChange = p.before

    debug(p.before)

    return counterChange

def p4ChangeList(p4client, startCL, endCL, ticket):
    """
    Get p4 changelist related to given p4 client from startCL to endCL.
    """

    command = 'p4 -P %s -c %s changes -s submitted //%s/...@%d,@%s' % (ticket, p4client, p4client, startCL, endCL)

    p = pexpect.spawn(command)
    p.expect(pexpect.EOF)

    changeListInfo = p.before

    lines = changeListInfo.splitlines(True)

    changeListPattern = 'Change (\d+) on .*'

    clIds = []
    for line in lines:
        groups = re.match(changeListPattern, line)
        clIds.append(int(groups.group(1)))

    clIds.sort()

    return clIds

def p4DiffFile(p4client, clId, ticket):
    """
    Get diff
    """

    command = 'p4 -P %s -c %s describe %d' % (ticket, p4client, clId)

    p = pexpect.spawn(command)
    p.expect(pexpect.EOF)

    messages = p.before.splitlines(True)

    fileChanges = {}

    currentFileName = None

    for message in messages:

        message = message.strip()

        groups = re.match(p4.FILE_PATTERN, message)

        if groups is not None:

            depotFilePath = groups.group(1)

            currentFileName = p4LocalPath(p4client, depotFilePath, ticket)

            if not currentFileName:
                debug("Can't find the local path of given file") # actually, it's impossible.
                sys.exit(1)

            fileChanges[currentFileName] = []
            continue

        groups = re.match(p4.DIFF_PATTERN, message)
        if groups is not None:

            src = groups.group(1)
            mode = groups.group(2)
            dest = groups.group(3)

            srcLines = src.split(',')
            destLines = dest.split(',')

            srcRange = None
            if len(srcLines) == 1:
                srcRange = Range(int(srcLines[0]), int(srcLines[0]))
            else:
                srcRange = Range(int(srcLines[0]), int(srcLines[1]))

            destRange = None
            if len(destLines) == 1:
                destRange = Range(int(destLines[0]), int(destLines[0]))
            else:
                destRange = Range(int(destLines[0]), int(destLines[1]))


            if currentFileName:
                fileChanges[currentFileName].append(FileChange(srcRange, destRange, mode))

            continue

    return fileChanges

def p4LocalPath(p4client, repoPath, ticket):
    """
    Get the local path of given repo path.
    """

    command = 'p4 -P %s -c %s where %s' % (ticket, p4client, repoPath)

    p = pexpect.spawn(command)
    p.expect(pexpect.EOF)

    # there are three path, depo path, workspace path and local path
    # we only need the local path.

    if p.before.find('refer to') != -1:
        return None

    paths = p.before.split()

    return paths[2]

def p4ClientRoot(p4client, ticket):
    """
    Get client root.
    """

    command = 'p4 -P %s client -o %s' % (ticket, p4client)

    p = pexpect.spawn(command)
    p.expect(pexpect.EOF)

    lines = p.before.splitlines()

    for line in lines:

        groups = re.match(p4.CLIENT_ROOT, line)

        if groups:
            client_root = groups.group(1)
            return client_root.strip()

    return ''

def isCodeChanged(coverRange, diffInfo):

    for aDiffInfo in diffInfo:
        if coverRange.inRange(aDiffInfo.getSrcRange()):
            return True

    return False

def runCoverage(caseDB, caseInfo, latestCL, scriptFolder):
    coverageInfo = reCalcCoverageInfo(caseIno)
    caseDB.refreshCoverageData(caseInfo.getSeq(), coverageInfo)
    caseDB.refreshCaseInfo(caseInfo.getSeq(), latestCL)

def processWaiter(popen, proc_queue, caseInfo):
    try:
        popen.wait()
    finally:
        proc_queue.put(("Case '%s' finished." % caseInfo.getName(), popen.returncode))

if __name__ == "__main__":

    description= 'Coverage-info based automation test script'

    #version = '1.0'

    parser = argparse.ArgumentParser(description=description) #, version=version)

    parser.add_argument('-p4client', type=str, help='p4 client', required=True)
    parser.add_argument('-p4passwd', type=str, help='p4 password', required=False)
    parser.add_argument('-p4port',   default='localhost:1666', type=str, help='p4 port', required=False)
    parser.add_argument('-p4user',   default='jason', type=str, help='p4 user', required=False)
    parser.add_argument('-init', default=False, type=bool, help='Initialize case', required=False)
    parser.add_argument('-lt_port', type=str, help='LithoTuner Port', required=False)

    options = parser.parse_args()

    # set environment for perforce
    if options.p4client:
        os.environ['P4CLIENT'] = options.p4client

    if options.p4passwd:
        os.environ['P4PASSWD'] = options.p4passwd

    if options.p4port:
        os.environ['P4PORT'] = options.p4port

    if options.p4user:
        os.environ['P4USER'] = options.p4user

    # initialize the database
    print ('Connect the database for test cases...')
    caseDB = TestCaseDB('casedb.sqlite')

    if options.init:
        print ('Initialize database...')
        caseDB.initDB()
        caseDB.addCase('Test Hello.py 1', 'hello.py')
        caseDB.addCase('Test Hello.py 2', 'hello.py')
        caseDB.addCase('Test Hello.py 3', 'hello.py')

    cases = caseDB.getCaseInfo()

    if not len(cases):
        print ("Can't find any cases in databases.")
        sys.exit(0)

    ticket = p4login(options.p4passwd)

    if not ticket:
        debug('p4 login failed!')
        sys.exit(1)

    counterChange = p4CounterChange(ticket)

    # p4 sync
    print 'Sync code to latest...'
    os.system("p4 -P %s -c %s sync" % (ticket, options.p4client))

    clientRoot = p4ClientRoot(options.p4client, ticket)

    first_run_set = []
    diff_run_set = []
    skipped_set = []
    print 'Go through all cases...'

    for caseInfo in cases:
        if caseInfo.getLastCL() == 0:
            first_run_set.append(caseInfo)
            continue

        if caseInfo.getLastCL() < int(counterChange):
            diff_run_set.append(caseInfo)
            continue
        else:
            skipped_set.append(caseInfo)

    first_run_set.sort()
    diff_run_set.sort()
    skipped_set.sort()

    totalProcCount = 0
    results = Queue.Queue()
    print 'First Run Cases...'
    for caseInfo in first_run_set:
        p = runCase(caseInfo, clientRoot)
        #p = Process(target=runCase, args=(caseInfo, clientRoot))
        thread.start_new_thread(processWaiter, (p, results, caseInfo))
        totalProcCount += 1

    print 'waiting...'
    while totalProcCount:
        description, rc = results.get()
        print description
        totalProcCount -= 1

    print "Parse each case's coverage info..."
    for caseInfo in first_run_set:
        coverageInfo = reCalcCoverageInfo(caseInfo)
        caseDB.refreshCoverageData(caseInfo.getSeq(), coverageInfo)
        caseDB.refreshCaseInfo(caseInfo.getSeq(), int(counterChange))

    rerun_case_set = []

    print 'Diff Cases...'
    for caseInfo in diff_run_set:
        print ('\tTry to get difference...')
        changeListIds = p4ChangeList(options.p4client, caseInfo.getLastCL(), counterChange, ticket)

        if len(changeListIds):
            print ('\tload coverage from database...')

            coverageInfo = caseDB.getCoverageData(caseInfo.getSeq())

            print ('\tGo through each changelist...')
            for clId in changeListIds:
                diffInfo = p4DiffFile(options.p4client, clId, ticket)

                triggered = False
                for aFile in diffInfo.keys():
                    if coverageInfo.has_key(aFile):
                        if isCodeChanged(coverageInfo[aFile], diffInfo[aFile]):
                            rerun_case_set.append(caseInfo)
                            triggered = True
                            break

                if triggered:
                    break


    for caseInfo in skipped_set:
        print "\tCase '%s' is up-to-date. Skip it." % caseInfo.getName()

    if len(rerun_case_set):

        rerun_case_set.sort()

        totalProcCount = 0
        results = Queue.Queue()
        for caseInfo in rerun_case_set:
            p = runCase(caseInfo, clientRoot)
            #p = Process(target=runCase, args=(caseInfo, clientRoot))
            thread.start_new_thread(processWaiter, (p, results, caseInfo))
            totalProcCount += 1

        print 'waiting...'
        while totalProcCount:
            description, rc = results.get()
            print description
            totalProcCount -= 1

        for caseInfo in rerun_case_set:
            coverageInfo = reCalcCoverageInfo(caseInfo)
            caseDB.refreshCoverageData(caseInfo.getSeq(), coverageInfo)
            caseDB.refreshCaseInfo(caseInfo.getSeq(), int(counterChange))

        print ('Done.')

    else:
        print "Nothing need to be re-run."