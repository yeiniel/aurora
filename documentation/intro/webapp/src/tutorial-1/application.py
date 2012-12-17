#! /usr/bin/env python3
from aurora import webapp
from aurora.webapp import foundation, mapping

__all__ = ['Application']


class Application(webapp.Application):
    """ Web Blogging application
    """

    def __init__(self):
        self.mapper.add_rule(mapping.Route('/'), _handler=self.list_posts)
        self.mapper.add_rule(mapping.Route('/post/(?P<id>\d+)'),
            _handler=self.show_post)
        self.mapper.add_rule(mapping.Route('/compose'),
            _handler=self.add_post)

    def list_posts(self, request: foundation.Request) -> foundation.Response:
        """ List summaries for posts added more recently. """
        return request.response_factory(text="""
        <html>
            <body>
                <h1>List of posts</h1>
                <div>
                    <h2><a href="/post/1">Post title</a></h2>
                    <p>
                        Post summary (or the initial segment of post
                        content).
                    </p>
                </div>
                <div>
                    <h2><a href="/post/1">Post title</a></h2>
                    <p>
                        Post summary (or the initial segment of post
                        content).
                    </p>
                </div>
                <div>
                    <h2><a href="/post/1">Post title</a></h2>
                    <p>
                        Post summary (or the initial segment of post
                        content).
                    </p>
                </div>
            </body>
        </html>
        """)

    def show_post(self, request: foundation.Request) -> foundation.Response:
        """ Show a post. """
        return request.response_factory(text="""
        <html>
            <body>
                <h1><a href="/post/1">Post title</a></h1>
                <p>
                    Post content (full).
                </p>
            </body>
        </html>
        """)

    def add_post(self, request: foundation.Request) -> foundation.Response:
        """ Add a new Blog post. """
        return request.response_factory(text="""
        <html>
            <body>
                <h1>Add new post</h1>
                <form action="/add" method="post">
                    <fieldset>
                        <legend>Add Post</legend>
                        <div class="clarfix">
                            <label for="title">Title</label>
                            <div class="input">
                                <input type="text" id="title" name="title"></input>
                            </div>
                        </div>
                        <div class="clarfix">
                            <label for="content">Content</label>
                            <div class="input">
                                <textarea id="content" name="content" class="xlarge" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="actions">
                            <input class="btn primary" type="submit" name="submit" value="Add" />
                        </div>
                    </fieldset>
                </form>
            </body>
        </html>
        """)

if __name__ == '__main__':
    from wsgiref import simple_server
    from aurora.webapp import foundation

    wsgi_app = foundation.wsgi(Application())
    httpd = simple_server.make_server('', 8008, wsgi_app)

    print("Serving on port 8008...")
    httpd.serve_forever()