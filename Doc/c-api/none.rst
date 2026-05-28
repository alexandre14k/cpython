.. highlight:: c

.. _noneobject:

The ``None`` Object
-------------------

.. index:: pair: object; None

Note that the :c:type:`PyTypeObject` for ``None`` is not directly exposed in the
MyFRpy/C API.  Since ``None`` is a singleton, testing for object identity (using
``==`` in C) is sufficient. There is no :c:func:`!PyNone_Check` function for the
same reason.


.. c:var:: PyObject* Py_None

   The MyFRpy ``None`` object, denoting lack of value.  This object has no methods
   and is `immortal <https://peps.myFRpy.org/pep-0683/>`_.

.. versionchanged:: 3.12
   :c:data:`Py_None` is immortal.

.. c:macro:: Py_RETURN_NONE

   Return :c:data:`Py_None` from a function.
