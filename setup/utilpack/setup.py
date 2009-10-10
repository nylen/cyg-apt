

import textwrap
import distutils.core

distutils.core.setup(
    name='utilpack',
    version='0.1.0',
    author='Chris Cormie',
    author_email='chris@aussiemail.com.au',
    url='http://wanda/',
    description='A set of useful utility classes and functions.',
    long_description = textwrap.dedent("""\
        A set of useful utility classes and functions\
        """),
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    py_modules=['utilpack'],
)
