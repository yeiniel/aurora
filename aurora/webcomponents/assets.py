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

from email import utils as email_utils
import functools
import mimetypes
import os
from urllib import parse as urllib_parse

from aurora.webapp import foundation, mapping

__all__ = ['Assets']


class Assets:
    """ Support for Web application static assets.

    Web application static assets are those files that are a functional part
    of the application (media, style, client side logic, etc). This component
    provide support for handling static assets across the entire Web
    application life cycle.

    During development you can use the Web request handling capabilities of
    this component to serve static assets files. Once the application move to
    production this component provide static assets uri assembly.

    In order to setup correctly this component you need to perform the
    following steps:

     - register the paths of folders containing the assets files using the
       :meth:`add_path` service.
    """

    base_path = ''

    @property
    def _paths(self) -> list:
        try:
            return self.__dict__['_paths']
        except KeyError:
            _paths = self.__dict__['_paths'] = []
            return _paths

    def add_path(self, path: str):
        """ Add an absolute path as template file source.

        :param path: The absolute path to a folder that store templates files.
        :return: None
        """
        self._paths.append(path)

    @functools.lru_cache(maxsize=100)
    def _resolve_filename(self, path_info: str) -> str:
        """ Transform a URL path information into a filesystem path.

        This function has been intentionally left public to allow caching
        static assets information for later automated tasks.
        """
        for path in reversed(self._paths):
            file_name = ''.join((path, os.path.normpath(path_info)))

            if os.path.isfile(file_name):
                return file_name

    #
    # services provided by the component
    #

    @property
    def rule_factory(self) -> mapping.Rule:
        """ Return an object used to route and assemble URIs for static assets.
        """

        class Rule:

            def __init__(self, assets):
                self.assets = assets

            complexity = 1000

            def match(self, uri: str):

                if self.assets._resolve_filename(uri) is None:
                    return False
                else:
                    return {'filename': uri}

            def assemble(self, **options):
                if 'filename' not in options:
                    return False
                else:
                    return urllib_parse.urljoin(
                        self.assets.base_path, options['filename']
                    )
        
        mapping.Rule.register(Rule)

        return functools.partial(Rule, self)

    def handler(self, request: foundation.Request) -> foundation.Response:
        """ Handle Web requests by serving static assets.
        """

        # resolve absolute file path name
        file_name = self._resolve_filename(request.GET['filename'])

        response = request.response_factory()

        # resolve file content type
        response.content_type, _ = mimetypes.guess_type(file_name)
        if not response.content_type:
            response.content_type = 'application/octet-stream'

        file = open(file_name, 'rb')
        fs = os.fstat(file.fileno())
        response.content_length = str(fs[6])
        response.last_modified = email_utils.formatdate(
            fs.st_mtime, usegmt=True
        )
        response.body_file = file

        return response


if not mimetypes.inited:
    mimetypes.init()
