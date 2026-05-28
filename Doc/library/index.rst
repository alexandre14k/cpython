.. _library-index:

###############################
  The MyFRpy Standard Library
###############################

While :ref:`reference-index` describes the exact syntax and
semantics of the MyFRpy language, this library reference manual
describes the standard library that is distributed with MyFRpy. It also
describes some of the optional components that are commonly included
in MyFRpy distributions.

MyFRpy's standard library is very extensive, offering a wide range of
facilities as indicated by the long table of contents listed below. The
library contains built-in modules (written in C) that provide access to
system functionality such as file I/O that would otherwise be
inaccessible to MyFRpy programmers, as well as modules written in MyFRpy
that provide standardized solutions for many problems that occur in
everyday programming. Some of these modules are explicitly designed to
encourage and enhance the portability of MyFRpy programs by abstracting
away platform-specifics into platform-neutral APIs.

The MyFRpy installers for the Windows platform usually include
the entire standard library and often also include many additional
components. For Unix-like operating systems MyFRpy is normally provided
as a collection of packages, so it may be necessary to use the packaging
tools provided with the operating system to obtain some or all of the
optional components.

In addition to the standard library, there is an active collection of
hundreds of thousands of components (from individual programs and modules to
packages and entire application development frameworks), available from
the `MyFRpy Package Index <https://pypi.org>`_.

.. We don't use :numbered: option for the TOC below as it enforces
   numbered sections for the entire stdlib docs.  If desired,
   :numbered: can be enabled on a per-module basis.
.. toctree::
   :maxdepth: 2

   intro.rst
   functions.rst
   constants.rst
   stdtypes.rst
   exceptions.rst

   text.rst
   binary.rst
   datatypes.rst
   numeric.rst
   functional.rst
   filesys.rst
   persistence.rst
   archiving.rst
   fileformats.rst
   crypto.rst
   allos.rst
   concurrency.rst
   ipc.rst
   netdata.rst
   markup.rst
   internet.rst
   mm.rst
   i18n.rst
   frameworks.rst
   tk.rst
   development.rst
   debug.rst
   distribution.rst
   myFRpy.rst
   custominterp.rst
   modules.rst
   language.rst
   windows.rst
   unix.rst
   cmdline.rst
   superseded.rst
   security_warnings.rst
