=========================================
Writing your first Aurora Web application
=========================================

In this tutorial you will learn by example how to create a Web based Blog
application using the Aurora Web application framework.

Creating the Web application
============================

.. admonition:: Scaffolding

    Currently the Aurora Web application framework doesn't provide a tool to
    automate the task of creating scaffolds for a new Web application,
    it must be done by hand.

First you need to create a folder that host all application specific files,
lets call this folder `my-blog`. Inside that folder create a `Python`_ source
file named `application.py`, we will use this file to host the Web
application definition. Open the file once created in your preferred text
editor and write the following::

    #! /usr/bin/env python3
    from aurora.webapp import infrastructure

    __all__ = ['Application']

    class Application(infrastructure.Application):
        """ MyBlog Application
        """

    if __name__ == '__main__':
        from wsgiref import simple_server
        from aurora.webapp import foundation

        wsgi_app = foundation.wsgi(Application())
        httpd = simple_server.make_server('', 8008, wsgi_app)

        print("Serving on port 8008...")
        httpd.serve_forever()

Until now we have a class that define a new Web application (that do nothing
yet) and a little piece of code used to run the application using the
`WSGI`_ Web server shipped with the `Python`_ standard library.

Adding application specific components
======================================
We are going to add the services that provide the Blog specific features into
a isolated component, this way the Blog features can be reused in other
applications. Lets create a `Python`_ source package named `components`
inside the application folder to hold the application specific components.
Inside that `Python`_ source package add a `Python`_ source file named
`my_blog.py` with the following content::



    __all__ = ['MyBlog']


    class MyBlog:
        """ Component that provide Web blogging services. """

        #
        # services provide by component
        #

        def list_posts(self):
            """ List posts added more recently. """

        def show_post(self):
            """ Show a post. """

        def add_post(self):
            """ Add a new Blog post. """


The `Python`_  source file provide a component definition (a class) that
expose the three basic services (methods) all blogging applications should
provide. Now we are ready to add the blogging features to our new Web
application, modify the Web application definition `Python`_ source file as
follows::

    #! /usr/bin/env python3
    from aurora.webapp import infrastructure
    from components import my_blog

    __all__ = ['Application']

    class Application(infrastructure.Application):
        """ MyBlog Application
        """

        @property
        def my_blog(self) -> my_blog.MyBlog:
            try:
                return self.__my_blog
            except AttributeError:
                self.__my_blog = my_blog.MyBlog()
                return self.__my_blog

    if __name__ == '__main__':
        from wsgiref import simple_server
        from aurora.webapp import foundation

        wsgi_app = foundation.wsgi(Application())
        httpd = simple_server.make_server('', 8008, wsgi_app)

        print("Serving on port 8008...")
        httpd.serve_forever()

The only change is the addition of a property to the Web application class
that provide the Blogging component (and therefore its services), even though
the Web application does nothing with it yet.

Making services implement the Web request handling protocol
===========================================================
Before the Web application can expose the Blogging features to its users,
the Blogging services need to be transformed into Web request handlers. A Web
request handler by definition is any callable object that accept a Web
request object as first positional argument and return a Web response object.
The Web request handler must create the Web response object by calling the
`response_factory()` service of the Web request object, this way the caller
keep control of the objects involved in the Web request handling process.
The three services once modified will look like as follows::


     from aurora.webapp import foundation, mapping

     __all__ = ['MyBlog']


     class MyBlog:
         """ Component that provide Web blogging services. """

         #
         # services provide by component
         #

         def setup_mapping(self, mapper: mapping.Mapper, base_path=''):
             """ Setup default mapping of component services.
             :param mapper: The mapping target.
             :param base_path: The mapping base path.
             """
             mapper.add_rule(mapping.Route('/'.join((base_path, ''))),
                 _handler=self.list_posts)
             mapper.add_rule(mapping.Route('/'.join((base_path, 'post/(?P<id>\d+)'))),
                 _handler=self.show_post)
             mapper.add_rule(mapping.Route('/'.join((base_path, 'compose'))),
                 _handler=self.add_post)

         def list_posts(self, request: foundation.Request) -> foundation.Response:
             """ List posts added more recently. """
             return request.response_factory(text="list of posts")

         def show_post(self, request: foundation.Request) -> foundation.Response:
             """ Show a post. """
             return request.response_factory(text="post content")

         def add_post(self, request: foundation.Request) -> foundation.Response:
             """ Add a new Blog post. """
             return request.response_factory(text="post form")

The major changes are in the service implementations and their signatures.
Even though they are just scaffolds for the real implementations,
now they can be mapped as a characteristic for Web request paths (the
`_handler` characteristic to be more specific). A `Python`_ module
(`aurora.webapp.foundation`) has been imported but just for documentation
purposes (on function annotations). Another modification is the addition of a
new service used to provide a default Web request path mapping (the
`setup_mapping` service). This way component users can setup default
component service Web request path mapping in a simple way. The mapping setup
service take as argument the mapper to setup. It use the
:class:`~aurora.webapp.mapping.Route`
:class:`mapping rule <aurora.webapp.mapping.Rule>` implementation to create the
mapping and the Web request handling service as the `_handler` characteristic.
The application need to be modified to call this service at initialization.
The code modified will look like this::

    #! /usr/bin/env python3
    from aurora.webapp import infrastructure
    from components import my_blog

    __all__ = ['Application']

    class Application(infrastructure.Application):
        """ MyBlog Application
        """

        def __init__(self):
            self.my_blog.setup_mapping(self.mapper)

        @property
        def my_blog(self) -> my_blog.MyBlog:
            try:
                return self.__my_blog
            except AttributeError:
                self.__my_blog = my_blog.MyBlog()
                return self.__my_blog

    if __name__ == '__main__':
        from wsgiref import simple_server
        from aurora.webapp import foundation

        wsgi_app = foundation.wsgi(Application())
        httpd = simple_server.make_server('', 8008, wsgi_app)

        print("Serving on port 8008...")
        httpd.serve_forever()

With all this code in place you can take your Web application for a ride. Run
your application in the console and with your preferred Web browser navigate
to `http://localhost:8008`, you will see the ``list of posts`` message. Try
the other paths mapped by the blogging component and see the results.

Well, this is all for now. In this tutorial you learn how to create a Web
application using the Aurora library, how to add components that provide
specific features to your Web application and how to write services that act
as Web request handlers. In the next part of this tutorial you will learn
how to integrate components shipped with the Aurora library to address common
needs and how to to create components to integrate third party libraries.

.. _Python: http://www.python.org/
.. _WSGI: http://www.wsgi.org/