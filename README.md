# myFRpy — A Python 3.12–based Interpreter
========================================

myFRpy is a Python 3.12 based interpreter (customized fork)
with bilingual en|fr keywords

The original CPython README is preserved for reference in
[README.old.rst](README.old.rst).

# General Information
-------------------

- Project homepage: <https://github.com/alexandre14k/myFRpy>
- Source code: <https://github.com/alexandre14k/myFRpy>

# Using myFRpy
------------

This repository contains the full source code for building
the interpreter from scratch on Linux.

# Build Instructions
--------------------------
**Target** is Linux Mint 22.2 x86_64

Use the `make.sh` bash script to manage the build steps:
``` bash
    ./make.sh

    project <myFRpy>

    t -- rename  | renommer
    d -- tree    | arborescence
    p -- regen   | configurer
    b -- build   | construire
    i -- install | installer
    s -- release | livraison
    r -- run     | exécuter
    c -- clean   | nettoyer
    e -- erase   | effacer
    x -- exit    | quitter
```

# Steps
1. on a new setup press `c` to clean the environment and reconfigure
2. press `p` to regen grammar (if `myFRpy.gram` changed)
3. press `b` to make (creates the ``myFRpy`` binary)
4. ``myFRpy`` is dynamically built in `output/` folder
5. press `i` allows to local install (see `output/bin/myFRpy3.12`)
6. press `r` to run it

# Optional <release>
7. press `s` allows to enter the release menu
``` bash
    ./_release/make.sh

    release

    b : build      -- construire
    r : run        -- executer
    c : clean      -- nettoyer
    e : setup venv -- construire venv
    o : open venv  -- ouvrir venv
    x : exit       -- sortir
```

## Notes
- `venv` mode is not yet supported
- `pip` mode is not yet supported

# Dependencies
------------

Building myFRpy requires standard development tools and libraries :

- a C compiler (GCC or Clang)
- development headers for zlib, libffi, OpenSSL, SQLite, and others

Refer to your distribution’s package manager for installation.

# Test Release
------------

All released packages will be in AppImage format.
The AppImage is fully portable and works on the host system as well as inside Docker containers.

# License
-------

myFRpy is distributed under a modified version of the Python Software
Foundation License. The original CPython license is preserved in
[LICENSE.old](LICENSE.old) for reference.

See [LICENSE](LICENSE) for the license governing this fork.
