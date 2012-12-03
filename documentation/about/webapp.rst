The Web application framework
=============================

The Web application framework contained in the :mod:`aurora.webapp` try to
deliver a product free of the issues discussed :doc:`here <why-aurora>`. The
framework is divided into three elements:

 * The foundation used to define the interface implemented by Web
   application components and services that want to be able to handle Web
   requests. This part of the framework is based on `WebOb`_ request and
   response wrappers.

 * The Web request path mapping interface and machinery used to allow the
   construction of Web applications based on multiple Web request handlers
   supporting different styles like pattern matching and object traversing.
   This part of the framework is totally independent and isolated into a
   `Python`_ module so you can event use it with other Web application
   framework.

 * The infrastructure used to built component based,
   complex Web applications with extensible Web request handling machinery.

The third element is build on top of the other two and provide the base
class used to define a Web application. The machinery and infrastructure
don't force you into using a given design pattern for Web request handling
implementation, but using a design pattern like `MVC`_ for example is not bad
and the examples shipped with the library code use this pattern extensively.

The foundation
--------------
The foundation is the specification of the objects involved in the
:class:`Web request <aurora.webapp.foundation.Request>` handling strategy (the
:class:`Web request <aurora.webapp.foundation.Request>`, the
:class:`Web response <aurora.webapp.foundation.Response>` and the
:class:`Web request handler <aurora.webapp.foundation.Handler>`). The
:class:`Web request <aurora.webapp.foundation.Request>` and the
:class:`Web response <aurora.webapp.foundation.Response>` are just subclasses
of `WebOb`_ request and response wrappers and the
:class:`Web request handler <aurora.webapp.foundation.Handler>` is any
callable object that accept as first positional argument a
:class:`Web request <aurora.webapp.foundation.Request>` object and return a
:class:`Web response <aurora.webapp.foundation.Response>` object.

The Web request handler must create the
:class:`Web response <aurora.webapp.foundation.Response>`  object by calling
the factory referenced by the
:attr:`~aurora.webapp.foundation.Request.response_factory` attribute of the
:class:`Web request <aurora.webapp.foundation.Request>` object. This way the
:class:`Web request handler <aurora.webapp.foundation.Handler>` can be
called using different request-response pairs (for testing purposes for
example). The following example shows a dummy
:class:`Web request handler <aurora.webapp.foundation.Handler>`::

    def handler(request):
        response = request.response_factory()

        return response


.. _MVC: http://en.wikipedia.org/wiki/Model–view–controller
.. _Python: http://www.python.org/
.. _WebOb: http://webob.org/
