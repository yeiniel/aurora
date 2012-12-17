=======================================================
Writing your first Aurora based Web application, part 1
=======================================================

In this tutorial you will learn by example how to create a Web based Blogging
application using the Aurora Web application framework.

For cut and paste purposes, the source code for all stages of this
tutorial can be browsed at
`https://github.com/yeiniel/aurora/tree/master/documentation/intro/webapp/src/tutorial-1
<https://github.com/yeiniel/aurora/tree/master/documentation/intro/webapp/src/tutorial-1>`_.

Basic Layout
============
.. admonition:: Scaffolding

    Currently the Aurora Web application framework doesn't provide a tool to
    automate the task of creating scaffolds for a new Web application,
    it must be done by hand.

Before we start coding our Web application we need to setup the basic layout
for it. First you need to create a folder that host all application's specific
files, lets call this folder `tutorial-1`. Inside that folder create a
`Python`_ module named ``application``, we will use this module to host the
Web application definition. Open the module file once created in your
preferred text editor and write the following:

.. literalinclude:: src/tutorial-1/application.py
      :lines: 1-2,5-11,93-
      :linenos:
      :language: py

This `Python`_ module define a class (the :class:`Application` class) that
inherit from a base class provided by the Web application framework, this is
the Web application definition. Additional code is provided to allow the
module to be executed directly as a console application, in this case the
`WSGI`_ Web server shipped with the `Python`_ standard library is used to
serve a Web application based on that definition on port ``8008``.

If you execute this module at the console and open the
`http://localhost:8008/ <http://localhost:8008/>`_ address in your preferred
Web browser you will see a default and simple ``Not Found`` message. This is
correct and it means you did not setup a Web request path mapping that
associate a Web request handler to the base Web application path. As you can
see the Web application framework doesn't do any magic for you and this is one
of its design principles.

Defining the Blogging services
==============================
There are three services that all Blogging's platforms provide:

 - present summary of recently published Posts.
 - present a published Post.
 - form for composing a new Post.

We are going to implement this three services into our Web application. As a
first step we are going to add the corresponding three service definitions
stubs (methods) to the Web application definition (class) as follows:

.. literalinclude:: src/tutorial-1/application.py
      :lines: 19-91
      :linenos:
      :language: py

As you can see, an additional `Python`_ module has been imported, and used to
annotate the three service definition stubs (the
:mod:`aurora.webapp.foundation` module). This has been done to make clear to
any user that read the source code, that this three services implement the Web
request handling protocol. By making this three services implement this
protocol (interface), we make them able to handle Web requests (read the
:class:`~aurora.webapp.foundation.Handler` documentation for more information).
But if you restart your Web application at the console once you make the
changes to your copy of the `Python`_ module, you will not going to
be able to see this services at action because the Web application don't know
which Web requests map to the different services that implement the Web
request handling protocol (remember that the Web application framework don't
do magic for you).

Mapping Web request paths to Web request handlers
=================================================
Now we are going to add code that map this three services as Web request path
characteristic (specifically the ``_handler`` characteristic) with the Web
application :attr:`~aurora.webapp.infrastructure.Application.mapper`, this
way the Web application will know which Web requests sent to the three
different Web request handlers. The code looks as follows:

.. literalinclude:: src/tutorial-1/application.py
      :lines: 12-17
      :linenos:
      :language: py

As you can see, an additional `Python`_ module has been imported (the
:mod:`aurora.webapp.mapping` module), and used to create the Web request path
rules used to map the tree Web request handlers. Once that you update your
Web application definition code, restart your Web application running at the
console and refresh the `http://localhost:8008/ <http://localhost:8008/>`_
address in your browser. You will see the list of Posts summaries produced by
the stub, from there you can browse to the pages of the independent Posts.

Conclusion
==========
Well, this is all for now. In this tutorial you learn how to create a Web
application using the Aurora library and how to write services that act
as Web request handlers. In the :doc:`next<tutorial-2>` part of this tutorial
you will learn how to integrate components shipped with the Aurora library to
address common needs and how to to create components to integrate third
party libraries.

.. _Python: http://www.python.org/
.. _WSGI: http://www.wsgi.org/