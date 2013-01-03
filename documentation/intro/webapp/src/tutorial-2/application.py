#! /usr/bin/env python3
import datetime
import os
import sqlalchemy
from sqlalchemy import orm
from aurora import webapp
from aurora.webapp import foundation, mapping
from aurora.webcomponents import views

import models
from components import engine_provider

__all__ = ['Application']


class Application(webapp.Application):
    """ Web Blogging application
    """

    def __init__(self):
        super().__init__()

        self.mapper.add_rule(mapping.Route('/'), _handler=self.list_posts)
        self.mapper.add_rule(mapping.Route('/post/(?P<id>\d+)'),
            _handler=self.show_post)
        self.mapper.add_rule(mapping.Route('/compose'),
            _handler=self.add_post)

        # add the `templates` folder as template source for the `views`
        # component
        self.views.add_path(os.path.join(os.path.dirname(__file__),
            'templates'))
        self.views.add_default('url_for', self.url_for)

        # try to create the database tables if needed
        models.Post.metadata.create_all(self.db.get_engine())

    @property
    def views(self) -> views.Views:
        try:
            return self.__views
        except AttributeError:
            self.__views = views.Views()
            return self.__views

    @property
    def db(self) -> engine_provider.EngineProvider:
        try:
            return self.__db
        except AttributeError:
            self.__db = engine_provider.EngineProvider()
            return self.__db

    def list_posts(self, request: foundation.Request) -> foundation.Response:
        """ List summaries for posts added more recently. """
        orm_session = orm.sessionmaker(bind=self.db.get_engine())()

        return self.views.render2response(request, 'list.html',
            posts=orm_session.query(models.Post).order_by(
                sqlalchemy.desc(models.Post.date))[:10],
            blog=self)

    def show_post(self, request: foundation.Request) -> foundation.Response:
        """ Show a post. """
        post_id = request.params['id']

        orm_session = orm.sessionmaker(bind=self.db.get_engine())()

        return self.views.render2response(request, 'show.html',
            post=orm_session.query(models.Post).filter_by(id=post_id).one(),
            blog=self)

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

            orm_session = orm.sessionmaker(bind=self.db.get_engine())()
            orm_session.add(post)
            orm_session.commit()

            # redirect to the post page
            resp = request.response_factory()
            resp.status_int = 302
            resp.location = request.application_url

            return resp
        else:
            return self.views.render2response(request, 'form.html', blog=self)


if __name__ == '__main__':
    from wsgiref import simple_server
    from aurora.webapp import foundation

    wsgi_app = foundation.wsgi(Application())
    httpd = simple_server.make_server('', 8008, wsgi_app)

    print("Serving on port 8008...")
    httpd.serve_forever()