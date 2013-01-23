Coding Conventions for cyg-apt
==============================

Extends and overwrite [PEP 8][] and [PEP 257][]

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119][].

[RFC 2119]: http://www.ietf.org/rfc/rfc2119.txt
[PEP 8]: http://www.python.org/dev/peps/pep-0008/
[PEP 257]: http://www.python.org/dev/peps/pep-0257/


General
-------

* Use classes as much as possible.
* A file SHOULD contain only one class (module == class).
* Each statement MUST end with a semicolon `;`.


Idioms
------

* Use only format() method to formatting strings.
* `print` is a function.


Files
-----

* Code MUST use 4 spaces for indenting, not tabs.
* All Python files MUST use the Unix LF (line feed) line ending.
* All Python files MUST end with a single blank line.


Classes
-------

* Class names MUST be declared in `StudlyCaps`.
* Method names MUST be declared in `camelCase`.
* Property/Method names MUST start but not ending with
  TWO underscores `__` to indicate private visibility.
* Property/Method names MUST start but not ending with
  ONE underscores `_` to indicate protected visibility.
* `exception` module SHOULD contain all `Exception` class.
* You can put an `Exception` definition at the end of a file
  if the file is the only one that uses that exception.
* Every `Exception` class MUST end with `Exception`.


Example
-------
```Python
import sys;

from package.class_name import ClassName;

class ClassName():
    def __init__(self, arg1, arg2):
        """Python magic method"""
        self.propertyName = "{1}".format("Public property");
        self._propertyName = arg1; # Protected property
        self.__propertyName = arg2; # Private property

        print(self.propertyName, end="", file=sys.stderr);

    def methodName(self):
        """Public method"""
        pass;

    def _methodName(self):
        """protected method"""
        pass;

    def __methodName(self):
        """private method"""
        pass;

class ClassNameException(Exception):
    """A ClassName Exception"""
    pass;

```


String
------

* Double quotes for text
* Single quotes for anything that behaves like an identifier
* Double quoted raw string literals for regexps
* Tripled double quotes for docstrings
