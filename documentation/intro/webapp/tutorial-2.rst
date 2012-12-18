=======================================================
Writing your first Aurora based Web application, part 2
=======================================================

In this second part of the Web application tutorial you will learn how to
integrate components shipped with the Aurora library to address common needs
and how to create components to integrate third party libraries.

Before you start coding we recommend you to copy the `Python`_ module produced
in the first part of this tutorial named ``application`` into a new
folder named ``tutorial-2``. For cut and paste purposes, the source code for
all stages of this tutorial can be browsed at
`https://github.com/yeiniel/aurora/tree/master/documentation/intro/webapp/src/tutorial-2
<https://github.com/yeiniel/aurora/tree/master/documentation/intro/webapp/src/tutorial-2>`_.

Using views
===========
The `MVC`_ pattern is widely used in Web application development. Products
created using the Web application framework from the Aurora library are not
enforced to use this pattern or any other related to the concept of
separation of concerns (`MVP`_, etc). Even though the library provide a
component very useful to construct the ``View`` part for an `MVC`_ based
product (The :class:`~aurora.webcomponents.views.Views` component). Next we
are going to refactor our Web application to implement Web request handlers
using the `MVC`_ pattern. As a first step we are going to make accessible the
:class:`~aurora.webcomponents.views.Views` component from the Web application
services by adding it as a Web application attribute (property).

.. literalinclude:: src/tutorial-2/application.py
      :lines: 37-43
      :linenos:
      :language: py

This step require that you first import the :mod:`~aurora.webcomponents.views`
module. Now we are ready to modify the Web request handlers so they implement
the `MVC`_ pattern. The code will look as follows:

.. code-block:: python

        def list_posts(self, request: foundation.Request) -> foundation.Response:
            """ List summaries for posts added more recently. """
            return self.views.render2response(request, 'list.html')

        def show_post(self, request: foundation.Request) -> foundation.Response:
            """ Show a post. """
            return self.views.render2response(request, 'show.html')

        def add_post(self, request: foundation.Request) -> foundation.Response:
            """ Add a new Blog post. """
            if request.method == 'POST':
                # process form submission
                pass
            else:
                return self.views.render2response(request, 'form.html')

The Web request handler services has been modified to use the
:meth:`~aurora.webcomponents.views.Views.render2response` service. This
service takes a Web request object, the path of the template file (without
the last extension, read the API documentation for that service for more
information), an arbitrary number of arguments used as ``view`` context and
return the corresponding Web response object.

Once the Web application has been modified the only missing step is adding the
templates used to render the views, but we are going to do that latter once
we write the data persistence logic. Create a folder inside the Web
application folder named ``templates``, this is the one that we are going to
register as template source using the following snippet of code added to the
Web application :meth:`__init__` method:

.. literalinclude:: src/tutorial-2/application.py
      :lines: 29-33
      :linenos:
      :language: py

This snippet additionally add as default ``views`` context element the
:meth:`~aurora.webapp.infrastructure.Application.url_for` Web application
service used to create links on the Web responses.

At this point is recommended that you review the :ref:`webcomponents` section
of the :doc:`/api` and learn about other Web application components shipped
with the Aurora library.

Integrating SQLAlchemy
======================
`SQLAlchemy`_ is a powerful Database abstraction library writen in Python
that provide a ORM pattern implementation. We re going to use the ORM to
implement the data layer of the Web application (the M part of the `MVC`_
design pattern). In order to integrate the library into the application we
are going to add a new component and will name it ``engine_provider``. Add a
`Python`_ package named ``components`` to the Web application folder and
there add a `Python`_ module with that name with the following content:

.. literalinclude:: src/tutorial-2/components/engine_provider.py
      :linenos:
      :language: py

Once we have that component in place add Web application models into a
separated `Python`_ module named ``models`` in the Web application folder as
follows:

.. literalinclude:: src/tutorial-2/models.py
      :linenos:
      :language: py


Now to make the models available to the Web application definition we need to
add the following import line:

.. literalinclude:: src/tutorial-2/application.py
      :lines: 11
      :linenos:
      :language: py

As we do with the ``views`` component we need to make accessible the component
from the Web application services by importing the component `Python`_ module
into the Web application definition `Python`_ module and adding it as a Web
application attribute (property):

.. literalinclude:: src/tutorial-2/application.py
      :lines: 47-53
      :linenos:
      :language: py

Now to make things easy lets ensure that tables on database needed to
store the model data are available by adding the following line to the Web
application :meth:`__init__` method:

.. literalinclude:: src/tutorial-2/application.py
      :lines: 35-37
      :linenos:
      :language: py

And finally lets show you the Web request handlers services once modified to
use the :meth:`get_engine` service from the :class:`EngineProvider` component:

.. literalinclude:: src/tutorial-2/application.py
      :lines: 55-97
      :linenos:
      :language: py

For this code to work you need first to import the following modules:
:mod:`datetime`, :mod:`sqlalchemy` and :mod:`sqlalchemy.orm`.

The used architecture allow us to share a common database connections across a
set  of components and provide different database engine for different
components if needed (consider the case you are using one component that use
specific  features from one database engine). Once we have the Blogging
application passing real data objects into the ``views`` we only need to
show you the templates used.

``templates/list.html.suba``

.. literalinclude:: src/tutorial-2/templates/list.html.suba
      :linenos:
      :language: html

``templates/summary.suba``

.. literalinclude:: src/tutorial-2/templates/summary.suba
      :linenos:
      :language: html

``templates/show.html.suba``

.. literalinclude:: src/tutorial-2/templates/show.html.suba
      :linenos:
      :language: html

``templates/form.html.suba``

.. literalinclude:: src/tutorial-2/templates/form.html.suba
      :linenos:
      :language: html

As you can guess by the template file extension this templates are using the
`suba`_  template engine, a lightweight template engine based on the mod (%)
operator.

Conclusion
==========
Well, this is all for now. In this tutorial you learn how to integrate
components provided by the Aurora library into your application and how to
create new ones to integrate third party libraries to provide your
Web application with features not provided by the Aurora library and you have
learn that the Aurora library provide a generic template based ``views``
framework with support by default for the `suba`_ template engine.

.. _MVC: http://en.wikipedia.org/wiki/Model–view–controller
.. _MVP: http://en.wikipedia.org/wiki/Model–view–presenter
.. _Python: http://www.python.org/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _suba: https://github.com/jldailey/suba
