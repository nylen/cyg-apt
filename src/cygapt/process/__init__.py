# -*- coding: utf-8 -*-
######################## BEGIN LICENSE BLOCK ########################
# This file is part of the cygapt package.
#
# Copyright (C) 2002-2009 Jan Nieuwenhuizen  <janneke@gnu.org>
#               2002-2009 Chris Cormie       <cjcormie@gmail.com>
#                    2012 James Nylen        <jnylen@gmail.com>
#               2012-2014 Alexandre Quercia  <alquerci@email.com>
#
# For the full copyright and license information, please view the
# LICENSE file that was distributed with this source code.
######################### END LICENSE BLOCK #########################

from __future__ import absolute_import;


import subprocess;
import shlex;

from .exception import ProcessFailedException;
from .exception import LogicException;

class Process:
    """Process is a thin wrapper around subprocess.* functions.

    @author: alquerci <alquerci@email.com>
    """

    exitCodes = {
        0: 'OK',
        1: 'General error',
        2: 'Misuse of shell builtins',

        # User-defined errors must use exit codes in the 64-113 range.

        126: 'Invoked command cannot execute',
        127: 'Command not found',
        128: 'Invalid exit argument',

        # signals
        129: 'Hangup',
        130: 'Interrupt',
        131: 'Quit and dump core',
        132: 'Illegal instruction',
        133: 'Trace/breakpoint trap',
        134: 'Process aborted',
        135: 'Bus error: "access to undefined portion of memory object"',
        136: 'Floating point exception: "erroneous arithmetic operation"',
        137: 'Kill (terminate immediately)',
        138: 'User-defined 1',
        139: 'Segmentation violation',
        140: 'User-defined 2',
        141: 'Write to pipe with no one reading',
        142: 'Signal raised by alarm',
        143: 'Termination (request to terminate)',
        # 144 - not defined
        145: 'Child process terminated, stopped (or continued*)',
        146: 'Continue if stopped',
        147: 'Stop executing temporarily',
        148: 'Terminal stop signal',
        149: 'Background process attempting to read from tty ("in")',
        150: 'Background process attempting to write to tty ("out")',
        151: 'Urgent data available on socket',
        152: 'CPU time limit exceeded',
        153: 'File size limit exceeded',
        154: 'Signal raised by timer counting virtual time: "virtual timer expired"',
        155: 'Profiling timer expired',
        # 156 - not defined
        157: 'Pollable event',
        # 158 - not defined
        159: 'Bad syscall',
    };

    def __init__(self, commandLine, cwd=None):
        """Constructor.

        @param commandLine: str|list The command line to run
        @param cwd: str|None The working directory or None to use the working
                             directory of the current Python process
        """
        self.__exitCode = None;

        self.setCommandLine(commandLine);
        self.setWorkingDirectory(cwd);
        self.setInput(None);

    def run(self, inheritOutput=False):
        """Runs the process.

        The STDOUT and STDERR are also available after the process is finished
        via the getOutput() and getErrorOutput() methods.

        @param inheritOutput: bool Whether to inherit the STDOUT and STDERR or not

        @return: int The exit status code
        """
        self.__stdout = '';
        self.__stderr = '';

        commandLine = self.getCommandLine();

        if isinstance(commandLine, str) :
            commandLine = shlex.split(commandLine);

        outputHandlers = subprocess.PIPE;
        if inheritOutput :
            outputHandlers = None;

        inputHandler = subprocess.PIPE;
        inputString = None;
        stdin = self.getInput();
        if self.__isFileLike(stdin) :
            inputHandler = stdin;
        else:
            inputString = stdin;

        try:
            process = subprocess.Popen(
                commandLine,
                stdin=inputHandler,
                stdout=outputHandlers,
                stderr=outputHandlers,
                cwd=self.getWorkingDirectory(),
            );

            stdout, stderr = process.communicate(inputString);
            self.__exitCode = process.returncode;
            self.__stdout = stdout;
            self.__stderr = stderr;
        except OSError as e:
            self.__exitCode = e.errno;

        return self.__exitCode;

    def mustRun(self, inheritOutput=False):
        """Runs and terminate successfully the process.

        This is identical to run() except that an exception is raised if the process
        exits with a non-zero exit code.

        @param inheritOutput: bool Whether to inherit the STDOUT and STDERR or not

        @raise ProcessFailedException: if the process didn't terminate successfully
        """
        self.run(inheritOutput);

        if 0 != self.getExitCode() :
            raise ProcessFailedException(self);

    def setInput(self, stdin):
        """Sets the input.

        This content will be passed to the underlying process standard input.

        @param stdin: str|file-like The content
        """
        if None is not stdin and not self.__isFileLike(stdin) :
            if not isinstance(stdin, (str, float, int, bool)) :
                raise TypeError('Process.setInput only accepts strings or file-like objects.');

            stdin = str(stdin);

        self.__stdin = stdin;

    def getInput(self):
        """Gets the Process input.

        @return: str|file-like|None The Process input
        """
        return self.__stdin;

    def getOutput(self):
        """Returns the current output of the process (STDOUT).

        @return: str The process output

        @raise LogicException: In case the process is not started
        """
        if None is self.getExitCode() :
            raise LogicException('Process must be started before calling getOutput');

        return self.__stdout;

    def getErrorOutput(self):
        """Returns the current error output of the process (STDERR).

        @return: str The process error output

        @raise LogicException: In case the process is not started
        """
        if None is self.getExitCode() :
            raise LogicException('Process must be started before calling getErrorOutput');

        return self.__stderr;

    def getExitCode(self):
        """Returns the exit code returned by the process.

        @return: int|None The exit status code, None if the Process is not terminated
        """
        return self.__exitCode;

    def getExitCodeText(self):
        """Returns a string representation for the exit code returned by the process.

        This method relies on the Unix exit code status standardization
        and might not be relevant for other operating systems.

        @return: None|str A string representation for the exit status code, None if the Process is not terminated.

        @see: http://tldp.org/LDP/abs/html/exitcodes.html
        @see: http://en.wikipedia.org/wiki/Unix_signal
        """
        exitCode = self.getExitCode();

        if None is exitCode :
            return;

        try:
            return self.exitCodes[exitCode];
        except KeyError:
            pass;

        return 'Unknown error';

    def setCommandLine(self, commandLine):
        """Sets the command line to be executed.

        @param commandLine: list|str The command to execute
        """
        self.__commandLine = commandLine;

    def getCommandLine(self):
        """Gets the command line to be executed.

        @return: str|list The command to execute
        """
        return self.__commandLine[:];

    def setWorkingDirectory(self, workingDirectory):
        """Sets the current working directory.

        @param workingDirectory: str|None The new working directory or None to use
                                          the working directory of the current
                                          Python process
        """
        self.__workingDirectory = workingDirectory;

    def getWorkingDirectory(self):
        """Gets the working directory.

        @return: str|None The working directory or None to use the working
                          directory of the current Python process
        """
        if None is self.__workingDirectory :
            return;

        return self.__workingDirectory[:];

    def __isFileLike(self, value):
        try:
            value.fileno();
        except:
            return False;
        else:
            return True;
