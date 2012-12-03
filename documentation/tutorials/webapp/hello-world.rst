Hello World application tutorial
================================

This tutorial introduce the audience in the concept of a
:class:`Web request handler <aurora.webapp.foundation.Handler>` and create a
simple one that shows a simple Hello World! message in the client browser. No
framework machinery or infrastructure is used, this tutorial only introduce
the concepts outlined in the Web application framework foundation. Ensure
before you test the code provided in this tutorial that you install first
the Aurora library. If you don't know how then read :doc:`here </install>`.

As stated in the
:doc:`description of the Web application framework </about/webapp>`, the
foundation provide an interface for objects that want to be able to handle
Web requests. This interface is described by the
:class:`~aurora.webapp.foundation.Handler` class. Basically, any callable that
accept a :class:`Web request <aurora.webapp.foundation.Request>` as argument
and return the produced
:class:`Web response<aurora.webapp.foundation.Response>` object is a valid
:class:`Web request handler <aurora.webapp.foundation.Handler>`.

Then we can implement the
:class:`Web request handler <aurora.webapp.foundation.Handler>` as a
function as follows::

    #! /usr/bin/env python3

    from aurora.webapp import foundation

    __all__ = ['application']

    def application(request: foundation.Request) -> foundation.Response:
        """ Web request handler. """
        return request.response_factory(text="Hello World!")

    if __name__ == '__main__':
        from wsgiref import simple_server
        wsgi_app = foundation.wsgi(application)
        httpd = simple_server.make_server('', 8008, wsgi_app)

        print("Serving on port 8008...")
        httpd.serve_forever()

The actual :class:`Web request handler <aurora.webapp.foundation.Handler>`
is the function ``application``. The remaining code is just for documenting
purposes (the beauty of `Python 3 <http://www.python.org/>`_) and to provide
a way of running the application using the Web server provided by the
standard library.

If you save the preceding code into a source file and run that file in the
console you will have a Web server listening on port ``8008`` and ready to
forward all Web requests to your ``application``. Now open your preferred Web
browser, type ``http://localhost:8008`` in the address bar and admire a simple
Web application that say you ``Hello World!``.

Testing our Web request handler
-------------------------------

The :class:`aurora.tests.webapp.test_handler.TestHandler` class provide the
tests needed to ensure the compliance of the
:class:`Web request handler <aurora.webapp.foundation.Handler>` protocol.
You should always test your handlers by inheriting
:class:`this <aurora.tests.webapp.test_handler.TestHandler>` class as
follows::

    #! /usr/bin/env python3

    import unittest
    from aurora.webapp import testing
    import application

    class TestApplication(testing.TestHandler):

        handler_factory = lambda self: application.application

        def test_response_content(self):
            """ Response content test.

            The :class:`Web response <aurora.webapp.foundation.Response>` object
            returned by the call to the Web request handler must have `Hello
            World!` as content.
            """
            request = self.request_factory({})
            response = self.handler(request)

            self.assertEqual(response.text, 'Hello World!', __doc__)

    if __name__ == "__main__":
        unittest.main()

Here we provide a test to ensure the Web request handler is returning the
right  content.

Well, this is it. The full source code of this application and its test can
be found in the example folder of the library distribution package.
