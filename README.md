# myFRpy — A MyFRpy 3.12–based Interpreter
========================================

myFRpy is a customized fork of the MyFRpy 3.12 interpreter, adapted for
Linux-only environments and simplified for experimentation, research, or
lightweight embedding.

The original CMyFRpy README is preserved for reference in
[README.old.rst](README.old.rst).

# General Information
-------------------

- Project homepage: <https://github.com/alexandre14k/myFRpy>
- Source code: <https://github.com/alexandre14k/myFRpy>

# Using myFRpy
------------

Prebuilt packages or installation instructions may be provided separately.
This repository contains the full source code for building the interpreter
from scratch on Linux.

# Build Instructions (Linux)
--------------------------

To build myFRpy from source on Linux or other Unix-like systems::

    ./make.sh

    project <myFRpy>

    d -- tree  | arborescence
    p -- regen | configurer
    b -- build | construire
    r -- run   | exécuter
    c -- clean | nettoyer
    e -- erase | effacer
    x -- exit  | quitter

First on a new setup press `c` to clean the environment and configure it.

Then edit press `p` to regen after grammar `myFRpy.gram` has changed.

Third press `b` to make. This creates the interpreter as ``myFRpy``.

The output ``myFRpy`` is built dynamically (requires external libraries).

Pressing `r` allows to run in from the bash menu.

# Dependencies
------------

Building myFRpy requires standard development tools and libraries such as:

- a C compiler (GCC or Clang)
- development headers for zlib, libffi, OpenSSL, SQLite, and others

Refer to your distribution’s package manager for installation.

# License
-------

myFRpy is distributed under a modified version of the MyFRpy Software
Foundation License. The original CMyFRpy license is preserved in
[LICENSE.old](LICENSE.old) for reference.

See [LICENSE](LICENSE) for the license governing this fork.
