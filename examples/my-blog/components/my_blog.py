
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
