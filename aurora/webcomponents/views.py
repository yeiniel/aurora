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

import html
import mimetypes

from aurora import views
from aurora.webapp import foundation

__all__ = ['Views']


class Views(views.Views):
    """ Provide generic template based view rendering support.

    This component is based on the :class:`aurora.views.Views` class from
    the ``Views`` framework. It provide the same services plus a new one
    (the :meth:`render2response` service) specific for usage in the context
    of Web applications.

    The component add a ``escape`` default content item designed to escape all
    content that represent a XSS attack vulnerability.
    """

    def __init__(self):
        self.add_default('escape', html.escape)

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
        response = request.response_factory(
            text=self.render(template_name, request=request, **context))

        response.content_type, _ = mimetypes.guess_type(template_name)
        if not response.content_type:
            response.content_type = self.DEFAULT_MIME_TYPE

        return response

    def handler4template(self, template_name: str, **context) -> foundation.Handler:
        """ Produce a Web request handler that simply render a template.

        This service use the :meth:`render2response` service and the same
        rules about template names are applied.
`

        :param template_name: The relative template name string without the
            last extension.
        :param context: The context mapping.
        :return: A Web request
            :class:`handler <aurora.webapp.foundation.Handler>`.
        """

        def handler(request):
            return self.render2response(request, template_name, **context)

        return handler

if not mimetypes.inited:
    mimetypes.init()
