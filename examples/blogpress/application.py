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

import os

from aurora import di, event, webapp
from aurora.webcomponents import assets, layout, views

from components import blog, engine_provider

__all__ = ['Application']


class Application(webapp.Application):
    """ Blogpress blogging application.
    """

    def __init__(self):
        super().__init__()

        self.mapper.add_rule(self.assets.rule_factory())

        self.blog.setup_mapping(self.mapper.add_rule)
        self.blog.setup_views(self.views.add_path)

        self.views.add_path(os.path.join(os.path.dirname(__file__),
            'templates'))
        self.views.add_default('url_for', self.url_for)
        self.views.add_default('assets', self.assets.handler)
        self.views.add_default('self', self)

        self.assets.add_path(os.path.join(os.path.dirname(__file__),
            'static'))

    assets = di.create_descriptor(assets.Assets)

    blog = di.create_descriptor(blog.Blog, 'db.get_engine',
        'views.render2response', 'url_for')

    db = di.create_descriptor(engine_provider.EngineProvider)

    layout = di.create_descriptor(layout.Layout, 'views.render')

    post_dispatch = di.create_descriptor(event.Event,
        di.list(['layout.post_dispatch']))

    views = di.create_descriptor(views.Views)

if __name__ == '__main__':
    from wsgiref import simple_server
    from aurora.webapp import foundation

    wsgi_app = foundation.wsgi(Application())
    httpd = simple_server.make_server('', 8008, wsgi_app)

    print("Serving on port 8008...")
    httpd.serve_forever()
