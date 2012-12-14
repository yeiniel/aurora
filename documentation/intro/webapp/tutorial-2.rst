=================================================
Writing your first Aurora Web application, part 2
=================================================

In this second part of the Web application tutorial you will learn how to
integrate components shipped with the Aurora library to address common needs
and how to to create components to integrate third party libraries.

Using views
===========
The `MVC`_ pattern is widely used in Web application development. Products
created using the Web application framework from the Aurora library are not
enforced to use this pattern or any other related to the concept of
separation of concerns (`MVP`_, etc). Even though the library provide a
component very useful to construct the ``View`` part for an `MVC`_ based
product (The :class:`~aurora.webcomponents.views.Views` component). Next we
are going to refactor our Web application and associated blogging component to
implement Web request handlers using the `MVC`_ pattern. As a first step we
are going to modify the blogging component to explicitly declare its relation
with the service provided by the :class:`~aurora.webcomponents.views.Views`
component and to use that service on the Web request handler services:

.. code-block:: python

    import os
    from aurora.webapp import foundation, mapping
    from aurora.webcomponents import views

    __all__ = ['MyBlog']


    class MyBlog:
        """ Component that provide Web blogging services. """

        def __init__(self, render2response: views.Views.render2response):
            # setup component dependencies
            self.render2response = render2response

        #
        # component dependencies
        #

        def render2response(self, request: foundation.Request, template_name: str,
                            **context) -> foundation.Response:
            """ Render a template into a `webob.Response` object with context.

            :param request: The request object used to build the response.
            :param template_name: The relative template name string without the
                last extension.
            :param context: The context mapping.
            :return: The rendered `webob.Response` object.
            """
            raise NotImplementedError()

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
                _handler=self.add_post

        def setup_views(self, views: views.Views):
            """ Setup a :class:`~aurora.webcomponents.views.Views` component.

            This service allow the :class:`~aurora.webcomponents.views.Views`
            component to find templates associated with this component.

            :param views: The :class:`~aurora.webcomponents.views.Views` component.
            """
            # add template path
            views.add_path(os.path.join(os.path.dirname(__file__), 'templates'))

        def list_posts(self, request: foundation.Request) -> foundation.Response:
            """ List posts added more recently. """
            return self.render2response(request, 'my-blog/list.html')

        def show_post(self, request: foundation.Request) -> foundation.Response:
            """ Show a post. """
            return self.render2response(request, 'my-blog/show.html')

        def add_post(self, request: foundation.Request) -> foundation.Response:
            """ Add a new Blog post. """
            if request.method == 'POST':
                # process form submission
                pass
            else:
                return self.render2response(request, 'my-blog/form.html')

As you can see a strict dependency on a service is declared as a method with
no implementation with the same service signature. The service
implementation is passed at initialization, this allow a great degree of
granularity and control very useful on testing stage and during software
evolution. A new service has been added (the :meth:`setup_views` service) to
allow the :class:`~aurora.webcomponents.views.Views` component to use the
templates shipped with the component. The Web request handler services has
been modified to use the
:meth:`~aurora.webcomponents.views.Views.render2response` service. This
service takes a Web request object, the path of the template file (without
the last extension, read the API documentation for that service for more
information), an arbitrary number of arguments used as ``view`` context and
return the corresponding Web response object.

Now that the Web blogging component is ready to use the service provided by 
the Views service it's time to modify the Web application to inject required
service into the Web blogging component and to call Views component 
initialization service provided by the Web blogging component. The code once
modified look as follows:

.. code-block:: python

    #! /usr/bin/env python3
    from aurora.webapp import infrastructure
    from aurora.webcomponents import views
    from components import my_blog

    __all__ = ['Application']

    class Application(infrastructure.Application):
        """ MyBlog Application
        """

        def __init__(self):
            self.my_blog.setup_mapping(self.mapper)
            self.my_blog.setup_views(self.views)
        
        @property
        def views(self) -> views.Views:
            try:
                return self.__views
            except AttributeError:
                self.__views = views.Views()
                return self.__views
        
        @property
        def my_blog(self) -> my_blog.MyBlog:
            try:
                return self.__my_blog
            except AttributeError:
                self.__my_blog = my_blog.MyBlog(
                    self.views.render2response
                )
                return self.__my_blog

    if __name__ == '__main__':
        from wsgiref import simple_server
        from aurora.webapp import foundation

        wsgi_app = foundation.wsgi(Application())
        httpd = simple_server.make_server('', 8008, wsgi_app)

        print("Serving on port 8008...")
        httpd.serve_forever()

As you can see a new property (:attr:`views`) has been added to the Web 
application to hold the Views component. The property that hold the Web
blogging component (:attr:`my_blog`) has been modified to perform
the injection of the dependent service and the :meth:`setup_views` service 
is called at application initialization. Once the Web application and the 
component has been modified the only missing step is adding the templates 
to the `Python`_ source package where the Web blogging component is located.
Create a folder inside the `components` `Python`_ source package named
``templates``, this is the one registered by the blogging component
:meth:`setup_views` service as template source. Inside this folder create
another one named ```my-blog``.

At this point is recommended that you review the :ref:`webcomponents` section
of the :doc:`/api` and learn about other Web application components shipped
with the Aurora library.

Integrating SQLAlchemy
======================
`SQLAlchemy`_ is a powerful Database abstraction library writen in Python
that provide a ORM pattern implementation. We re going to use the ORM to
implement the data layer of the Web blogging component. In order to integrate
the library into the application we are going to add a new component and will
name it ``engine_provider``. Add a `Python`_ module with that name inside the 
`Python`_ package that hold the application specific components (the 
```components`` `Python`_ source package) with the following content::


    import sqlalchemy

    __all__ = ['EngineProvider']


    class EngineProvider:
        """ `SQLAlchemy`_ support provider.

        This component provide support for use the ``SQLAlchemy`` library to
        connect to one database. The `get_engine` method is the only exposed
        service.

        The source database is configured using the `dsn` component attribute.

        If you need different database connections in the same application you
        can create multiple instances of this component and distribute them as
        needed.

        .. _SQLAlchemy: http://www.sqlalchemy.org/
        """

        dsn = 'sqlite:///data/application.db'

        def __init__(self):
            self._engine = sqlalchemy.create_engine(self.dsn)

        def get_engine(self) -> sqlalchemy.engine.Engine:
            """ Return an `sqlalchemy` engine object.
            :return: a ready to use `sqlalchemy.engine.Engine` object.
            """
            return self._engine

Once we have the component, declare a strict depedency for this component 
service on the Web blogging component and modify the Bloggin services to use 
that service to implement the data model as follows:

.. code-block:: python
    
    import datetime
    import os
    import sqlalchemy
    from sqlalchemy.ext import declarative

    from aurora.webapp import foundation, mapping
    from aurora.webcomponents import views
    from . import engine_provider

    __all__ = ['MyBlog']


    Model = declarative.declarative_base()


    class Post(Model):
        __tablename__ = 'blog_post'

        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
        content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
        author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
        date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)


    class MyBlog:
        """ Component that provide Web blogging services. """

        def __init__(self, render2response: views.Views.render2response,
                get_engine: engine_provider.EngineProvider.get_engine):
            # setup component dependencies
            self.render2response = render2response
            self.get_engine = get_engine
            
            # try to create the database tables if needed
            Model.metadata.create_all(get_engine())

        #
        # component dependencies
        #

        def render2response(self, request: foundation.Request, template_name: str,
                            **context) -> foundation.Response:
            """ Render a template into a `webob.Response` object with context.

            :param request: The request object used to build the response.
            :param template_name: The relative template name string without the
                last extension.
            :param context: The context mapping.
            :return: The rendered `webob.Response` object.
            """
            raise NotImplementedError()
        
        def get_engine(self) -> sqlalchemy.engine.Engine:
            """ Return an :class:`sqlalchemy.engine.Engine` object.
            :return: a ready to use :class:`sqlalchemy.engine.Engine` object.
            """
            raise NotImplementedError()

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
                _handler=self.add_post

        def setup_views(self, views: views.Views):
            """ Setup a :class:`~aurora.webcomponents.views.Views` component.

            This service allow the :class:`~aurora.webcomponents.views.Views`
            component to find templates associated with this component.

            :param views: The :class:`~aurora.webcomponents.views.Views` component.
            """
            # add template path
            views.add_path(os.path.join(os.path.dirname(__file__), 'templates'))

        def list_posts(self, request: foundation.Request) -> foundation.Response:
            """ List posts added more recently. """
            orm_session = orm.sessionmaker(bind=self.get_engine())()
            
            return self.render2response(request, 'my-blog/list.html',
                posts=orm_session.query(models.Post).order_by(
                    sqlalchemy.desc(models.Post.date))[:10])

        def show_post(self, request: foundation.Request) -> foundation.Response:
            """ Show a post. """
            post_id = request.params['id']

            orm_session = orm.sessionmaker(bind=self.get_engine())()
            
            return self.render2response(request, 'my-blog/show.html',
                post=orm_session.query(models.Post).filter_by(id=post_id).one())

        def add_post(self, request: foundation.Request) -> foundation.Response:
            """ Add a new Blog post. """
            if request.method == 'POST':
                # process form submission
                # TODO: need to implement form validation here.
                post = models.Post(
                    title=request.POST['title'],
                    content=request.POST['content'],
                    author='',
                    date=datetime.datetime.utcnow(),
                )

                orm_session = orm.sessionmaker(bind=self.get_engine())()
                orm_session.add(post)
                orm_session.commit()

                # redirect to the post page
                resp = request.ResponseClass()
                resp.status_int = 302
                resp.location = request.application_url

                return resp
            else:
                return self.render2response(request, 'my-blog/form.html')

This architecture allow us to share a common database connections across a set 
of components and provide different database engine for different components if
needed (consider the case you are using one component that use specific 
features from one database engine). Once we have the Blogging component passing
real data objects into the views we only need to update the view templates to 
use that data.

.. _MVC: http://en.wikipedia.org/wiki/Model–view–controller
.. _MVP: http://en.wikipedia.org/wiki/Model–view–presenter
.. _Python: http://www.python.org/
.. _SQLAlchemy: http://www.sqlalchemy.org/
