myFRpy — A MyFRpy 3.12–based Interpreter
========================================

myFRpy is a customized fork of the MyFRpy 3.12 interpreter, adapted for
Linux-only environments and simplified for experimentation, research, or
lightweight embedding.

The original CMyFRpy README is preserved for reference in
``README.old.rst``.

General Information
-------------------

- Project homepage: <https://github.com/alexandre14k/myFRpy>
- Source code: <https://github.com/alexandre14k/myFRpy>

Using myFRpy
------------

Prebuilt packages or installation instructions may be provided separately.
This repository contains the full source code for building the interpreter
from scratch on Linux.

Build Instructions (Linux)
--------------------------

To build myFRpy from source on Linux or other Unix-like systems::

    ./make.sh

This installs the interpreter as ``myFRpy``.

You can view available configuration options with::

    ./configure --help

Dependencies
------------

Building myFRpy requires standard development tools and libraries such as:

- a C compiler (GCC or Clang)
- development headers for zlib, libffi, OpenSSL, SQLite, and others

Refer to your distribution’s package manager for installation.

Optimized Builds
----------------

To enable Profile Guided Optimization (PGO) and Link Time Optimization (LTO)::

    ./configure --enable-optimizations
    make

Testing
-------

Run the full test suite with::

    make test

Verbose testing example::

    make test TESTOPTS="-v test_os test_gdb"

If you encounter issues that appear to be bugs in myFRpy, please open an
issue with the failing test output.

License
-------

myFRpy is distributed under a modified version of the MyFRpy Software
Foundation License. The original CMyFRpy license is preserved in
``LICENSE.old`` for reference.

See ``LICENSE`` for the license governing this fork.
