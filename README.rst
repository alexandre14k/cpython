# myFRpy — A Python 3.12–based Interpreter
========================================

myFRpy is a customized fork of the Python 3.12 interpreter, adapted for
Linux-only environments and simplified for experimentation, research, or
lightweight embedding.

The original CPython README is preserved for reference in
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

# Build Instructions (Linux Mint 22.2)
--------------------------

To build myFRpy from source on Linux or other Unix-like systems:

``` bash
    ./make.sh

    project <myFRpy>

    t -- rename  | renommer
    d -- tree    | arborescence
    p -- regen   | configurer
    b -- build   | construire
    i -- install | installer
    r -- run     | exécuter
    c -- clean   | nettoyer
    e -- erase   | effacer
    x -- exit    | quitter
```

# Todo
1. on a new setup press `c` to clean the environment and reconfigure
2. press `p` to regen after grammar `myFRpy.gram` has changed
3. press `b` to make. This creates the interpreter as ``myFRpy``
4. output ``myFRpy`` is dynamically built
5. pressing `r` allows to run from the bash menu
6. pressing `i` allows to local install (see `output/bin/myFRpy3.12`)

# Dependencies
------------

Building myFRpy requires standard development tools and libraries :

- a C compiler (GCC or Clang)
- development headers for zlib, libffi, OpenSSL, SQLite, and others

Refer to your distribution’s package manager for installation.

# License
-------

myFRpy is distributed under a modified version of the Python Software
Foundation License. The original CPython license is preserved in
[LICENSE.old](LICENSE.old) for reference.

See [LICENSE](LICENSE) for the license governing this fork.
