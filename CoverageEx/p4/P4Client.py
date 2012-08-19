__author__ = 'jason'

import subprocess
import socket
import os
import sys
import re

DEBUG = True
def debug(s):
    if DEBUG:
        print ">>> %s" % s

class P4Client:

    @staticmethod
    def __check_install(command):

        try:
            p = subprocess.Popen(['p4', 'help'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

            return True

        except OSError:
            return False


    @staticmethod
    def __execute(command, env=None, split_lines=False, ignore_errors=False,
                extra_ignore_errors=()):
        """
        Utility function to execute a command and return the output.
        """
        if isinstance(command, list):
            debug(subprocess.list2cmdline(command))
        else:
            debug(command)

        if env:
            env.update(os.environ)
        else:
            env = os.environ.copy()

        env['LC_ALL'] = 'en_US.UTF-8'
        env['LANGUAGE'] = 'en_US.UTF-8'

        if sys.platform.startswith('win'):
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 shell=False,
                                 universal_newlines=True,
                                 env=env)
        else:
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 shell=False,
                                 close_fds=True,
                                 universal_newlines=True,
                                 env=env)
        if split_lines:
            data = p.stdout.readlines()
        else:
            data = p.stdout.read()
        rc = p.wait()
        if rc and not ignore_errors and rc not in extra_ignore_errors:
            die('Failed to execute command: %s\n%s' % (command, data))

        return data

    @staticmethod
    def get_repository_info():

        env = os.environ.copy()
        env['P4PORT'] = 'localhost:1666'

        if not P4Client.__check_install('p4 help'):
            return None

        data = P4Client.__execute(["p4", "info"], ignore_errors=True)

        m = re.search(r'^Server address: (.+)$', data, re.M)
        if not m:
            return None

        repository_path = m.group(1).strip()

        try:
            host, port = repository_path.split(":")
            info = socket.gethostbyaddr(host)
            repository_path = "%s:%s" % (info[0], port)
        except (socket.gaierror, socket.herror):
            pass

        return repository_path

    @staticmethod
    def getCurrentCL():

        env = os.environ.copy()
        env['P4PORT'] = 'localhost:1666'

        if not P4Client.__check_install('p4 help'):
            return None

        cl = P4Client.__execute(["p4", "counter", "change"], ignore_errors=True)

        return int(cl)

    @staticmethod
    def login(password):
        env = os.environ.copy()
        env['P4PORT'] = 'localhost:1666'
        env['P4PASSWD'] = 'iloveyou'

        P4Client.__execute("p4 login".split())

    @staticmethod
    def __get_ticket_value():
        ticket = P4Client.__execute("p4 login -p".split())
        return ticket

    @staticmethod
    def __open_workspace(ticket, workspace_name):
        command = "p4 -P %s workspace -o %s" % (ticket, workspace_name)

        P4Client.__execute(command.split())


if __name__=='__main__':
    print P4Client.get_repository_info()
