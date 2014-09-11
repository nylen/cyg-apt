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

from unittest import TestCase as BaseTestCase;
from unittest import _TextTestResult;
from unittest import TestResult;

from .exception import SkipTestException;

__unittest = True;

class TestCase(BaseTestCase):
    """Backports some useful feature from newer unittest version.
    """

    def run(self, result=None):
        """Runs the test.

        @param result: TestResult
        """
        assert None is result or isinstance(result, TestResult);

        if None is result :
            result = self.defaultTestResult();

        if not isinstance(result, _TestResultWrapper) :
            result = _TestResultWrapper(result);

        return BaseTestCase.run(self, result);

    def skipTest(self, reason):
        """Skip this test.

        @param reason: str Explain why this test is skip

        @raise SkipTest: Always
        """
        assert isinstance(reason, str);

        raise SkipTestException(reason);

class _AbstractTestResultWrapper(TestResult):
    """Backports some useful feature from newer unittest version.
    """

    def __init__(self, result):
        """Constructor.

        @param result: TestResult The wrapped object
        """
        assert isinstance(result, TestResult);

        TestResult.__init__(self);

        self._result = result;

    def startTest(self, test):
        """Called when the given test is about to be run.

        @param test: TestCase The case where the skip come from
        """
        assert isinstance(test, BaseTestCase);

        return self._result.startTest(test);

    def stopTest(self, test):
        """Called when the given test has been run.

        @param test: TestCase The case where the skip come from
        """
        assert isinstance(test, BaseTestCase);

        return self._result.stopTest(test);

    def addError(self, test, err):
        """Called when an error has occurred.

        @param test: TestCase The case where the error come from
        @param err:  tuple    Returned by sys.exc_info()
        """
        assert isinstance(test, BaseTestCase);
        assert isinstance(err, tuple);

        return self._result.addError(test, err);

    def addFailure(self, test, err):
        """Called when a test failed.

        @param test: TestCase The case where the failure come from
        @param err:  tuple    Returned by sys.exc_info()
        """
        assert isinstance(test, BaseTestCase);
        assert isinstance(err, tuple);

        return self._result.addFailure(test, err);

    def addSuccess(self, test):
        """Called when a test has completed successfully.

        @param test: TestCase The case where the success come from
        """
        assert isinstance(test, BaseTestCase);

        return self._result.addSuccess(test);

    def wasSuccessful(self):
        """Tells whether or not this result was a success.

        @return: bool
        """
        return self._result.wasSuccessful();

    def stop(self):
        """Indicates that the tests should be aborted.
        """
        return self._result.stop();

class _TestResultWrapper(_AbstractTestResultWrapper):
    """Backports some useful feature from newer unittest version.
    """

    def addError(self, test, err):
        """Called when an error has occurred.

        @param test: TestCase The case where the error come from
        @param err:  tuple    Returned by sys.exc_info()
        """
        assert isinstance(test, BaseTestCase);
        assert isinstance(err, tuple);

        exception = err[1];
        if isinstance(exception, SkipTestException) :
            return self._addSkip(test, str(exception));

        return _AbstractTestResultWrapper.addError(self, test, err);

    def _addSkip(self, test, reason):
        """Called when a test is skipped.

        @param test:   TestCase The case where the skip come from
        @param reason: str      Explain why a test has been skip
        """
        assert isinstance(test, BaseTestCase);
        assert isinstance(reason, str);

        if not isinstance(self._result, _TextTestResult) :
            return;

        if self._result.showAll :
            self._result.stream.writeln("skipped {0!r}".format(reason));
        elif self._result.dots :
            self._result.stream.write("s");
            self._result.stream.flush();
