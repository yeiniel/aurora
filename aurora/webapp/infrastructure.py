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

from urllib import parse as urllib_parse
from .import foundation, mapping

__all__ = ['Application']


class Application:
    """ Web application.

    This class provide the basic infrastructure needed to build a Web
    application based on multiple handlers and with a extensible
    :class:`Web request <.foundation.Request>` handling mechanism.

    Web application objects implement the
    :class:`Web request handler <.foundation.Handler>` protocol. The
    :class:`Web request <.foundation.Request>` handling strategy has been
    built on top of the Web request path mapping components. The
    characteristic used as :class:`Web request <.foundation.Request>` handler
    is ``_handler``. All characteristics except ``_handler`` update the
    :class:`Web request <.foundation.Request>` ``GET`` mapping.

    The :class:`Web request <.foundation.Request>` handling strategy can be
    extended by implementing the :meth:`pre_dispatch` and :meth:`post_dispatch`
    services. In order to provide plug-able extension points this services
    can be replaced with event dispatchers.
    """

    @property
    def mapper(self) -> mapping.Mapper:
        """ Web request :class:`path mapper <.mapping.Mapper>`.
        """
        try:
            return self.__mapper
        except AttributeError:
            self.__mapper = mapping.Mapper()
            #noinspection PyTypeChecker
            self.__mapper.add_rule(mapping.DefaultRule(),
                _handler=self.not_found)
            return self.__mapper

    def not_found(self, request: foundation.Request) -> foundation.Response:
        """ Service invoked for not mapped Web requests.

        This service is the first :class:`~mapping.Rule` registered with the
        application's Web request path :attr:`.mapper` using the
        :class:`~mapping.DefaultRule` :class:`~mapping.Rule`. It shows a
        basic not found message on the client browser.
        """
        #noinspection PyArgumentList
        return request.response_factory(text="""
        <html>
            <body>
                <h1>Not Found</h1>
                <p>
                    The requested path is not found on this server.
                </p>
            </body>
        </html>
        """, status="404 Not Found")

    def get_request(self) -> foundation.Request:
        """ The Web request been handled by the application.

        The Web application can handle one
        :class:`Web request <.foundation.Request>` at a time. This service
        return the :class:`Web request <.foundation.Request>` currently been
        handled. It is intended to be used by components that provide a
        request centered service (like HTTP session support).
        """
        return self.__request

    def url_for(self, **characteristics) -> str:
        """ Create a fully usable url.

        This method fill the void left by the lack of integration between
        the :class:`Web request <.foundation.Request>` path mapping components
        and the Web application framework foundation. The url is produced by
        concatenating the :class:`Web request <.foundation.Request>`
        application url and the relative url produced by the associated rule
        :meth:`~.mapping.Rule.assemble` method call. If the last element is a
        absolute url then no concatenation is done.

        :param characteristics: The Web request path characteristics.
        :return: A fully usable url.
        """
        return urllib_parse.urljoin(
            self.get_request().application_url,
            self.mapper.assemble(**characteristics)
        )

    def pre_dispatch(self, request: foundation.Request):
        """ Web request handling strategy extension.

        This service is invoked by the Web request handling strategy after
        the :class:`Web request <.foundation.Request>` path is mapped into its
        characteristics and before the
        :class:`Web request handler <.foundation.Handler>` is invoked.
        :param request: The :class:`Web request <.foundation.Request>`.
        """

    def post_dispatch(self, response: foundation.Response):
        """ Web request handling strategy extension.

        This service is invoked by the Web request handling strategy after
        the :class:`Web request handler <.foundation.Handler>` is invoked.
        :param response: The :class:`Web response <.foundation.Response>`.
        """

    def __call__(self, request: foundation.Request) -> foundation.Response:
        # register request for latter retrieval
        self.__request = request

        characteristics = self.mapper.match(request.path_info)
        handler = characteristics['_handler']
        del characteristics['_handler']
        request.GET.update(characteristics)

        self.pre_dispatch(request)
        response = handler(request)
        self.post_dispatch(response)

        return response