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

import collections
import functools
import webob

__all__ = ['Request', 'Response', 'Handler', 'wsgi']


class Response(webob.Response):
    """ Web response.

    The Web response is created by the Web request handler and is used to
    store the information that is going to be sent to the client browser in
    return.
    """


class Request(webob.Request):
    """ Web request.

    The Web request provide access to the information sent by the
    client browser to the Web application.
    """

    @property
    def response_factory(self) -> Response:
        """ Factory used to produce a :class:`Web response <Response>` object.
        """
        return Response


class Handler(collections.Callable):
    """ Web request handler.

    .. admonition::

        This class is not meant to be inherited it is here just for interface
        documentation purposes.

    A Web request handler is any callable object that accept as first
    positional argument a :class:`Web request <Request>` object and return a
    :class:`Web response <Response>` object.

    The Web request handler must create the :class:`Web response <Response>`
    object by calling the factory referenced by the
    :attr:`~Request.response_factory` attribute of the
    :class:`Web request <Request>` object. This way the Web handler can be
    called using different request-response pairs (for testing purposes for
    example).

    Example `Hello World!` Web request handler::

        def say_hello(request):
            return request.response_factory(text='Hello World!')
    """


def wsgi(handler):
    """ Wrap `handler` with a WSGI application interface.

    :param handler: A :class:`Web request handler <Handler>`.
    :return: A `WSGI <http://www.python.org/dev/peps/pep-333>`_ application.
    """

    @functools.wraps(handler)
    def wsgi_app(env, start_response):
        return handler(Request(env))(env, start_response)

    return wsgi_app
