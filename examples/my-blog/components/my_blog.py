
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