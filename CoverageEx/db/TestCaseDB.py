__author__ = 'jasonlee'

import sqlite3
import string
from CoverageEx.report.ScriptCovInfo import ScriptCovInfo

class TestCaseDB:

    CASE_COVERAGE_TABLE_NAME = "case_coverage"

    CREATE_COVERAGE_TABLE_SQL="""
    CREATE TABLE IF NOT EXISTS {0}
    (case_seq INT,
    package VARCHAR(255) DEFAULT NULL,
    file VARCHAR(255) DEFAULT '',
    line TEXT)
    """.format(CASE_COVERAGE_TABLE_NAME)

    def __init__(self, dbName):
        self.dbName = dbName

        self.conn = sqlite3.connect(self.dbName)

        c = self.conn.cursor()
        c.execute(TestCaseDB.CREATE_COVERAGE_TABLE_SQL)
        self.conn.commit()

    def refreshCoverageData(self, testCaseSeq, covInfo):
        """
        Refresh coverage data.
        covInfo is a dict, key is file name, value is a coverage info.
        """
        c = self.conn.cursor()

        REMOVE_DATA_SQL="""
        DELETE FROM {0}
        WHERE case_seq = {1}
        """.format(TestCaseDB.CASE_COVERAGE_TABLE_NAME, testCaseSeq)

        c.execute(REMOVE_DATA_SQL)
        self.conn.commit()

        for aFile in covInfo.keys():

            aCovInfo = covInfo[aFile]

            INSERT_SQL = """
            INSERT INTO {0}
            (case_seq, file, line)
            VALUES ({1}, '{2}', '{3}')
            """.format(TestCaseDB.CASE_COVERAGE_TABLE_NAME, testCaseSeq, aFile, str(aCovInfo.getAllLines())[5:-2])

            c.execute(INSERT_SQL)

        self.conn.commit()

    def getCoverageData(self, testCaseSeq):
        c = self.conn.cursor()

        SELECT_SQL = """
        SELECT file, line FROM {0}
        WHERE case_seq = {1}
        """.format(TestCaseDB.CASE_COVERAGE_TABLE_NAME, testCaseSeq)

        c.execute(SELECT_SQL)

        result = {}
        row = c.fetchone()
        while row:
            scriptName = row[0]
            lineSet = set(string.split(row[1]))

            covInfo = ScriptCovInfo(scriptName, lineSet)

            result[scriptName] = covInfo

            row = c.fetchone()

        return result

