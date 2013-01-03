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
""" DI tools
"""

import collections

__all__ = ['Dependency', 'List', 'Reference', 'Value', 'inject',
           'create_descriptor']


class Dependency:
    """ Dependency definition

    A dependency definition is used to construct the DI specification providing
    an indirection level.

    You don't need to inherit from this class to create a new definition type.
    The DI framework use duck typing thus as long as you provide a callable
    attribute named `resolve` that accept a single positional argument,
    everything is OK.
    """

    def resolve(self, container: object) -> object:
        """ Resolve the target dependency

        This method is called by the DI framework in order to remove the
        indirection level at target construction. The only positional argument
        it receives is the DI container used as source.
        """
        raise NotImplementedError()


class List(Dependency, list):
    """ Definition that once it's resolved produce a list of dependencies

    It takes as constructor argument a list of dependency definition objects.
    """

    def resolve(self, container):
        _normalize_arg_spec(self)

        for i, value in enumerate(self):
            if hasattr(value, 'resolve'):
                self[i] = value.resolve(container)

        return self


class Reference(Dependency):
    """ Definition resolved as a named reference relative to the DI container.

    This is the most common definition type and every string found in the
    specification it is assumed to be a referenced and converted to an object
    of this type before the target object is built.
    """

    def __init__(self, reference: str):
        self.reference = reference

    def resolve(self, container):
        target = container
        for part in self.reference.split('.'):
            target = getattr(target, part)

        return target

class Value(Dependency):
    """ Definition resolved to a fixed value passed as constructor argument.

    This is a simple way used to pass configuration and fixed value objects.
    """

    def __init__(self, value):
        self.value = value

    def resolve(self, container):
        return self.value

def _normalize_arg_spec(arg_spec):

    for i, value in enumerate(arg_spec):
        if isinstance(value, str):
            arg_spec[i] = Reference(value)

    return arg_spec


def _normalize_attr_spec(spec):
    for key, value in spec.items():
        if isinstance(value, str):
            spec[key] = Reference(value)

    return spec

def inject(target_factory: collections.Callable, container: object, *arg_spec, **attr_spec):
    """ Produce target by injecting its dependencies.
    
    The first positional argument is the factory for constructing the target
    object. The second positional argument is the container used as
    source of dependencies and any other positional arguments are definitions
    for factory arguments.

    Named arguments are used as attribute definitions for the target object.

    :param target_factory: The target factory callable.
    :return: The ready to use target object.
    """
    # TODO: need to implement DI auto-resolution capabilities

    arg_spec = _normalize_arg_spec(list(arg_spec))
    attr_spec = _normalize_attr_spec(attr_spec)

    args = list(map(lambda item: item.resolve(container), arg_spec))
    target = target_factory(*args)

    for key in list(attr_spec):
        setattr(target, key, attr_spec[key].resolve(container))

    return target


def create_descriptor(target_factory: collections.Callable, *arg_spec,
                      **attr_spec):
    """ Create a descriptor that produce target by injecting its dependencies.

    This function produce a descriptor object that create a target object
    the first time the attribute is accessed for every class instance. It use
    the class instance as DI container.
    """

    class Descriptor:

        def __init__(self):
            self.cache = {}

        def __get__(self, instance, owner):
            if instance is None:
                return self
            try:
                return self.cache[instance]
            except KeyError:
                self.cache[instance] = inject(target_factory, instance,
                                              *arg_spec, **attr_spec)
                return self.cache[instance]

    return Descriptor()
