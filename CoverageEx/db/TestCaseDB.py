__author__ = 'jasonlee'

import sqlite3
import string
from CoverageEx.report.ScriptCovInfo import ScriptCovInfo
from CoverageEx.common.CaseInfo import CaseInfo

class TestCaseDB:

    CASE_COVERAGE_TABLE_NAME = "case_coverage"

    CREATE_COVERAGE_TABLE_SQL="""
    CREATE TABLE IF NOT EXISTS {0}
    (case_seq INTEGER PRIMARY KEY AUTOINCREMENT,
    package VARCHAR(255) DEFAULT NULL,
    file VARCHAR(255) DEFAULT '',
    line TEXT,
    last_changelist INT)
    """.format(CASE_COVERAGE_TABLE_NAME)

    CASE_TABLE_NAME = "test_cases"

    CREATE_CASE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS {0}
    (case_seq INTEGER PRIMARY KEY AUTOINCREMENT,
    case_name VARCHAR(255),
    case_command VARCHAR(255),
    last_cl INT DEFAULT 0)
    """.format(CASE_TABLE_NAME)

    def __init__(self, dbName):
        self.dbName = dbName

        self.conn = sqlite3.connect(self.dbName)

        c = self.conn.cursor()

        c.execute(TestCaseDB.CREATE_COVERAGE_TABLE_SQL)
        c.execute(TestCaseDB.CREATE_CASE_TABLE_SQL)

        self.conn.commit()

    def closeDB(self):
        self.conn.close()

    def initDB(self):
        c = self.conn.cursor()

        c.execute('DROP TABLE {0}'.format(TestCaseDB.CASE_COVERAGE_TABLE_NAME))
        c.execute(TestCaseDB.CREATE_COVERAGE_TABLE_SQL)
        c.execute('DROP TABLE {0}'.format(TestCaseDB.CASE_TABLE_NAME))
        c.execute(TestCaseDB.CREATE_CASE_TABLE_SQL)

        self.conn.commit()

    def addCase(self, name, command):
        """
        Add case
        """

        c = self.conn.cursor()

        insert_sql = """
        INSERT INTO %s
        (case_name, case_command) values
        (?, ?)
        """ % (TestCaseDB.CASE_TABLE_NAME)

        c.execute(insert_sql, (name, command))

        self.conn.commit()

    def getCaseInfo(self):
        """
        Get case info.
        """
        c = self.conn.cursor()

        SELECT_SQL = """
        SELECT * FROM {0}
        """.format(TestCaseDB.CASE_TABLE_NAME)

        rows = c.execute(SELECT_SQL)

        cases = []
        for row in rows:
            testCase = CaseInfo(row[0], row[1], row[2], row[3])
            cases.append(testCase)

        return cases

    def refreshCaseInfo(self, testCaseSeq, last_cl):
        # update the last cl.
        c = self.conn.cursor()

        command = 'UPDATE %s SET last_cl = ? WHERE case_seq = ?' % TestCaseDB.CASE_TABLE_NAME
        c.execute(command, (last_cl, testCaseSeq))

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

