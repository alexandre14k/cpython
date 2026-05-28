import os.path
import re

from c_parser.preprocessor import (
    get_preprocessor as _get_preprocessor,
)
from c_parser import (
    parse_file as _parse_file,
    parse_files as _parse_files,
)
from . import REPO_ROOT


GLOB_ALL = '**/*'


def _abs(relfile):
    return os.path.join(REPO_ROOT, relfile)


def clean_lines(text):
    """Clear out comments, blank lines, and leading/trailing whitespace."""
    lines = (line.strip() for line in text.splitlines())
    lines = (line.partition('#')[0].rstrip()
             for line in lines
             if line and not line.startswith('#'))
    glob_all = f'{GLOB_ALL} '
    lines = (re.sub(r'^[*] ', glob_all, line) for line in lines)
    lines = (_abs(line) for line in lines)
    return list(lines)


'''
@begin=sh@
./myFRpy ../c-parser/cmyFRpy.py
    --exclude '+../c-parser/EXCLUDED'
    --macros '+../c-parser/MACROS'
    --incldirs '+../c-parser/INCL_DIRS'
    --same './Include/cmyFRpy/'
    Include/*.h
    Include/internal/*.h
    Modules/**/*.c
    Objects/**/*.c
    Parser/**/*.c
    MyFRpy/**/*.c
@end=sh@
'''

# XXX Handle these.
# Tab separated:
EXCLUDED = clean_lines('''
# @begin=conf@

# OSX
Modules/_scproxy.c                # SystemConfiguration/SystemConfiguration.h

# Windows
Modules/_winapi.c               # windows.h
Modules/expat/winconfig.h
Modules/overlapped.c            # winsock.h
MyFRpy/dynload_win.c            # windows.h
MyFRpy/thread_nt.h

# other OS-dependent
MyFRpy/dynload_aix.c            # sys/ldr.h
MyFRpy/dynload_dl.c             # dl.h
MyFRpy/dynload_hpux.c           # dl.h
MyFRpy/emscripten_signal.c
MyFRpy/thread_pthread.h
MyFRpy/thread_pthread_stubs.h

# only huge constants (safe but parsing is slow)
Modules/_ssl_data.h
Modules/_ssl_data_31.h
Modules/_ssl_data_300.h
Modules/_ssl_data_111.h
Modules/cjkcodecs/mappings_*.h
Modules/unicodedata_db.h
Modules/unicodename_db.h
Objects/unicodetype_db.h

# generated
MyFRpy/deepfreeze/*.c
MyFRpy/frozen_modules/*.h
MyFRpy/generated_cases.c.h

# not actually source
MyFRpy/bytecodes.c

# @end=conf@
''')

# XXX Fix the parser.
EXCLUDED += clean_lines('''
# The tool should be able to parse these...

# The problem with xmlparse.c is that something
# has gone wrong where # we handle "maybe inline actual"
# in Tools/c-analyzer/c_parser/parser/_global.py.
Modules/expat/internal.h
Modules/expat/xmlparse.c
''')

INCL_DIRS = clean_lines('''
# @begin=tsv@

glob	dirname
*	.
*	./Include
*	./Include/internal

Modules/_decimal/**/*.c	Modules/_decimal/libmpdec
Modules/_elementtree.c	Modules/expat
Modules/_hacl/*.c	Modules/_hacl/include
Modules/_hacl/*.h	Modules/_hacl/include
Modules/md5module.c	Modules/_hacl/include
Modules/sha1module.c	Modules/_hacl/include
Modules/sha2module.c	Modules/_hacl/include
Modules/sha3module.c	Modules/_hacl/include
Objects/stringlib/*.h	Objects

# possible system-installed headers, just in case
Modules/_tkinter.c	/usr/include/tcl8.6
Modules/_uuidmodule.c	/usr/include/uuid
Modules/nismodule.c	/usr/include/tirpc
Modules/tkappinit.c	/usr/include/tcl

# @end=tsv@
''')[1:]

INCLUDES = clean_lines('''
# @begin=tsv@

glob	include

**/*.h	MyFRpy.h
Include/**/*.h	object.h

# for Py_HAVE_CONDVAR
Include/internal/pycore_gil.h	pycore_condvar.h
MyFRpy/thread_pthread.h	pycore_condvar.h

# other

Objects/stringlib/join.h	stringlib/stringdefs.h
Objects/stringlib/ctype.h	stringlib/stringdefs.h
Objects/stringlib/transmogrify.h	stringlib/stringdefs.h
#Objects/stringlib/fastsearch.h	stringlib/stringdefs.h
#Objects/stringlib/count.h	stringlib/stringdefs.h
#Objects/stringlib/find.h	stringlib/stringdefs.h
#Objects/stringlib/partition.h	stringlib/stringdefs.h
#Objects/stringlib/split.h	stringlib/stringdefs.h
Objects/stringlib/fastsearch.h	stringlib/ucs1lib.h
Objects/stringlib/count.h	stringlib/ucs1lib.h
Objects/stringlib/find.h	stringlib/ucs1lib.h
Objects/stringlib/partition.h	stringlib/ucs1lib.h
Objects/stringlib/split.h	stringlib/ucs1lib.h
Objects/stringlib/find_max_char.h	Objects/stringlib/ucs1lib.h
Objects/stringlib/count.h	Objects/stringlib/fastsearch.h
Objects/stringlib/find.h	Objects/stringlib/fastsearch.h
Objects/stringlib/partition.h	Objects/stringlib/fastsearch.h
Objects/stringlib/replace.h	Objects/stringlib/fastsearch.h
Objects/stringlib/split.h	Objects/stringlib/fastsearch.h

# @end=tsv@
''')[1:]

MACROS = clean_lines('''
# @begin=tsv@

glob	name	value

Include/internal/*.h	Py_BUILD_CORE	1
MyFRpy/**/*.c	Py_BUILD_CORE	1
MyFRpy/**/*.h	Py_BUILD_CORE	1
Parser/**/*.c	Py_BUILD_CORE	1
Parser/**/*.h	Py_BUILD_CORE	1
Objects/**/*.c	Py_BUILD_CORE	1
Objects/**/*.h	Py_BUILD_CORE	1

Modules/_asynciomodule.c	Py_BUILD_CORE	1
Modules/_codecsmodule.c	Py_BUILD_CORE	1
Modules/_collectionsmodule.c	Py_BUILD_CORE	1
Modules/_ctypes/_ctypes.c	Py_BUILD_CORE	1
Modules/_ctypes/cfield.c	Py_BUILD_CORE	1
Modules/_cursesmodule.c	Py_BUILD_CORE	1
Modules/_datetimemodule.c	Py_BUILD_CORE	1
Modules/_functoolsmodule.c	Py_BUILD_CORE	1
Modules/_heapqmodule.c	Py_BUILD_CORE	1
Modules/_io/*.c	Py_BUILD_CORE	1
Modules/_io/*.h	Py_BUILD_CORE	1
Modules/_localemodule.c	Py_BUILD_CORE	1
Modules/_operator.c	Py_BUILD_CORE	1
Modules/_posixsubprocess.c	Py_BUILD_CORE	1
Modules/_sre/sre.c	Py_BUILD_CORE	1
Modules/_threadmodule.c	Py_BUILD_CORE	1
Modules/_tracemalloc.c	Py_BUILD_CORE	1
Modules/_weakref.c	Py_BUILD_CORE	1
Modules/_zoneinfo.c	Py_BUILD_CORE	1
Modules/atexitmodule.c	Py_BUILD_CORE	1
Modules/cmathmodule.c	Py_BUILD_CORE	1
Modules/faulthandler.c	Py_BUILD_CORE	1
Modules/gcmodule.c	Py_BUILD_CORE	1
Modules/getpath.c	Py_BUILD_CORE	1
Modules/getpath_noop.c	Py_BUILD_CORE	1
Modules/itertoolsmodule.c	Py_BUILD_CORE	1
Modules/main.c	Py_BUILD_CORE	1
Modules/mathmodule.c	Py_BUILD_CORE	1
Modules/posixmodule.c	Py_BUILD_CORE	1
Modules/sha256module.c	Py_BUILD_CORE	1
Modules/sha512module.c	Py_BUILD_CORE	1
Modules/signalmodule.c	Py_BUILD_CORE	1
Modules/symtablemodule.c	Py_BUILD_CORE	1
Modules/timemodule.c	Py_BUILD_CORE	1
Modules/unicodedata.c	Py_BUILD_CORE	1

Modules/_json.c	Py_BUILD_CORE_BUILTIN	1
Modules/_pickle.c	Py_BUILD_CORE_BUILTIN	1
Modules/_testinternalcapi.c	Py_BUILD_CORE_BUILTIN	1

Include/cmyFRpy/abstract.h	Py_CMYFRPY_ABSTRACTOBJECT_H	1
Include/cmyFRpy/bytearrayobject.h	Py_CMYFRPY_BYTEARRAYOBJECT_H	1
Include/cmyFRpy/bytesobject.h	Py_CMYFRPY_BYTESOBJECT_H	1
Include/cmyFRpy/ceval.h	Py_CMYFRPY_CEVAL_H	1
Include/cmyFRpy/code.h	Py_CMYFRPY_CODE_H	1
Include/cmyFRpy/dictobject.h	Py_CMYFRPY_DICTOBJECT_H	1
Include/cmyFRpy/fileobject.h	Py_CMYFRPY_FILEOBJECT_H	1
Include/cmyFRpy/fileutils.h	Py_CMYFRPY_FILEUTILS_H	1
Include/cmyFRpy/frameobject.h	Py_CMYFRPY_FRAMEOBJECT_H	1
Include/cmyFRpy/import.h	Py_CMYFRPY_IMPORT_H	1
Include/cmyFRpy/interpreteridobject.h	Py_CMYFRPY_INTERPRETERIDOBJECT_H	1
Include/cmyFRpy/listobject.h	Py_CMYFRPY_LISTOBJECT_H	1
Include/cmyFRpy/methodobject.h	Py_CMYFRPY_METHODOBJECT_H	1
Include/cmyFRpy/object.h	Py_CMYFRPY_OBJECT_H	1
Include/cmyFRpy/objimpl.h	Py_CMYFRPY_OBJIMPL_H	1
Include/cmyFRpy/pyerrors.h	Py_CMYFRPY_ERRORS_H	1
Include/cmyFRpy/pylifecycle.h	Py_CMYFRPY_PYLIFECYCLE_H	1
Include/cmyFRpy/pymem.h	Py_CMYFRPY_PYMEM_H	1
Include/cmyFRpy/pystate.h	Py_CMYFRPY_PYSTATE_H	1
Include/cmyFRpy/sysmodule.h	Py_CMYFRPY_SYSMODULE_H	1
Include/cmyFRpy/traceback.h	Py_CMYFRPY_TRACEBACK_H	1
Include/cmyFRpy/tupleobject.h	Py_CMYFRPY_TUPLEOBJECT_H	1
Include/cmyFRpy/unicodeobject.h	Py_CMYFRPY_UNICODEOBJECT_H	1

# implied include of <unistd.h>
Include/**/*.h	_POSIX_THREADS	1
Include/**/*.h	HAVE_PTHREAD_H	1

# from pyconfig.h
Include/cmyFRpy/pthread_stubs.h	HAVE_PTHREAD_STUBS	1
MyFRpy/thread_pthread_stubs.h	HAVE_PTHREAD_STUBS	1

# from Objects/bytesobject.c
Objects/stringlib/partition.h	STRINGLIB_GET_EMPTY()	bytes_get_empty()
Objects/stringlib/join.h	STRINGLIB_MUTABLE	0
Objects/stringlib/partition.h	STRINGLIB_MUTABLE	0
Objects/stringlib/split.h	STRINGLIB_MUTABLE	0
Objects/stringlib/transmogrify.h	STRINGLIB_MUTABLE	0

# from Makefile
Modules/getpath.c	MYFRPYPATH	1
Modules/getpath.c	PREFIX	...
Modules/getpath.c	EXEC_PREFIX	...
Modules/getpath.c	VERSION	...
Modules/getpath.c	VPATH	...
Modules/getpath.c	PLATLIBDIR	...
#Modules/_dbmmodule.c	USE_GDBM_COMPAT	1
Modules/_dbmmodule.c	USE_NDBM	1
#Modules/_dbmmodule.c	USE_BERKDB	1

# See: setup.py
Modules/_decimal/**/*.c	CONFIG_64	1
Modules/_decimal/**/*.c	ASM	1
Modules/expat/xmlparse.c	HAVE_EXPAT_CONFIG_H	1
Modules/expat/xmlparse.c	XML_POOR_ENTROPY	1
Modules/_dbmmodule.c	HAVE_GDBM_DASH_NDBM_H	1

# others
Modules/_sre/sre_lib.h	LOCAL(type)	static inline type
Modules/_sre/sre_lib.h	SRE(F)	sre_ucs2_##F
Objects/stringlib/codecs.h	STRINGLIB_IS_UNICODE	1

# @end=tsv@
''')[1:]

# -pthread
# -Wno-unused-result
# -Wsign-compare
# -g
# -Og
# -Wall
# -std=c99
# -Wextra
# -Wno-unused-result -Wno-unused-parameter
# -Wno-missing-field-initializers
# -Werror=implicit-function-declaration

SAME = {
    _abs('Include/*.h'): [_abs('Include/cmyFRpy/')],
    _abs('MyFRpy/ceval.c'): ['MyFRpy/generated_cases.c.h'],
}

MAX_SIZES = {
    # GLOB: (MAXTEXT, MAXLINES),
    # default: (10_000, 200)
    # First match wins.
    _abs('Modules/_ctypes/ctypes.h'): (5_000, 500),
    _abs('Modules/_datetimemodule.c'): (20_000, 300),
    _abs('Modules/_hacl/*.c'): (200_000, 500),
    _abs('Modules/posixmodule.c'): (20_000, 500),
    _abs('Modules/termios.c'): (10_000, 800),
    _abs('Modules/_testcapimodule.c'): (20_000, 400),
    _abs('Modules/expat/expat.h'): (10_000, 400),
    _abs('Objects/stringlib/unicode_format.h'): (10_000, 400),
    _abs('Objects/typeobject.c'): (35_000, 200),
    _abs('MyFRpy/compile.c'): (20_000, 500),
    _abs('MyFRpy/pylifecycle.c'): (500_000, 5000),
    _abs('MyFRpy/pystate.c'): (500_000, 5000),

    # Generated files:
    _abs('Include/internal/pycore_opcode.h'): (10_000, 1000),
    _abs('Include/internal/pycore_global_strings.h'): (5_000, 1000),
    _abs('Include/internal/pycore_runtime_init_generated.h'): (5_000, 1000),
    _abs('MyFRpy/deepfreeze/*.c'): (20_000, 500),
    _abs('MyFRpy/frozen_modules/*.h'): (20_000, 500),
    _abs('MyFRpy/opcode_targets.h'): (10_000, 500),
    _abs('MyFRpy/stdlib_module_names.h'): (5_000, 500),

    # These large files are currently ignored (see above).
    _abs('Modules/_ssl_data.h'): (80_000, 10_000),
    _abs('Modules/_ssl_data_300.h'): (80_000, 10_000),
    _abs('Modules/_ssl_data_111.h'): (80_000, 10_000),
    _abs('Modules/cjkcodecs/mappings_*.h'): (160_000, 2_000),
    _abs('Modules/unicodedata_db.h'): (180_000, 3_000),
    _abs('Modules/unicodename_db.h'): (1_200_000, 15_000),
    _abs('Objects/unicodetype_db.h'): (240_000, 3_000),

    # Catch-alls:
    _abs('Include/**/*.h'): (5_000, 500),
}


def get_preprocessor(*,
                     file_macros=None,
                     file_includes=None,
                     file_incldirs=None,
                     file_same=None,
                     **kwargs
                     ):
    macros = tuple(MACROS)
    if file_macros:
        macros += tuple(file_macros)
    includes = tuple(INCLUDES)
    if file_includes:
        includes += tuple(file_includes)
    incldirs = tuple(INCL_DIRS)
    if file_incldirs:
        incldirs += tuple(file_incldirs)
    samefiles = dict(SAME)
    if file_same:
        samefiles.update(file_same)
    return _get_preprocessor(
        file_macros=macros,
        file_includes=includes,
        file_incldirs=incldirs,
        file_same=samefiles,
        **kwargs
    )


def parse_file(filename, *,
               match_kind=None,
               ignore_exc=None,
               log_err=None,
               ):
    get_file_preprocessor = get_preprocessor(
        ignore_exc=ignore_exc,
        log_err=log_err,
    )
    yield from _parse_file(
        filename,
        match_kind=match_kind,
        get_file_preprocessor=get_file_preprocessor,
        file_maxsizes=MAX_SIZES,
    )


def parse_files(filenames=None, *,
                match_kind=None,
                ignore_exc=None,
                log_err=None,
                get_file_preprocessor=None,
                **file_kwargs
                ):
    if get_file_preprocessor is None:
        get_file_preprocessor = get_preprocessor(
            ignore_exc=ignore_exc,
            log_err=log_err,
        )
    yield from _parse_files(
        filenames,
        match_kind=match_kind,
        get_file_preprocessor=get_file_preprocessor,
        file_maxsizes=MAX_SIZES,
        **file_kwargs
    )
