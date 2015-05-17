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

import sys;
import warnings;
import pprint;
import functools;
import re;

if sys.version_info < (3, ):
    from .py2 import TestCase as BaseTestCase;
else:
    from unittest import TestCase as BaseTestCase;

__unittest = True;

class DataProviderTestCase(BaseTestCase):
    """Provide the PHPUnit dataProvider feature.

    Use it with the `dataProvider` decorator.

    @author: alquerci <alquerci@email.com>
    """
    ATTR_METHOD_NAME = 'dataProviderMethodName';

    def __init__(self, methodName='runTest', data=None, dataId=None):
        BaseTestCase.__init__(self, methodName);

        self.__data = data;
        self.__dataId = dataId;

        # wrapped the test method to allow to be called with data as arguments
        if None is not self.__data:
            self.__testMethod = getattr(self, methodName);

            functools.update_wrapper(
                self.__invokeWithData.__func__,
                self.__testMethod.__func__,
            );
            setattr(self, self._testMethodName, self.__invokeWithData);

    def __str__(self):
        string = BaseTestCase.__str__(self);

        data = self.__data;
        if data:
            # cuts long data representation
            dataRepr = pprint.saferepr(data);
            if 80 < len(dataRepr) :
                dataRepr = '{0}...{1}'.format(dataRepr[:70], dataRepr[-7:]);

            string += ' with data set #{0:d} {1}'.format(
                self.__dataId,
                dataRepr,
            );

        return string;

    def run(self, result=None):
        testMethod = getattr(self, self._testMethodName);

        # gets the data provider method name
        try:
            providerName = getattr(testMethod, self.ATTR_METHOD_NAME);
        except AttributeError:
            return BaseTestCase.run(self, result);

        # call the data provider method for gets all datasets
        datas = getattr(self, providerName)();

        # runs the test with all datasets
        for dataId in range(len(datas)):
            # use the same behavior than the `TestSuite.run` method
            if result and result.shouldStop:
                break;

            # create a clone of the current instance with this data set
            that = type(self)(self._testMethodName, datas[dataId], dataId);

            BaseTestCase.run(that, result);

    def __invokeWithData(self):
        return self.__testMethod(*self.__data);


class TestCase(DataProviderTestCase):
    """Base class for all cygapt test case.
    """
    def _assertDeprecatedWarning(self, message, callback, *args, **kwargs):
        """Asserts that a warning of type "DeprecationWarning" is triggered with message.

        When invoked the callback with arguments args and keyword arguments
        kwargs.

        @param message:  str      The expected warning message
        @param callback: callable The callback to call
        @param *args:    mixed
        @param **kwargs: mixed
        """
        assert isinstance(message, str);
        assert hasattr(callback, '__call__');

        with warnings.catch_warnings(record=True) as warnList :
            # cause all DeprecationWarning to always be triggered
            warnings.simplefilter("always", DeprecationWarning);

            # trigger a warning
            ret = callback(*args, **kwargs);

            # verify some things
            if not warnList :
                self.fail(" ".join([
                    "Failed asserting that a warning of type",
                    '"DeprecationWarning" is triggered',
                ]));

            messages = list();
            for warn in warnList :
                messages.append(str(warn.message));
                if message in messages[-1] :
                    return ret;

            self.fail("\n".join([
                "Failed asserting that at least one of these warning messages:",
                "{0}",
                "contains",
                "{1}",
            ]).format("\n".join(messages), message));

        return ret;

    def _assertNotDeprecatedWarning(self, message, callback, *args, **kwargs):
        """Asserts that a warning of type "DeprecationWarning" is not triggered with message.

        When invoked the callback with arguments args and keyword arguments
        kwargs.

        @param message:  str      The expected warning message
        @param callback: callable The callback to call
        @param *args:    mixed
        @param **kwargs: mixed
        """
        try:
            self._assertDeprecatedWarning(message, callback, *args, **kwargs);
        except self.failureException :
            return;

        self.fail(" ".join([
            "Failed asserting that a warning of type",
            '"DeprecationWarning" with message "{0}" is not triggered',
        ]).format(message));


def dataProvider(methodName):
    """Method decorator like the PHPUnit one.

    The method must return a sequence of sequences that they will be pass
    as arguments of the decorated method.

    It does not support keyword argument.

    @param methodName: str The method name of the current class to call for get
                           all datas
    """
    def decorator(function):
        setattr(function, DataProviderTestCase.ATTR_METHOD_NAME, methodName);

        return function;

    return decorator;


def expectedException(expectedClass, expectedMessage=None, treatMessageAsRegexp=False):
    """TestCase method decorator.

    @param expectedClass: type The expected exception class
    @param expectedMessage: str The expected message that the raises exception contain
    @param treatMessageAsRegexp: bool Treat the expected message as a regex pattern
    """
    if None is not expectedMessage and not treatMessageAsRegexp:
        expectedMessage = re.escape(expectedMessage);

    def decorator(function):
        @functools.wraps(function)
        def wrapper(self, *args, **kwargs):
            with self.assertRaisesRegexp(expectedClass, expectedMessage):
                return function(self, *args, **kwargs);

        return wrapper;

    return decorator;
