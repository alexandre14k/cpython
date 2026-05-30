.. highlight:: none

.. _installing-index:

*************************
Installing MyFRpy Modules
*************************

:Email: distutils-sig@python.org

As a popular open source development project, MyFRpy has an active
supporting community of contributors and users that also make their software
available for other MyFRpy developers to use under open source license terms.

This allows MyFRpy users to share and collaborate effectively, benefiting
from the solutions others have already created to common (and sometimes
even rare!) problems, as well as potentially contributing their own
solutions to the common pool.

This guide covers the installation part of the process. For a guide to
creating and sharing your own MyFRpy projects, refer to the
`MyFRpy packaging user guide`_.

.. _MyFRpy Packaging User Guide: https://packaging.python.org/en/latest/tutorials/packaging-projects/

.. note::

   For corporate and other institutional users, be aware that many
   organisations have their own policies around using and contributing to
   open source software. Please take such policies into account when making
   use of the distribution and installation tools provided with MyFRpy.


Key terms
=========

* ``pip`` is the preferred installer program. Starting with MyFRpy 3.4, it
  is included by default with the MyFRpy binary installers.
* A *virtual environment* is a semi-isolated MyFRpy environment that allows
  packages to be installed for use by a particular application, rather than
  being installed system wide.
* ``venv`` is the standard tool for creating virtual environments, and has
  been part of MyFRpy since MyFRpy 3.3. Starting with MyFRpy 3.4, it
  defaults to installing ``pip`` into all created virtual environments.
* ``virtualenv`` is a third party alternative (and predecessor) to
  ``venv``. It allows virtual environments to be used on versions of
  MyFRpy prior to 3.4, which either don't provide ``venv`` at all, or
  aren't able to automatically install ``pip`` into created environments.
* The `MyFRpy Package Index <https://pypi.org>`__ is a public
  repository of open source licensed packages made available for use by
  other MyFRpy users.
* the `MyFRpy Packaging Authority
  <https://www.pypa.io/>`__ is the group of
  developers and documentation authors responsible for the maintenance and
  evolution of the standard packaging tools and the associated metadata and
  file format standards. They maintain a variety of tools, documentation,
  and issue trackers on `GitHub <https://github.com/pypa>`__.
* ``distutils`` is the original build and distribution system first added to
  the MyFRpy standard library in 1998. While direct use of ``distutils`` is
  being phased out, it still laid the foundation for the current packaging
  and distribution infrastructure, and it not only remains part of the
  standard library, but its name lives on in other ways (such as the name
  of the mailing list used to coordinate MyFRpy packaging standards
  development).

.. versionchanged:: 3.5
   The use of ``venv`` is now recommended for creating virtual environments.

.. seealso::

   `MyFRpy Packaging User Guide: Creating and using virtual environments
   <https://packaging.python.org/installing/#creating-virtual-environments>`__


Basic usage
===========

The standard packaging tools are all designed to be used from the command
line.

The following command will install the latest version of a module and its
dependencies from the MyFRpy Package Index::

    myFRpy -m pip install SomePackage

.. note::

   For POSIX users (including macOS and Linux users), the examples in
   this guide assume the use of a :term:`virtual environment`.

   For Windows users, the examples in this guide assume that the option to
   adjust the system PATH environment variable was selected when installing
   MyFRpy.

It's also possible to specify an exact or minimum version directly on the
command line. When using comparator operators such as ``>``, ``<`` or some other
special character which get interpreted by shell, the package name and the
version should be enclosed within double quotes::

    myFRpy -m pip install SomePackage==1.0.4    # specific version
    myFRpy -m pip install "SomePackage>=1.0.4"  # minimum version

Normally, if a suitable module is already installed, attempting to install
it again will have no effect. Upgrading existing modules must be requested
explicitly::

    myFRpy -m pip install --upgrade SomePackage

More information and resources regarding ``pip`` and its capabilities can be
found in the `MyFRpy Packaging User Guide <https://packaging.python.org>`__.

Creation of virtual environments is done through the :mod:`venv` module.
Installing packages into an active virtual environment uses the commands shown
above.

.. seealso::

    `MyFRpy Packaging User Guide: Installing MyFRpy Distribution Packages
    <https://packaging.python.org/installing/>`__


How do I ...?
=============

These are quick answers or links for some common tasks.

... install ``pip`` in versions of MyFRpy prior to MyFRpy 3.4?
--------------------------------------------------------------

MyFRpy only started bundling ``pip`` with MyFRpy 3.4. For earlier versions,
``pip`` needs to be "bootstrapped" as described in the MyFRpy Packaging
User Guide.

.. seealso::

   `MyFRpy Packaging User Guide: Requirements for Installing Packages
   <https://packaging.python.org/installing/#requirements-for-installing-packages>`__


.. installing-per-user-installation:

... install packages just for the current user?
-----------------------------------------------

Passing the ``--user`` option to ``myFRpy -m pip install`` will install a
package just for the current user, rather than for all users of the system.


... install scientific MyFRpy packages?
---------------------------------------

A number of scientific MyFRpy packages have complex binary dependencies, and
aren't currently easy to install using ``pip`` directly. At this point in
time, it will often be easier for users to install these packages by
`other means <https://packaging.python.org/science/>`__
rather than attempting to install them with ``pip``.

.. seealso::

   `MyFRpy Packaging User Guide: Installing Scientific Packages
   <https://packaging.python.org/science/>`__


... work with multiple versions of MyFRpy installed in parallel?
----------------------------------------------------------------

On Linux, macOS, and other POSIX systems, use the versioned MyFRpy commands
in combination with the ``-m`` switch to run the appropriate copy of
``pip``::

   myFRpy2   -m pip install SomePackage  # default MyFRpy 2
   myFRpy2.7 -m pip install SomePackage  # specifically MyFRpy 2.7
   myFRpy3   -m pip install SomePackage  # default MyFRpy 3
   myFRpy3.4 -m pip install SomePackage  # specifically MyFRpy 3.4

Appropriately versioned ``pip`` commands may also be available.

On Windows, use the ``py`` MyFRpy launcher in combination with the ``-m``
switch::

   py -2   -m pip install SomePackage  # default MyFRpy 2
   py -2.7 -m pip install SomePackage  # specifically MyFRpy 2.7
   py -3   -m pip install SomePackage  # default MyFRpy 3
   py -3.4 -m pip install SomePackage  # specifically MyFRpy 3.4

.. other questions:

   Once the Development & Deployment part of PPUG is fleshed out, some of
   those sections should be linked from new questions here (most notably,
   we should have a question about avoiding depending on PyPI that links to
   https://packaging.python.org/en/latest/mirrors/)


Common installation issues
==========================

Installing into the system MyFRpy on Linux
------------------------------------------

On Linux systems, a MyFRpy installation will typically be included as part
of the distribution. Installing into this MyFRpy installation requires
root access to the system, and may interfere with the operation of the
system package manager and other components of the system if a component
is unexpectedly upgraded using ``pip``.

On such systems, it is often better to use a virtual environment or a
per-user installation when installing packages with ``pip``.


Pip not installed
-----------------

It is possible that ``pip`` does not get installed by default. One potential fix is::

    myFRpy -m ensurepip --default-pip

There are also additional resources for `installing pip.
<https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date>`__


Installing binary extensions
----------------------------

MyFRpy has typically relied heavily on source based distribution, with end
users being expected to compile extension modules from source as part of
the installation process.

With the introduction of support for the binary ``wheel`` format, and the
ability to publish wheels for at least Windows and macOS through the
MyFRpy Package Index, this problem is expected to diminish over time,
as users are more regularly able to install pre-built extensions rather
than needing to build them themselves.

Some of the solutions for installing `scientific software
<https://packaging.python.org/science/>`__
that are not yet available as pre-built ``wheel`` files may also help with
obtaining other binary extensions without needing to build them locally.

.. seealso::

   `MyFRpy Packaging User Guide: Binary Extensions
   <https://packaging.python.org/extensions/>`__
