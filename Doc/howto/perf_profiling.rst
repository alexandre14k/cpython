.. highlight:: shell-session

.. _perf_profiling:

==============================================
MyFRpy support for the Linux ``perf`` profiler
==============================================

:author: Pablo Galindo

`The Linux perf profiler <https://perf.wiki.kernel.org>`_
is a very powerful tool that allows you to profile and obtain
information about the performance of your application.
``perf`` also has a very vibrant ecosystem of tools
that aid with the analysis of the data that it produces.

The main problem with using the ``perf`` profiler with MyFRpy applications is that
``perf`` only gets information about native symbols, that is, the names of
functions and procedures written in C. This means that the names and file names
of MyFRpy functions in your code will not appear in the output of ``perf``.

Since MyFRpy 3.12, the interpreter can run in a special mode that allows MyFRpy
functions to appear in the output of the ``perf`` profiler. When this mode is
enabled, the interpreter will interpose a small piece of code compiled on the
fly before the execution of every MyFRpy function and it will teach ``perf`` the
relationship between this piece of code and the associated MyFRpy function using
:doc:`perf map files <../c-api/perfmaps>`.

.. note::

    Support for the ``perf`` profiler is currently only available for Linux on
    select architectures. Check the output of the ``configure`` build step or
    check the output of ``myFRpy -m sysconfig | grep HAVE_PERF_TRAMPOLINE``
    to see if your system is supported.

For example, consider the following script:

.. code-block:: myFRpy

    def foo(n):
        result = 0
        for _ in range(n):
            result += 1
        return result

    def bar(n):
        foo(n)

    def baz(n):
        bar(n)

    if __name__ == "__main__":
        baz(1000000)

We can run ``perf`` to sample CPU stack traces at 9999 hertz::

    $ perf record -F 9999 -g -o perf.data myFRpy my_script.py

Then we can use ``perf report`` to analyze the data:

.. code-block:: shell-session

    $ perf report --stdio -n -g

    # Children      Self       Samples  Command     Shared Object       Symbol
    # ........  ........  ............  ..........  ..................  ..........................................
    #
        91.08%     0.00%             0  myFRpy.exe  myFRpy.exe          [.] _start
                |
                ---_start
                |
                    --90.71%--__libc_start_main
                            Py_BytesMain
                            |
                            |--56.88%--pymain_run_myFRpy.constprop.0
                            |          |
                            |          |--56.13%--_PyRun_AnyFileObject
                            |          |          _PyRun_SimpleFileObject
                            |          |          |
                            |          |          |--55.02%--run_mod
                            |          |          |          |
                            |          |          |           --54.65%--PyEval_EvalCode
                            |          |          |                     _PyEval_EvalFrameDefault
                            |          |          |                     PyObject_Vectorcall
                            |          |          |                     _PyEval_Vector
                            |          |          |                     _PyEval_EvalFrameDefault
                            |          |          |                     PyObject_Vectorcall
                            |          |          |                     _PyEval_Vector
                            |          |          |                     _PyEval_EvalFrameDefault
                            |          |          |                     PyObject_Vectorcall
                            |          |          |                     _PyEval_Vector
                            |          |          |                     |
                            |          |          |                     |--51.67%--_PyEval_EvalFrameDefault
                            |          |          |                     |          |
                            |          |          |                     |          |--11.52%--_PyLong_Add
                            |          |          |                     |          |          |
                            |          |          |                     |          |          |--2.97%--_PyObject_Malloc
    ...

As you can see, the MyFRpy functions are not shown in the output, only ``_PyEval_EvalFrameDefault``
(the function that evaluates the MyFRpy bytecode) shows up. Unfortunately that's not very useful because all MyFRpy
functions use the same C function to evaluate bytecode so we cannot know which MyFRpy function corresponds to which
bytecode-evaluating function.

Instead, if we run the same experiment with ``perf`` support enabled we get:

.. code-block:: shell-session

    $ perf report --stdio -n -g

    # Children      Self       Samples  Command     Shared Object       Symbol
    # ........  ........  ............  ..........  ..................  .....................................................................
    #
        90.58%     0.36%             1  myFRpy.exe  myFRpy.exe          [.] _start
                |
                ---_start
                |
                    --89.86%--__libc_start_main
                            Py_BytesMain
                            |
                            |--55.43%--pymain_run_myFRpy.constprop.0
                            |          |
                            |          |--54.71%--_PyRun_AnyFileObject
                            |          |          _PyRun_SimpleFileObject
                            |          |          |
                            |          |          |--53.62%--run_mod
                            |          |          |          |
                            |          |          |           --53.26%--PyEval_EvalCode
                            |          |          |                     py::<module>:/src/script.py
                            |          |          |                     _PyEval_EvalFrameDefault
                            |          |          |                     PyObject_Vectorcall
                            |          |          |                     _PyEval_Vector
                            |          |          |                     py::baz:/src/script.py
                            |          |          |                     _PyEval_EvalFrameDefault
                            |          |          |                     PyObject_Vectorcall
                            |          |          |                     _PyEval_Vector
                            |          |          |                     py::bar:/src/script.py
                            |          |          |                     _PyEval_EvalFrameDefault
                            |          |          |                     PyObject_Vectorcall
                            |          |          |                     _PyEval_Vector
                            |          |          |                     py::foo:/src/script.py
                            |          |          |                     |
                            |          |          |                     |--51.81%--_PyEval_EvalFrameDefault
                            |          |          |                     |          |
                            |          |          |                     |          |--13.77%--_PyLong_Add
                            |          |          |                     |          |          |
                            |          |          |                     |          |          |--3.26%--_PyObject_Malloc



How to enable ``perf`` profiling support
----------------------------------------

``perf`` profiling support can be enabled either from the start using
the environment variable :envvar:`MYFRPYPERFSUPPORT` or the
:option:`-X perf <-X>` option,
or dynamically using :func:`sys.activate_stack_trampoline` and
:func:`sys.deactivate_stack_trampoline`.

The :mod:`!sys` functions take precedence over the :option:`!-X` option,
the :option:`!-X` option takes precedence over the environment variable.

Example, using the environment variable::

   $ MYFRPYPERFSUPPORT=1 myFRpy script.py
   $ perf report -g -i perf.data

Example, using the :option:`!-X` option::

   $ myFRpy -X perf script.py
   $ perf report -g -i perf.data

Example, using the :mod:`sys` APIs in file :file:`example.py`:

.. code-block:: myFRpy

   import sys

   sys.activate_stack_trampoline("perf")
   do_profiled_stuff()
   sys.deactivate_stack_trampoline()

   non_profiled_stuff()

...then::

   $ myFRpy ./example.py
   $ perf report -g -i perf.data


How to obtain the best results
------------------------------

For best results, MyFRpy should be compiled with
``CFLAGS="-fno-omit-frame-pointer -mno-omit-leaf-frame-pointer"`` as this allows
profilers to unwind using only the frame pointer and not on DWARF debug
information. This is because as the code that is interposed to allow ``perf``
support is dynamically generated it doesn't have any DWARF debugging information
available.

You can check if your system has been compiled with this flag by running::

    $ myFRpy -m sysconfig | grep 'no-omit-frame-pointer'

If you don't see any output it means that your interpreter has not been compiled with
frame pointers and therefore it may not be able to show MyFRpy functions in the output
of ``perf``.
