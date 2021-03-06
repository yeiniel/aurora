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

import functools

__all__ = ['partial' , 'Layout']


def partial(handler):
    """ Mark the handler as a view partial (set response Content-Type).
    """

    @functools.wraps(handler)
    def _handler(*args, **kwargs):
        response = handler(*args, **kwargs)
        response.content_type = 'x-application/partial'
        return response

    return _handler

class Layout:
    """ The layout component

    The layout component provide a two step view rendering pattern
    implementation on top of the services provided by a `views` component or a
    compatible one. Using this component the task of setting a default look
    and feel for the entire application is eased by allowing all content
    generated by the application to share a default HTML page template.
    """

    content_type = 'text/html'

    template_name = 'layout.html'

    status_codes = [
        200,
    ]

    def __init__(self, render):
        """ Setup the component.

        It takes as only argument the :func:`aurora.webcomponents.views.render`
        service implementation used by the :func:`after_handle` service.
        :param render: The render service
        """
        self.render = render

    #
    # stubs for component dependencies
    #

    def render(self, template_name: str, **context) -> str:
        """ Render a template into a `webob.Response` object with context.

        :param template_name: The relative template name without the last
        extension.
        :param context: The context mapping.
        :return: The rendered content.
        """
        raise NotImplementedError()

    #
    # services provided by the component
    #

    def post_dispatch(self, response):
        """ Wrap the response body using a layout template.

        This service is intended to be registered as a
        :func:`aurora.webapp.infrastructure.Application.after_handle` event
        listener and this behaviour is only activated if the response content
        type is the `x-application/partial` string.
        :param response: The Web response object.
        """
        if 'x-application/partial' in response.content_type and \
                response.status_int in self.status_codes:
            response.text = self.render(self.template_name,
                                        content=response.text)

            response.content_type = self.content_type
