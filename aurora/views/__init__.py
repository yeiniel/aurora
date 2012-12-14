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
import os

__all__ = ['Engine', 'Views']


class Engine(collections.Callable):
    """ Provide syntax specific template based view rendering support.

    A Views engine is any callable object that takes a string containing the
    absolute filesystem path of the View template as first positional
    argument and any named argument used as context and return a string
    containing the rendered content.
    """

    def __call__(self, file_name: str, **context) -> str:
        """ Render a template into content with context.

        :param file_name: The absolute template file name.
        :param context: The context mapping.
        :return: The rendered output string.
        """


class Views:
    """ Provide generic template based view rendering support.

    The template file extension is very important, is used to map template
    file to the engine capable of handling correctly the template syntax.

    Template composition support is provided (the :meth:`render` method is
    mapped into the default context). This allow composing templates with
    different syntax as long as the Template :class:`Engine` of the composed
    view support using a context element as callable.

    The only template engine available by default is one based on `suba`_ and
    created on the fly the first time the template engine cache is hit
    (either because a new template engine is added using :meth:`add_engine`
    or because :meth:`render` is called). A copy of the `suba`_ module is
    shipped with the Aurora library (the `aurora.webcomponents._suba`
    `Python`_ source module.) because it can't be added as a library
    dependency because this library is not on `PYPI`_ `Python`_ package index.

    .. _PYPI: http://pypi.python.org/pypi/
    .. _Python: http://www.python.org/
    .. _suba: https://github.com/jldailey/suba
    """

    DEFAULT_MIME_TYPE = 'text/html'

    @property
    def _engines(self) -> dict:
        try:
            return self.__dict__['_engines']
        except KeyError:
            try:
                import suba as _suba
            except ImportError:
                from . import _suba

            def _suba_engine(file_name, **c):

                root_dir, file_name = os.path.split(file_name)

                gen = _suba.template(filename=file_name, root=root_dir, **c)

                result = ''
                for part in gen:
                    if part is None:
                        break

                    result = ''.join((result, part))

                return result

            _engines = self.__dict__['_engines'] = {
                'suba': _suba_engine
            }

            return _engines

    @property
    def _paths(self) -> list:
        try:
            return self.__dict__['_paths']
        except KeyError:
            _paths = self.__dict__['_paths'] = []
            return _paths

    @property
    def _default_context(self) -> dict:
        try:
            return self.__dict__['_default_context']
        except KeyError:
            default_context = self.__dict__['_default_context'] = {
                'render': self.render
            }
            return default_context

    def add_engine(self, engine: Engine, *extensions):
        """ Register an :class:`Engine`-like object for rendering files.

        :param engine: An :class:`Engine`-like object.
        :param extensions: List of template file extensions.
        """

        for extension in extensions:
            self._engines[extension] = engine

    def add_path(self, path: str):
        """ Add an absolute path as template file source.

        :param path: The absolute path (string) to a folder that store
            templates files.
        """
        self._paths.append(path)

    def add_default(self, key: str, value):
        """ Add a default context item.

        :param key: Item key string.
        :param value: Item value
        """
        self._default_context[key] = value

    @functools.lru_cache(maxsize=100)
    def _resolve_template(self, template_name: str) -> (str, str):
        for path in self._paths:
            for extension in self._engines.keys():
                file_name = os.path.join(
                    path, ''.join((
                        os.path.normpath(template_name), '.', extension))
                )

                if os.path.isfile(file_name):
                    return file_name, extension

    #
    # services provided by the component
    #

    def render(self, template_name: str, **context) -> str:
        """ Render a template into content with context.

        :param template_name: The relative template name string without the
            last extension.
        :param context: The context mapping.
        :return: The rendered output string.
        """
        c = self._default_context.copy()
        c.update(context)

        file_name, extension = self._resolve_template(template_name)

        return self._engines[extension](file_name, **c)