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
import re;

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

    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        """Fail unless an exception of class excClass is raised
           by callableObj when invoked with arguments args and keyword
           arguments kwargs. If a different type of exception is
           raised, it will not be caught, and the test case will be
           deemed to have suffered an error, exactly as for an
           unexpected exception.

           If called with callableObj omitted or None, will return a
           context object used like this::

                with self.assertRaises(SomeException):
                    do_something()

           The context manager keeps a reference to the exception as
           the 'exception' attribute. This allows you to inspect the
           exception after the assertion::

               with self.assertRaises(SomeException) as cm:
                   do_something()
               the_exception = cm.exception
               self.assertEqual(the_exception.error_code, 3)
        """
        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)

    def assertRaisesRegexp(self, expected_exception, expected_regexp,
                           callable_obj=None, *args, **kwargs):
        """Asserts that the message in a raised exception matches a regexp.

        Args:
            expected_exception: Exception class expected to be raised.
            expected_regexp: Regexp (re pattern object or string) expected
                    to be found in error message.
            callable_obj: Function to be called.
            args: Extra args.
            kwargs: Extra kwargs.
        """
        if expected_regexp is not None:
            expected_regexp = re.compile(expected_regexp)
        context = _AssertRaisesContext(expected_exception, self, expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj(*args, **kwargs)


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


class _AssertRaisesContext(object):
    """A context manager used to implement TestCase.assertRaises* methods."""

    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "{0} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        self.exception = exc_value # store for later retrieval
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                     (expected_regexp.pattern, str(exc_value)))
        return True
