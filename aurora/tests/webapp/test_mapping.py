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

import unittest
from aurora.webapp import mapping, testing

__all__ = ['TestRoute', 'TestMapper']


class TestRoute(testing.TestRule):
    """ Tests for Web request path mapping route.
    """

    def rule_factory(self):
        return mapping.Route('/(?P<id>\d+)/(?P<name>\w+)', name='name')

    def test_match_success(self):
        """ Test rule `match` method call success.

        This test validate the case where Web request path match the route
        pattern (the structure and group value types).
        """
        self.assertDictEqual(
            self.rule.match('/1/name'), {'id': '1', 'name': 'name'}
        )

    def test_match_invalid_type(self):
        """ Test the rule `match` method with a path having group values with
        invalid types.
        """
        self.assertFalse(self.rule.match('/a/111'))
        self.assertFalse(self.rule.match('/1/1 11'))
        self.assertFalse(self.rule.match('/1/a aaa'))

    def test_assemble_missing_argument(self):
        """ Test route `assemble` method call with missing arguments.
        """
        self.assertFalse(self.rule.assemble(name='name'), __doc__)

    def test_assemble_with_default_arguments(self):
        """ Test rule `assemble` method call with missing default arguments.
        """
        self.assertEqual(self.rule.assemble(id='1'), '/1/name', __doc__)

    def test_assemble_append_extra_characteristics_as_query(self):
        """ Test that extra characteristics are appended as query on `assemble`
        """
        self.assertEqual(
            self.rule.assemble(name='r2', id=2, extra='extra_value'),
            '/2/r2?extra=extra_value'
        )


class TestMapper(testing.TestRule):
    """ Tests for Web request path mapping mapper.
    """

    def rule_factory(self):
        mapper = mapping.Mapper()

        # add rules
        mapper.add_rule(mapping.Route('/'), _name='default')
        mapper.add_rule(mapping.Route('/(?P<id>\w+)'), _name='r1')
        mapper.add_rule(mapping.Route('/(?P<id>\d+)'), _name='r2')

        return mapper

    def test_match_no_rule(self):
        """ Test mapper `match` call when no there is no rule.
        """
        self.assertFalse(self.rule.match('/no/rule/for/me'))

    def test_match_with_rule(self):
        """ Test  mapper `match` call when there is a rule.
        """
        self.assertDictEqual(self.rule.match('/1'), {'id': '1', '_name': 'r2'})

    def test_match_with_generic_rule(self):
        """ Test mapper `match` call when there is more than one rule.

        In this case the last been added should be the one been activated.
        """
        self.assertDictEqual(self.rule.match('/a'), {'id': 'a', '_name': 'r1'})

    def test_assemble_strip_metadata(self):
        """ Test metadata is stripped from characteristics on `assemble` call.
        """
        self.assertEqual(self.rule.assemble(_name='default'), '/')
        self.assertEqual(self.rule.assemble(_name='r2', id='1'), '/1')

if __name__ == '__main__':
    unittest.main()
