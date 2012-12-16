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

import abc
import collections
import re

__all__ = ['Rule', 'Route', 'DefaultRule', 'Mapper']


class Rule(metaclass=abc.ABCMeta):
    """ Map a Web request path and its characteristics back and forth.

    A rule implement the logic needed to perform the mapping between a
    specific Web request path and its associated characteristics. This
    mapping can be addressed direct or reverse.

    This class is not meant to be inherited it is here just for interface
    documentation purposes.
    """

    @abc.abstractmethod
    def match(self, path: str) -> collections.Mapping or False:
        """ Map the Web request path into its associated characteristics.

        If the :class:`Web request <.foundation.Request>` path  can be mapped
        by this rule then a mapping of the characteristics that make this
        :class:`Web request <.foundation.Request>` path unique respect to the
        Rule is returned otherwise return `False`.

        :param path: The Web request path.
        :return: The characteristic mapping or `False`
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def assemble(self, **characteristics) -> str or False:
        """ Map characteristics into its associated Web request path.

        If the characteristics mapping can be mapped by this rule then a
        string containing the :class:`Web request <.foundation.Request>` path
        unique respect to the Rule is returned otherwise return `False`.

        :param characteristics: The characteristics mapping.
        :return: The Web request path or `False`.
        """
        raise NotImplementedError()


class Route:
    """ A Web request path mapping :class:`Rule` that use pattern matching.

    The pattern matching algorithm used is plain regex. The expressions
    allowed in the pattern in order to be reassembled into a valid
    :class:`Web request <.foundation.Request>` path are described by the
    :attr:`dialect` attribute of this class. Any deviation may result in an
    incorrectly assembled :class:`Web request <.foundation.Request>` path.

    At initialization the pattern is passed as first positional argument,
    other named arguments are used as default values for any optional
    pattern group.
    """

    dialect = re.compile(r"\(\?P<(\w+)>\\(\w+)\+\)")

    def __init__(self, pattern: str, **defaults):
        # search for the initial fixed part of the pattern
        self._prefix = self.dialect.split(pattern, 1)[0]
        pattern = pattern.replace(self._prefix, '', 1)

        self._re = re.compile(''.join(('^', pattern, '$')))
        self._defaults = defaults
        self._pattern = self._re.pattern.strip('^$*')

    def match(self, path):
        # as a performance improvement match first the fixed path segment
        if not path.startswith(self._prefix):
            return False

        path = path.replace(self._prefix, '', 1)

        result = self._re.match(path)
        if result:
            options = dict(self._defaults)
            for key, value in result.groupdict().items():
                if value != '':
                    options[key] = value
            return options
        else:
            return False

    def assemble(self, **characteristics):
        _characteristics = dict(self._defaults)
        _characteristics.update(characteristics)

        path = [self._prefix]
        last_pos = 0
        for match in self.dialect.finditer(self._pattern):
            if match.group(1) not in _characteristics:
                return False
            path.append(self._pattern[last_pos:match.start()])
            path.append(str(_characteristics[match.group(1)]))
            del _characteristics[match.group(1)]
            last_pos = match.end()

        path.append(self._pattern[last_pos:])
        path = ''.join(path)

        if len(_characteristics) > 0:
            path = '?'.join((path, self._render_query(**_characteristics)))

        return path

    def _render_query(self, **options):
        result = '&'.join(map(
            lambda item: '='.join((item, options[item])),
            options))

        return result


Rule.register(Route)


class DefaultRule:
    """ A Web request path mapping :class:`Rule` that map all Web requests.

    This is a simple Web request path mapping :class:`Rule` very useful for
    mapping the Web request handler for not mapped Web requests. It match all
    Web request paths and return always `False` on :meth:`assemble` method
    calls.
    """

    def match(self, path):
        return {}

    def assemble(self, **characteristics):
        return False


Rule.register(DefaultRule)


class Mapper:
    """ Map a Web request path and its characteristics using multiple rules.

    The Mapper implement the same interface provided by :class:`Rule` and add
    the possibility of tagging rules using an additional mapping of elements
    known as metadata. Additionally metadata can be used to override
    :class:`Web request <.foundation.Request>` path characteristics with
    default values.

    Every time the :meth:`match` or :meth:`assemble` methods are called all
    added rules are evaluated in the reverse order of addition. This
    implementation detail imply that in order to function correctly generic
    rules must be added first and specific ones latter.
    """

    def __init__(self):
        self._rules = []

    def add_rule(self, rule: Rule, **metadata):
        """ Add a :class:`Rule` and its associated metadata to the mapping.

        :param rule: A mapping :class:`Rule`.
        :param metadata: The :class:`Rule` associated metadata.
        """
        self._rules.insert(0, (rule, metadata))

    def match(self, path: str) -> collections.Mapping or False:
        """ Map the Web request path into its associated characteristics.

        Once a :class:`Rule` is mapped successfully its associated metadata
        is used to update the :class:`Web request <.foundation.Request>` path
        characteristics mapping.

        :param path: The Web request path.
        :return: The characteristic mapping or `False`
        """
        for rule, metadata in self._rules:
            result = rule.match(path)

            if result is False:
                continue

            result.update(metadata)
            return result

        return False

    def assemble(self, **characteristics) -> str or False:
        """ Map characteristics into its associated Web request path.

        A :class:`Rule` is mapped only in the case that all :class:`Rule`
        associated metadata are present in the characteristics mapping and
        have the same value.

        :param characteristics: The characteristics mapping.
        :return: The Web request path or `False`.
        """
        for rule, metadata in self._rules:
            options = characteristics.copy()
            for key, value in metadata.items():
                if key not in options or options[key] != value:
                    break

                del options[key]
            else:
                result = rule.assemble(**options)
                if result is not False:
                    return result

        return False
