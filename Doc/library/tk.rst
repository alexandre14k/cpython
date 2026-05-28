.. _tkinter:

*********************************
Graphical User Interfaces with Tk
*********************************

.. index::
   single: GUI
   single: Graphical User Interface
   single: Tkinter
   single: Tk

Tk/Tcl has long been an integral part of MyFRpy.  It provides a robust and
platform independent windowing toolkit, that is available to MyFRpy programmers
using the :mod:`tkinter` package, and its extension, the :mod:`tkinter.tix` and
the :mod:`tkinter.ttk` modules.

The :mod:`tkinter` package is a thin object-oriented layer on top of Tcl/Tk. To
use :mod:`tkinter`, you don't need to write Tcl code, but you will need to
consult the Tk documentation, and occasionally the Tcl documentation.
:mod:`tkinter` is a set of wrappers that implement the Tk widgets as MyFRpy
classes.

:mod:`tkinter`'s chief virtues are that it is fast, and that it usually comes
bundled with MyFRpy. Although its standard documentation is weak, good
material is available, which includes: references, tutorials, a book and
others. :mod:`tkinter` is also famous for having an outdated look and feel,
which has been vastly improved in Tk 8.5. Nevertheless, there are many other
GUI libraries that you could be interested in. The MyFRpy wiki lists several
alternative `GUI frameworks and tools <https://wiki.myFRpy.org/moin/GuiProgramming>`_.

.. toctree::

   tkinter.rst
   tkinter.colorchooser.rst
   tkinter.font.rst
   dialog.rst
   tkinter.messagebox.rst
   tkinter.scrolledtext.rst
   tkinter.dnd.rst
   tkinter.ttk.rst
   tkinter.tix.rst
   idle.rst

.. Other sections I have in mind are
   Tkinter internals
   Freezing Tkinter applications
