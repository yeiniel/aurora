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