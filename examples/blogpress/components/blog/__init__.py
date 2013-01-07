# Copyright (c) 2011, Yeiniel Suarez Sosa.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of Yeiniel Suarez Sosa. nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import os

import sqlalchemy
from sqlalchemy import engine, orm

from aurora.webapp import foundation, infrastructure, mapping
from aurora.webcomponents import layout, views

from components import engine_provider

from . import models

__all__ = ['Blog']


class Blog:
    """ Blogging service provider.

    This component provide the three common services all blogging platforms
    provide (listing posts, showing posts and composing posts). It has three
    dependencies:

     - A :meth:`engine_provider.EngineProvider.get_engine` compliant service
       used to access and persist information into a relational database.

     - A :meth:`aurora.webcomponents.views.Views.render2response` compliant
       service used to implement the ``View`` part of the ``MVC`` design
       pattern.

     - A :meth:`aurora.webapp.infrastructure.Application.url_for` compliant
       service used to create suitable URLs for known Web request handlers.

    This component can be simply installed into your Web application by
    calling the two services (:meth:`setup_mapping` and :meth:`setup_views`)
    used to setup the component.

    The Web requests handler provided by this component produce partial
    content and therefore you need to use the
    :class:`aurora.webcomponents.layout.Layout` component to produce the
    final HTML output.
    """

    def __init__(self, get_engine: engine_provider.EngineProvider.get_engine,
                 render2response: views.Views.render2response,
                 url_for: infrastructure.Application.url_for):
        self.get_engine = get_engine
        self.render2response = render2response
        self.url_for = url_for

        # create the model tables if they don't exist
        models.Model.metadata.create_all(self.get_engine())

    #
    # stubs for services required by the component
    #

    def get_engine(self) -> engine.Engine:
        """ Return a :class:`sqlalchemy.engine.Engine` object.

        :return: A ready to use :class:`sqlalchemy.engine.Engine` object.
        """
        raise NotImplementedError()

    def render2response(self, request: foundation.Request, template_name: str,
                        **context) -> foundation.Response:
        """ Render a template into a :class:`~aurora.webapp.foundation.Response` object with context.

        Template file names must have two extensions. The first extension is
        used to identify the content type of the output and the second
        extension is used to identify the engine capable of handling
        correctly the syntax used in the template.

        :param request: The request object used to build the response.
        :param template_name: The relative template name string without the
            last extension.
        :param context: The context mapping.
        :return: The rendered :class:`~aurora.webapp.foundation.Response`
            object.
        """
        raise NotImplementedError()
    
    def url_for(self, **characteristics) -> str:
        """ Create a fully usable url.

        :param characteristics: The Web request path characteristics.
        :return: A fully usable url.
        """
        raise NotImplementedError()

    def get_profile_id(self, request: foundation.Request) -> str:
        """ Return the profile ID for the user related to the Web request.
        :param request: A Web request object.
        :return: The profile ID string.
        """
        return 'admin'

    #
    # services provided by the component
    #

    def setup_mapping(self, add_rule: mapping.Mapper.add_rule, base_path='/'):
        add_rule(mapping.Route(base_path), _handler=self.list_posts)
        add_rule(mapping.Route(''.join((base_path, '(?P<id>\d+)'))),
            _handler=self.show_post)
        add_rule(mapping.Route(''.join((base_path, 'compose'))),
            _handler=self.compose_post)

    def setup_views(self, add_path: views.Views.add_path):
        add_path(os.path.join(os.path.dirname(__file__), 'templates'))

    @layout.partial
    def list_posts(self, request: foundation.Request) -> foundation.Response:
        """ List summaries for posts added more recently. """
        orm_session = orm.sessionmaker(bind=self.get_engine())()

        return self.render2response(request, 'blog/list.html',
            posts=orm_session.query(models.Post).filter(
                models.Post.published != None).order_by(
                sqlalchemy.desc(models.Post.published))[:10],
            blog=self, url_for=self.url_for)

    @layout.partial
    def show_post(self, request: foundation.Request) -> foundation.Response:
        """ Present a Blog post on the client browser.

        The value of the element from the `params` request mapping with
        keyword `id` is used as table row id if present.

        :param request: The
            :class:`Web request <aurora.webapp.foundation.Request>` object.
        :return: A :class:`Web response <aurora.webapp.foundation.Response>`
            object.
        """

        id = request.params['id']

        orm_session = orm.sessionmaker(bind=self.get_engine())()

        post = orm_session.query(models.Post).filter_by(id=id).one()

        return self.render2response(request, 'blog/show.html', post=post,
            blog=self, url_for=self.url_for)

    @layout.partial
    def compose_post(self, request: foundation.Request) -> foundation.Response:
        """ Present a form on the client browser used to compose a new Post.

        If the request method is ``POST`` this Web request handler attempt to
        process and persist the Blog post.

        :param request: The
            :class:`Web request <aurora.webapp.foundation.Request>` object.
        :return: A :class:`Web response <aurora.webapp.foundation.Response>`
            object.
        """
        if request.method == 'POST':
            # process form submission
            # TODO: need to implement form validation here.
            post = models.Post(
                title=request.POST['title'],
                content=request.POST['content'],
                author=self.get_profile_id(request),
                created = datetime.datetime.utcnow(),
                modified = datetime.datetime.utcnow(),
                published=datetime.datetime.utcnow(),
            )

            orm_session = orm.sessionmaker(bind=self.get_engine())()
            orm_session.add(post)
            orm_session.commit()

            # redirect to the post page
            resp = request.response_factory()
            resp.status_int = 302
            resp.location = self.url_for(_handler=self.show_post,
                id=str(post.id))

            return resp
        else:
            return self.render2response(request, 'blog/form.html', blog=self,
                url_for=self.url_for)