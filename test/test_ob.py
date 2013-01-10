#!/usr/bin/python
"""
    unit test for cygapt.ob
"""

from __future__ import print_function
import unittest
import sys

from cygapt.ob import CygAptOb

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
        txt = "makeOn"
        t = self.obj._buffer.getvalue()
        print(txt)
        self.assertEqual(sys.stdout.getvalue(), t + txt + "\n")
        self.assertTrue(self.obj._state)
    
    def makeOff(self):
        def call():
            sys.stdout.getvalue
        self.assertRaises(AttributeError, call)
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
        txt = "test_get_clean"
        print(txt)
        ret = self.obj.get_clean()
        self.assertEqual(ret, t + txt + "\n")
        self.makeOff()
        
    def test_get_content(self):
        ret = self.obj.get_contents()
        self.assertFalse(ret)
        self.makeOff()
        self.obj.start()
        txt = "test_get_content"
        print(txt)
        ret = self.obj.get_contents()
        self.assertEqual(ret, txt + "\n")
        self.makeOn()
        
    def test_get_flush(self):
        ret = self.obj.get_flush()
        self.assertFalse(ret)
        self.makeOff()
        self.obj.start()
        txt = "test_get_flush"
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