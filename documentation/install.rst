Installing Aurora
=================

Before You Install
------------------

Aurora has been writen using Python 3 syntax and therefore you will need
`Python`_ version 3.2 or better to install the library.

.. sidebar:: Python Versions

    As of this writing, Aurora has been tested under Python 3.2 and
    Python 3.3.  Aurora does not run under any version of `Python`_
    before 3.2.

Aurora is known to run on Debian Linux distribution as well as on Windows XP
platform. The installation does not require the compilation of any C code,
so you need only a `Python`_ interpreter that meets the requirements
mentioned.

Installing Aurora on a UNIX System
----------------------------------

It is best practice to install Aurora into a "virtual" `Python`_ environment
in order to obtain isolation from any "system" packages you've got installed
in your `Python`_ version.  This can be done by using the ``virtualenv``
package.  Using a virtualenv will also prevent Aurora from globally
installing versions of packages that are not compatible with your system
`Python`_.

To set up a virtualenv in which to install Aurora,
first ensure that ``setuptools`` is installed.  Invoke ``import
setuptools`` within the `Python`_ interpreter you'd like to run
Aurora under:

If running ``import setuptools`` does not raise an ``ImportError``, it
means that setuptools is already installed into your `Python`_
interpreter.  If ``import setuptools`` fails, you will need to install
setuptools manually.

If you are using a "system" `Python`_ (one installed by your OS
distributor or a 3rd-party packager such as Fink or MacPorts), you can
usually install the setuptools package by using your system's package
manager.  If you cannot do this, or if you're using a self-installed
version of Python, you will need to install setuptools "by hand".
Installing setuptools "by hand" is always a reasonable thing to do,
even if your package manager already has a pre-chewed version of
setuptools for installation.

To install setuptools by hand, first download `ez_setup.py
<http://peak.telecommunity.com/dist/ez_setup.py>`_ then invoke it
using the Python interpreter into which you want to install
setuptools.

.. code-block:: text

   $ python ez_setup.py

Once this command is invoked, setuptools should be installed on your
system.  If the command fails due to permission errors, you may need
to be the administrative user on your system to successfully invoke
the script.  To remediate this, you may need to do:

.. code-block:: text

   $ sudo python ez_setup.py

Installing the ``virtualenv`` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've got setuptools installed, you should install the
``virtualenv`` package.  To install the ``virtualenv`` package
into your setuptools-enabled Python interpreter, use the
``easy_install`` command.

.. code-block:: text

   $ easy_install virtualenv

This command should succeed, and tell you that the virtualenv package is now
installed.  If it fails due to permission errors, you may need to install it
as your system's administrative user.  For example:

.. code-block:: text

   $ sudo easy_install virtualenv

.. index::
   single: virtualenv
   pair: Python; virtual environment

Creating the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the ``virtualenv`` package is installed in your Python, you
can then create a virtual environment.  To do so, invoke the
following:

.. code-block:: text

   $ virtualenv --no-site-packages env
   New python executable in env/bin/python
   Installing setuptools.............done.

.. warning::

   Using ``--no-site-packages`` when generating your
   virtualenv is *very important*. This flag provides the necessary
   isolation for running the set of packages required by
   Aurora.  If you do not specify ``--no-site-packages``,
   it's possible that Aurora will not install properly into
   the virtualenv, or, even if it does, may not run properly,
   depending on the packages you've already got installed into your
   Python's "main" site-packages dir.

.. warning:: *do not* use ``sudo`` to run the
   ``virtualenv`` script.  It's perfectly acceptable (and desirable)
   to create a virtualenv as a normal user.

You should perform any following commands that mention a "bin"
directory from within the ``env`` virtualenv dir.

Installing Aurora Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``env`` virtualenv installed, you may install
Aurora itself using the following commands from within the virtualenv
(``env``) directory you created in the last step.

.. code-block:: text

   $ cd env
   $ bin/easy_install aurora

The ``easy_install`` command will take longer than the previous ones to
complete, as it downloads and installs a number of dependencies.

What Gets Installed
-------------------

When you ``easy_install`` Aurora, various other libraries such as
WebOb, and others are installed.

.. _Python: http://www.python.org/
