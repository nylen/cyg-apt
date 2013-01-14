#!/usr/bin/python
######################## BEGIN LICENSE BLOCK ########################
# This file is part of the cygapt package.
#
# Copyright (C) 2002-2009 Jan Nieuwenhuizen  <janneke@gnu.org>
#               2002-2009 Chris Cormie       <cjcormie@gmail.com>
#                    2012 James Nylen        <jnylen@gmail.com>
#               2012-2013 Alexandre Quercia  <alquerci@email.com>
#
# For the full copyright and license information, please view the
# LICENSE file that was distributed with this source code.
######################### END LICENSE BLOCK #########################
"""
    unit test for cygapt.ob
"""

from __future__ import print_function
import unittest
import sys

from cygapt.ob import CygAptOb

REPR_STDOUT = repr(sys.stdout);

class TestOb(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.obj = CygAptOb(False)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        try:
            self.obj.end()
        except:
            pass
    
    def makeOn(self):
        txt = "TestOb.makeOn "
        print(txt, end="");
        value = sys.stdout.getvalue();
        self.assertTrue(value.endswith(txt));
        self.assertTrue(self.obj._state)
    
    def makeOff(self):
        self.assertEqual(repr(sys.stdout), REPR_STDOUT);
        self.assertFalse(self.obj._state)
    
    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygAptOb))
    
    def test_clean(self):
        self.obj.clean()
        self.makeOff()
        self.obj.start()
        self.makeOn()
        self.obj.clean()
        self.assertEqual(self.obj._buffer.getvalue(), "")
        self.assertFalse(self.obj._value == "")
        self.assertFalse(self.obj.get_contents() == "")
    
    def test_start_end(self):
        self.obj.end()
        self.makeOff()
        self.obj.start()
        self.makeOn()
        self.obj.end()
        self.makeOff()
        
    def test_end_clean(self):
        self.obj.end_clean()
        self.makeOff()
        self.obj.start()
        self.makeOn()
        self.obj.end_clean()
        self.makeOff()
    
    def test_end_flush(self):
        self.obj.end_flush()
        self.makeOff()
        self.obj.start()
        self.makeOn()
        self.obj.end_flush()
        self.makeOff()
    
    def test_flush(self):
        self.obj.flush()
        self.makeOff()
        self.obj.start()
        self.makeOn()
        self.obj.flush()
        self.makeOn()
    
    def test_get_clean(self):
        ret = self.obj.get_clean()
        self.assertFalse(ret)
        self.makeOff()
        self.obj.start()
        self.makeOn()
        t = self.obj._buffer.getvalue()
        txt = "TestOb.test_get_clean"
        print(txt)
        ret = self.obj.get_clean()
        self.assertEqual(ret, t + txt + "\n")
        self.makeOff()
        
    def test_get_content(self):
        ret = self.obj.get_contents()
        self.assertFalse(ret)
        self.makeOff()
        self.obj.start()
        txt = "TestOb.test_get_content"
        print(txt)
        ret = self.obj.get_contents()
        self.assertEqual(ret, txt + "\n")
        self.makeOn()
        
    def test_get_flush(self):
        ret = self.obj.get_flush()
        self.assertFalse(ret)
        self.makeOff()
        self.obj.start()
        txt = "TestOb.test_get_flush"
        print(txt)
        ret = self.obj.get_flush()
        self.assertEqual(ret, txt + "\n")
        self.makeOff()
    
    def test_get_length(self):
        ret = self.obj.get_length()
        self.assertFalse(ret)
        self.makeOff()
        self.obj.start()
        length = 10
        print("t" * length)
        ret = self.obj.get_length()
        self.assertEqual(ret, length + 1)
        self.makeOn()
        
    def test_implicit_flush(self):
        self.obj.implicit_flush(True)
        self.makeOff()
        self.obj.implicit_flush(False)
        self.makeOn()


if __name__ == '__main__':
    unittest.main()