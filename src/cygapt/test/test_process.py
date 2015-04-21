#!/usr/bin/env python
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
"""
    Unit test for cygapt.process
"""

from __future__ import absolute_import;

import os;
import unittest;
import subprocess;
from tempfile import TemporaryFile;

from cygapt.test.case import TestCase;
from cygapt.test.case import dataProvider;
from cygapt.test.case import expectedException;
from cygapt.process import Process;
from cygapt.process.exception import ProcessFailedException;
from cygapt.process.exception import LogicException;

class TestProcess(TestCase):
    def setUp(self):
        TestCase.setUp(self);

    def tearDown(self):
        TestCase.tearDown(self);

    def getDefaultGetterSetterData(self):
        return [
            ['CommandLine', ['foo']],
            ['WorkingDirectory', ['foo']],
            ['CommandLine', 'bar'],
            ['WorkingDirectory', 'bar'],
            ['Input', 'bar'],
        ];

    @dataProvider('getDefaultGetterSetterData')
    def testDefaultGetterSetter(self, fn, value):
        proc = Process('python');

        setter = 'set'+fn;
        getter = 'get'+fn;

        self.assertTrue(
            None is getattr(proc, setter)(value),
            "Failed asserting that setter method return None",
        );

        self.assertEqual(getattr(proc, getter)(), value);

        if not isinstance(value, str) :
            self.assertFalse(
                value is getattr(proc, getter)(),
                "Failed asserting that getter method return a cloned value",
            );

    def responsesCodeProvider(self):
        return [
            [1, 'getExitCode', 'exit(1);'],
            [0, 'getExitCode', 'exit();'],
            ['Misuse of shell builtins', 'getExitCodeText', 'exit(2);'],
            ['Unknown error', 'getExitCodeText', 'exit(64);'],
            ['foo', 'getOutput', 'import sys; sys.stdout.write("foo");'],
            ['bar', 'getOutput', 'import sys; sys.stdout.write("bar");'],
            ['0', 'getOutput', 'import sys; sys.stdout.write("0");'],
            ['foo', 'getErrorOutput', 'import sys; sys.stderr.write("foo");'],
            ['bar', 'getErrorOutput', 'import sys; sys.stderr.write("bar");'],
        ];

    @dataProvider('responsesCodeProvider')
    def testProcessResponses(self, expected, getter, code):
        proc = Process("python -c '{0}'".format(code));
        proc.run();

        self.assertEqual(getattr(proc, getter)(), expected);

    @dataProvider('responsesCodeProvider')
    def testRunReturnAlwaysExitCode(self, expected, getter, code):
        proc = Process("python -c '{0}'".format(code));
        actual = proc.run();

        self.assertEqual(actual, proc.getExitCode());

    def testRunReturnAlwaysExitCodeEvenOnCommandFailed(self):
        proc = Process('nonexistingcommandIhopeneversomeonewouldnameacommandlikethis');
        actual = proc.run();

        self.assertTrue(0 < actual, "Failed asserting that {0} is greater than 0".format(actual));

    def getProcessPipesData(self):
        return [
            [1, 'getOutput', 'import sys; sys.stdout.write(sys.stdin.read());'],
            [1, 'getErrorOutput', 'import sys; sys.stderr.write(sys.stdin.read());'],
            [16, 'getOutput', 'import sys; sys.stdout.write(sys.stdin.read());'],
            [16, 'getErrorOutput', 'import sys; sys.stderr.write(sys.stdin.read());'],
            [64, 'getOutput', 'import sys; sys.stdout.write(sys.stdin.read());'],
            [64, 'getErrorOutput', 'import sys; sys.stderr.write(sys.stdin.read());'],
            [1024, 'getOutput', 'import sys; sys.stdout.write(sys.stdin.read());'],
            [1024, 'getErrorOutput', 'import sys; sys.stderr.write(sys.stdin.read());'],
            [4096, 'getOutput', 'import sys; sys.stdout.write(sys.stdin.read());'],
            [4096, 'getErrorOutput', 'import sys; sys.stderr.write(sys.stdin.read());'],
        ];

    @dataProvider('getProcessPipesData')
    def testProcessPipes(self, size, getter, code):
        expected = '*' * 1024 * size + '!';
        expectedLength = 1024 * size + 1;

        proc = Process("python -c '{0}'".format(code));
        proc.setInput(expected);
        proc.run();

        self.assertEqual(len(getattr(proc, getter)()), expectedLength);
        self.assertEqual(proc.getExitCode(), 0);

    @dataProvider('getProcessPipesData')
    def testSetStreamAsInput(self, size, getter, code):
        expected = '*' * 1024 * size + '!';
        expectedLength = 1024 * size + 1;

        stream = TemporaryFile();
        stream.write(expected);
        stream.seek(0);

        proc = Process("python -c '{0}'".format(code));
        proc.setInput(stream);
        proc.run();

        stream.close();

        self.assertEqual(len(getattr(proc, getter)()), expectedLength);
        self.assertEqual(proc.getExitCode(), 0);

    @dataProvider('provideInvalidInputValues')
    @expectedException(
        TypeError,
        'Process.setInput only accepts strings or file-like objects.'
    )
    def testInvalidInput(self, value):
        process = Process('python --version');
        process.setInput(value);

    def provideInvalidInputValues(self):
        return [
            [list()],
            [object()],
        ];

    @dataProvider('provideInputValues')
    def testValidInput(self, expected, value):
        process = Process('python --version');
        process.setInput(value);

        self.assertEqual(process.getInput(), expected);

    def provideInputValues(self):
        return [
            [None, None],
            ['24.5', 24.5],
            ['input data', 'input data'],
        ];

    def testExitCodeCommandFailed(self):
        process = Process('nonexistingcommandIhopeneversomeonewouldnameacommandlikethis');
        process.run();

        actual = process.getExitCode();
        self.assertTrue(0 < actual, "Failed asserting that {0} is greater than 0".format(actual));

    def testExitCodeTextIsNoneWhenExitCodeIsNone(self):
        process = Process('');

        self.assertEqual(process.getExitCodeText(), None);

    def getResponsesCommandFailedData(self):
        return [
            ['', 'getOutput'],
            ['', 'getErrorOutput'],
        ];

    @dataProvider('getResponsesCommandFailedData')
    def testResponsesCommandFailed(self, expected, method):
        process = Process('python -c \'import sys; sys.stdout.write("foo"); sys.stderr.write("bar");\'');
        process.run();
        process.setCommandLine('nonexistingcommandIhopeneversomeonewouldnameacommandlikethis');
        process.run();

        self.assertEqual(getattr(process, method)(), expected);

    def testMustRun(self):
        process = Process('python -c \'import sys; sys.stdout.write("foo");\'');
        process.mustRun();

        self.assertEqual(process.getOutput(), 'foo');
        self.assertEqual(process.getExitCode(), 0);

    @expectedException(ProcessFailedException, """\
The command "python -c 'import sys; sys.stdout.write("foo"); sys.stderr.write("bar"); exit(1);'" failed.
Exit Code: 1 (General error)

Output:
================
foo

Error Output:
================
bar\
""")
    def testMustRunThrowsException(self):
        process = Process('python -c \'import sys; sys.stdout.write("foo"); sys.stderr.write("bar"); exit(1);\'');
        process.mustRun();

    @expectedException(LogicException, 'Process must be started before calling getOutput')
    def testGetOutputProcessNotStarted(self):
        proc = Process('python --version');
        proc.getOutput();

    @expectedException(LogicException, 'Process must be started before calling getErrorOutput')
    def testGetErrorOutputProcessNotStarted(self):
        proc = Process('python --version');
        proc.getErrorOutput();

    def testConstructor(self):
        proc = Process('foo');

        self.assertEqual(proc.getCommandLine(), 'foo');
        self.assertEqual(proc.getWorkingDirectory(), None);
        self.assertEqual(proc.getInput(), None);

    def testConstructorSetTheCwd(self):
        proc = Process('foo', 'bar');

        self.assertEqual(proc.getWorkingDirectory(), 'bar');

    def provideStartMethods(self):
        return [
            ['run'],
            ['mustRun'],
        ];

    @dataProvider('provideStartMethods')
    def testRunWorkingDirectoryIsUsed(self, startMethod):
        popen = subprocess.Popen;
        directory = os.path.dirname(__file__);

        def mock(*args, **kargs):
            self.assertEqual(kargs['cwd'], directory);

            return popen(*args, **kargs);

        subprocess.Popen = mock;

        try:
            proc = Process('python --version');
            proc.setWorkingDirectory(directory);

            getattr(proc, startMethod)();
        finally:
            subprocess.Popen = popen;

    @dataProvider('provideStartMethods')
    def testRunInheritOutput(self, startMethod):
        popen = subprocess.Popen;

        def mock(*args, **kargs):
            self.assertTrue(None is kargs['stdout']);
            self.assertTrue(None is kargs['stderr']);

            return popen(*args, **kargs);

        subprocess.Popen = mock;

        try:
            proc = Process("python -c ''");

            getattr(proc, startMethod)(True);
        finally:
            subprocess.Popen = popen;

if __name__ == "__main__":
    unittest.main();
