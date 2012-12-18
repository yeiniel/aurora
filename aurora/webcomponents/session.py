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
import hashlib
import hmac
import random
import time

from aurora.webapp import foundation

__all__ = ['SessionProvider']


class SessionProvider:
    """ Provide state to the HTTP protocol.

    This component has two use cases:

     * In a Web application that use the Aurora Web framework infrastructure.
     * In a Web application with a custom infrastructure.

    In the first case you need to provide an implementation for the
    `get_request` optional dependency service and add the `after_handle`
    listener service to the application instance `after_handle` event. Under
    this conditions you can use the `get_session` provided service without
    the Web request object argument. This is known as the higher level
    service.

    In the second case the exposed services are the ones known as the lower
    level services: the `get_session` and `persist_session` services. As
    long as there is no implementation for the optional Web request object
    provisioning service you need to pass explicitly the Web request object
    as argument for the `get_session` service and call the `persist_session`
    service in all you handlers.
    """

    #
    # stubs for component dependencies
    #

    secret = None   # secret string used to create the (id, hash) pair.

    cookie_name = 'aurora-sid'  # name of the cookie used to persist
                                # information on the client browser.

    max_age = 3300  # browser cookie maximum age

    def get_cache(self) -> collections.MutableMapping:
        """ Return the session cache.

        The session cache is a mapping that use as key the session id. By
        default this service return an in-memory session cache and this
        implementation is not suitable in the use case of multiple
        application instances behind a load balancing proxy.
        :return: A mapping.
        """
        try:
            return self.__cache
        except AttributeError:
            self.__cache = {}

            return self.__cache

    def get_request(self) -> foundation.Request:
        """ Web request been handled by the application.

        The Web application can handle one Web request at a time. This service
        return the Web request currently been handled.
        """
        raise NotImplementedError()

    #
    # component implementation
    #

    def __init__(self, secret: str, get_request=None):
        """ Initialize the session provider component.

        If the `get_request` service is provided then the `after_handle`
        service is exposed by the component.
        :param secret: The secret used to create the (id, hash) pair.
        :param get_request: A
            :func:`aurora.webapp.infrastructure.Application.get_request`
            compliant service.
        """
        self.secret = secret

        if get_request:
            self.get_request = get_request

    def generate_id(self) -> str:
        rnd = ''.join((str(time.time()), str(random.random()), self.secret))

        return hashlib.sha1(rnd.encode()).hexdigest()[:8]

    def make_hash(self, id: str) -> str:
        return hmac.new(
            self.secret.encode(), id.encode(), hashlib.sha1).hexdigest()[:8]

    def get_session_info(self, request: foundation.Request) -> (str, str):
        if hasattr(request, '_session_id'):
            id = request._session_id
            hash = request._session_hash
        else:
            cn = self.cookie_name
            if cn in request.cookies and \
                    request.cookies[cn][8:] == self.make_hash(
                        request.cookies[cn][:8]):
                id = request.cookies[self.cookie_name][:8]
                hash = request.cookies[self.cookie_name][8:]
            else:
                id = self.generate_id()
                hash = self.make_hash(id)

            request._session_id = id
            request._session_hash = hash

        return id, hash

    #
    # services provided by the component
    #

    def get_session(self, request=None) -> collections.MutableMapping:
        """ Return the session mapping associated to a Web request object.

        If the Web request object is not given then the one returned by the
        `on_request` optional dependency service will be used as default.
        This method create the session mapping on first access if needed.
        :param request: A Web request object.
        :return: The session mapping.
        """
        if not request:
            request = self.get_request()

        id, hash = self.get_session_info(request)
        return self.get_cache().setdefault(id, {})


    def persist_session(self, request: foundation.Request,
                        response: foundation.Response):
        """ Persist session identification information on the client browser.

        If the session cache mapping is empty then it is destroyed and no
        session information is sent to the browser.
        :param request: A Web request object.
        :param response: A Web response object.
        """
        id, hash = self.get_session_info(request)
        if id in self.get_cache() and len(self.get_cache()[id]) > 0:
            response.set_cookie(self.cookie_name, ''.join((id, hash)),
                    self.max_age, request.script_name)
        elif id in self.get_cache():
            del self.get_cache()[id]


    def after_handle(self, response: foundation.Response):
        """ Service meant to be used as a application `after_handle` listener.

        It is only available if the `get_request` optional dependency service
        is provided because it use that service to make Web request
        provisioning.
        :param response: The Web response object.
        """
        self.persist_session(self.get_request(), response)
