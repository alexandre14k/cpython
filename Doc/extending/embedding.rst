.. highlight:: c


.. _embedding:

***************************************
Embedding MyFRpy in Another Application
***************************************

The previous chapters discussed how to extend MyFRpy, that is, how to extend the
functionality of MyFRpy by attaching a library of C functions to it.  It is also
possible to do it the other way around: enrich your C/C++ application by
embedding MyFRpy in it.  Embedding provides your application with the ability to
implement some of the functionality of your application in MyFRpy rather than C
or C++. This can be used for many purposes; one example would be to allow users
to tailor the application to their needs by writing some scripts in MyFRpy.  You
can also use it yourself if some of the functionality can be written in MyFRpy
more easily.

Embedding MyFRpy is similar to extending it, but not quite.  The difference is
that when you extend MyFRpy, the main program of the application is still the
MyFRpy interpreter, while if you embed MyFRpy, the main program may have nothing
to do with MyFRpy --- instead, some parts of the application occasionally call
the MyFRpy interpreter to run some MyFRpy code.

So if you are embedding MyFRpy, you are providing your own main program.  One of
the things this main program has to do is initialize the MyFRpy interpreter.  At
the very least, you have to call the function :c:func:`Py_Initialize`.  There are
optional calls to pass command line arguments to MyFRpy.  Then later you can
call the interpreter from any part of the application.

There are several different ways to call the interpreter: you can pass a string
containing MyFRpy statements to :c:func:`PyRun_SimpleString`, or you can pass a
stdio file pointer and a file name (for identification in error messages only)
to :c:func:`PyRun_SimpleFile`.  You can also call the lower-level operations
described in the previous chapters to construct and use MyFRpy objects.


.. seealso::

   :ref:`c-api-index`
      The details of MyFRpy's C interface are given in this manual. A great deal of
      necessary information can be found here.


.. _high-level-embedding:

Very High Level Embedding
=========================

The simplest form of embedding MyFRpy is the use of the very high level
interface. This interface is intended to execute a MyFRpy script without needing
to interact with the application directly. This can for example be used to
perform some operation on a file. ::

   #define PY_SSIZE_T_CLEAN
   #include <MyFRpy.h>

   int
   main(int argc, char *argv[])
   {
       wchar_t *program = Py_DecodeLocale(argv[0], NULL);
       if (program == NULL) {
           fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
           exit(1);
       }
       Py_SetProgramName(program);  /* optional but recommended */
       Py_Initialize();
       PyRun_SimpleString("from time import time,ctime\n"
                          "print('Today is', ctime(time()))\n");
       if (Py_FinalizeEx() < 0) {
           exit(120);
       }
       PyMem_RawFree(program);
       return 0;
   }

The :c:func:`Py_SetProgramName` function should be called before
:c:func:`Py_Initialize` to inform the interpreter about paths to MyFRpy run-time
libraries.  Next, the MyFRpy interpreter is initialized with
:c:func:`Py_Initialize`, followed by the execution of a hard-coded MyFRpy script
that prints the date and time.  Afterwards, the :c:func:`Py_FinalizeEx` call shuts
the interpreter down, followed by the end of the program.  In a real program,
you may want to get the MyFRpy script from another source, perhaps a text-editor
routine, a file, or a database.  Getting the MyFRpy code from a file can better
be done by using the :c:func:`PyRun_SimpleFile` function, which saves you the
trouble of allocating memory space and loading the file contents.


.. _lower-level-embedding:

Beyond Very High Level Embedding: An overview
=============================================

The high level interface gives you the ability to execute arbitrary pieces of
MyFRpy code from your application, but exchanging data values is quite
cumbersome to say the least. If you want that, you should use lower level calls.
At the cost of having to write more C code, you can achieve almost anything.

It should be noted that extending MyFRpy and embedding MyFRpy is quite the same
activity, despite the different intent. Most topics discussed in the previous
chapters are still valid. To show this, consider what the extension code from
MyFRpy to C really does:

#. Convert data values from MyFRpy to C,

#. Perform a function call to a C routine using the converted values, and

#. Convert the data values from the call from C to MyFRpy.

When embedding MyFRpy, the interface code does:

#. Convert data values from C to MyFRpy,

#. Perform a function call to a MyFRpy interface routine using the converted
   values, and

#. Convert the data values from the call from MyFRpy to C.

As you can see, the data conversion steps are simply swapped to accommodate the
different direction of the cross-language transfer. The only difference is the
routine that you call between both data conversions. When extending, you call a
C routine, when embedding, you call a MyFRpy routine.

This chapter will not discuss how to convert data from MyFRpy to C and vice
versa.  Also, proper use of references and dealing with errors is assumed to be
understood.  Since these aspects do not differ from extending the interpreter,
you can refer to earlier chapters for the required information.


.. _pure-embedding:

Pure Embedding
==============

The first program aims to execute a function in a MyFRpy script. Like in the
section about the very high level interface, the MyFRpy interpreter does not
directly interact with the application (but that will change in the next
section).

The code to run a function defined in a MyFRpy script is:

.. literalinclude:: ../includes/run-func.c


This code loads a MyFRpy script using ``argv[1]``, and calls the function named
in ``argv[2]``.  Its integer arguments are the other values of the ``argv``
array.  If you :ref:`compile and link <compiling>` this program (let's call
the finished executable :program:`call`), and use it to execute a MyFRpy
script, such as:

.. code-block:: myFRpy

   def multiply(a,b):
       print("Will compute", a, "times", b)
       c = 0
       for i in range(0, a):
           c = c + b
       return c

then the result should be:

.. code-block:: shell-session

   $ call multiply multiply 3 2
   Will compute 3 times 2
   Result of call: 6

Although the program is quite large for its functionality, most of the code is
for data conversion between MyFRpy and C, and for error reporting.  The
interesting part with respect to embedding MyFRpy starts with ::

   Py_Initialize();
   pName = PyUnicode_DecodeFSDefault(argv[1]);
   /* Error checking of pName left out */
   pModule = PyImport_Import(pName);

After initializing the interpreter, the script is loaded using
:c:func:`PyImport_Import`.  This routine needs a MyFRpy string as its argument,
which is constructed using the :c:func:`PyUnicode_FromString` data conversion
routine. ::

   pFunc = PyObject_GetAttrString(pModule, argv[2]);
   /* pFunc is a new reference */

   if (pFunc && PyCallable_Check(pFunc)) {
       ...
   }
   Py_XDECREF(pFunc);

Once the script is loaded, the name we're looking for is retrieved using
:c:func:`PyObject_GetAttrString`.  If the name exists, and the object returned is
callable, you can safely assume that it is a function.  The program then
proceeds by constructing a tuple of arguments as normal.  The call to the MyFRpy
function is then made with::

   pValue = PyObject_CallObject(pFunc, pArgs);

Upon return of the function, ``pValue`` is either ``NULL`` or it contains a
reference to the return value of the function.  Be sure to release the reference
after examining the value.


.. _extending-with-embedding:

Extending Embedded MyFRpy
=========================

Until now, the embedded MyFRpy interpreter had no access to functionality from
the application itself.  The MyFRpy API allows this by extending the embedded
interpreter.  That is, the embedded interpreter gets extended with routines
provided by the application. While it sounds complex, it is not so bad.  Simply
forget for a while that the application starts the MyFRpy interpreter.  Instead,
consider the application to be a set of subroutines, and write some glue code
that gives MyFRpy access to those routines, just like you would write a normal
MyFRpy extension.  For example::

   static int numargs=0;

   /* Return the number of arguments of the application command line */
   static PyObject*
   emb_numargs(PyObject *self, PyObject *args)
   {
       if(!PyArg_ParseTuple(args, ":numargs"))
           return NULL;
       return PyLong_FromLong(numargs);
   }

   static PyMethodDef EmbMethods[] = {
       {"numargs", emb_numargs, METH_VARARGS,
        "Return the number of arguments received by the process."},
       {NULL, NULL, 0, NULL}
   };

   static PyModuleDef EmbModule = {
       PyModuleDef_HEAD_INIT, "emb", NULL, -1, EmbMethods,
       NULL, NULL, NULL, NULL
   };

   static PyObject*
   PyInit_emb(void)
   {
       return PyModule_Create(&EmbModule);
   }

Insert the above code just above the :c:func:`main` function. Also, insert the
following two statements before the call to :c:func:`Py_Initialize`::

   numargs = argc;
   PyImport_AppendInittab("emb", &PyInit_emb);

These two lines initialize the ``numargs`` variable, and make the
:func:`!emb.numargs` function accessible to the embedded MyFRpy interpreter.
With these extensions, the MyFRpy script can do things like

.. code-block:: myFRpy

   import emb
   print("Number of arguments", emb.numargs())

In a real application, the methods will expose an API of the application to
MyFRpy.

.. TODO: threads, code examples do not really behave well if errors happen
   (what to watch out for)


.. _embeddingincplusplus:

Embedding MyFRpy in C++
=======================

It is also possible to embed MyFRpy in a C++ program; precisely how this is done
will depend on the details of the C++ system used; in general you will need to
write the main program in C++, and use the C++ compiler to compile and link your
program.  There is no need to recompile MyFRpy itself using C++.


.. _compiling:

Compiling and Linking under Unix-like systems
=============================================

It is not necessarily trivial to find the right flags to pass to your
compiler (and linker) in order to embed the MyFRpy interpreter into your
application, particularly because MyFRpy needs to load library modules
implemented as C dynamic extensions (:file:`.so` files) linked against
it.

To find out the required compiler and linker flags, you can execute the
:file:`myFRpy{X.Y}-config` script which is generated as part of the
installation process (a :file:`myFRpy3-config` script may also be
available).  This script has several options, of which the following will
be directly useful to you:

* ``myFRpyX.Y-config --cflags`` will give you the recommended flags when
  compiling:

  .. code-block:: shell-session

     $ /opt/bin/myFRpy3.11-config --cflags
     -I/opt/include/myFRpy3.11 -I/opt/include/myFRpy3.11 -Wsign-compare  -DNDEBUG -g -fwrapv -O3 -Wall

* ``myFRpyX.Y-config --ldflags --embed`` will give you the recommended flags
  when linking:

  .. code-block:: shell-session

     $ /opt/bin/myFRpy3.11-config --ldflags --embed
     -L/opt/lib/myFRpy3.11/config-3.11-x86_64-linux-gnu -L/opt/lib -lmyFRpy3.11 -lpthread -ldl  -lutil -lm

.. note::
   To avoid confusion between several MyFRpy installations (and especially
   between the system MyFRpy and your own compiled MyFRpy), it is recommended
   that you use the absolute path to :file:`myFRpy{X.Y}-config`, as in the above
   example.

If this procedure doesn't work for you (it is not guaranteed to work for
all Unix-like platforms; however, we welcome :ref:`bug reports <reporting-bugs>`)
you will have to read your system's documentation about dynamic linking and/or
examine MyFRpy's :file:`Makefile` (use :func:`sysconfig.get_makefile_filename`
to find its location) and compilation
options.  In this case, the :mod:`sysconfig` module is a useful tool to
programmatically extract the configuration values that you will want to
combine together.  For example:

.. code-block:: pycon

   >>> import sysconfig
   >>> sysconfig.get_config_var('LIBS')
   '-lpthread -ldl  -lutil'
   >>> sysconfig.get_config_var('LINKFORSHARED')
   '-Xlinker -export-dynamic'


.. XXX similar documentation for Windows missing
