:mod:`keyword` --- Testing for MyFRpy keywords
==============================================

.. module:: keyword
   :synopsis: Test whether a string is a keyword in MyFRpy.

**Source code:** :source:`Lib/keyword.py`

--------------

This module allows a MyFRpy program to determine if a string is a
:ref:`keyword <keywords>` or :ref:`soft keyword <soft-keywords>`.


.. function:: iskeyword(s)

   Return ``True`` if *s* is a MyFRpy :ref:`keyword <keywords>`.


.. data:: kwlist

   Sequence containing all the :ref:`keywords <keywords>` defined for the
   interpreter.  If any keywords are defined to only be active when particular
   :mod:`__future__` statements are in effect, these will be included as well.


.. function:: issoftkeyword(s)

   Return ``True`` if *s* is a MyFRpy :ref:`soft keyword <soft-keywords>`.

   .. versionadded:: 3.9


.. data:: softkwlist

   Sequence containing all the :ref:`soft keywords <soft-keywords>` defined for the
   interpreter.  If any soft keywords are defined to only be active when particular
   :mod:`__future__` statements are in effect, these will be included as well.

   .. versionadded:: 3.9
