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
import unittest
from aurora.webapp import foundation, mapping

__all__ = ['TestHandler', 'TestRule']


class TestHandler(unittest.TestCase):
    """ Tests for Web request handlers.

    This test case provide common tests to all Web request handlers. Is is not
    a framework test case but a base class for
    :class:`Web request handler<.foundation.Handler>` tests.

    You need to override the :attr:`handler_factory` class attribute used to
    set the Web request handler factory used at test suite setup.
    """

    handler_factory = foundation.Handler
    request_factory = foundation.Request

    def setUp(self):
        self.handler = self.handler_factory()

    def test_response_type(self):
        """ Response object type test.

        The :class:`Web response <.foundation.Response>` object returned by
        the call to the Web request handler should be an instance of the same
        type of the objects returned by calls to the
        :class:`Web request <.foundation.Request>`
        :attr:`~.foundation.Request.response_factory` attribute.
        """
        request = self.request_factory({})
        response = self.handler(request)

        self.assertEqual(
            type(response), type(request.response_factory()), __doc__
        )


class TestRule(unittest.TestCase):
    """ Tests for Web request path mapping rules.

    This test case provide common tests to all Web request path mapping rules.
    Is is not a framework test case but a base class for
    :class:`Web request path mapping rule<.mapping.Rule>` tests.

    You need to override the :attr:`rule_factory` class attribute
    used to set the Web request path mapping rule factory used at test suite
    setup.

    The set of test is permissive, they test if the
    :class:`Web request path mapping rule<.mapping.Rule>` object
    implement the
    :class:`Web request path mapping rule<.mapping.Rule>` protocol
    but don't fail if the
    :class:`Web request path mapping rule<.mapping.Rule>` object
    provide additional features (an augmented argument list for example).
    """

    rule_factory = mapping.Rule

    def setUp(self):
        self.rule = self.rule_factory()

    def test_match_accept_one_positional_argument(self):
        """ Test if the rule `match` method accept one positional argument.

        This test call the `match` method of the rule and assert if the
        result is `False` or a `Mapping`.
        """
        result = self.rule.match('/')
        self.assertTrue(
            result is False or isinstance(result, collections.Mapping),
            __doc__
        )

    def test_assemble_without_arguments(self):
        """ Test if the rule `assemble` method can be called without arguments.

        This test call the `assemble` method of the rule and assert if the
        result is `False` or a string.
        """
        result = self.rule.assemble()
        self.assertTrue(result is False or isinstance(result, str), __doc__)

    def test_assemble_accept_arbitrary_named_arguments(self):
        """ Test if the rule assemble method accept arbitrary named arguments.

        This test call the `assemble` method of the rule and assert if the
        result is `False` or a string.
        """
        data = {}
        data.update(map(
            lambda item: (item, item),
            map(lambda item: chr(item), range(1000))
        ))
        result = self.rule.assemble(**data)
        self.assertTrue(result is False or isinstance(result, str), __doc__)