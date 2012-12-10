Why I need to develop a new Python Web framework
================================================

I begin developing Web applications on 2004 for the library at `UCLV`_
university, back at that time I use `PHP`_ as programming
language. But 5 years latter it became clear for me that the same design
decisions that make `PHP`_ a easy to use programming language for Web
development purposes where the same that degrade exponentially the
performance of my products as they became more complex.

On 2009 I met `Python`_ and :pep:`333` for the first time and the first
impression was: "Oh wow! This is what I was looking for!". The simple
concept of application presented at :pep:`333`  and
the realization of its capabilities make me switch to `Python`_ as
programming language for my future Web experiments.

After toying with most of the open source `Python`_ based Web frameworks I
realize of some issues that arise on them:

 * The use of thread local (global in the worst cases) objects for sharing
   resources/services. This issue make the testing of components complicated.

 * The use of the Web request object as a registry for sharing
   resources/services. This create a dependency problem and corrupt the
   meaning of Web request.

 * The use of the `WSGI <http://www.python.org/dev/peps/pep-333>`_ protocol
   for connecting required application components as middleware.

 * The use of the `WSGI <http://www.python.org/dev/peps/pep-333>`_ protocol
   for writing actual Web request handlers. This force the developer to
   handle the complexities of this low level protocol.

The first two issues share a common consequence: component requirements gets
replaced by the framework (because you need the framework to provide the
component requirements trough the use of a global object or the request
object) and the real component requirement expression is at the component
implementation and not at the component interface. This break the rule that
explicit is better than implicit.

This are the conditions that motivate me to develop a new `Python`_ based Web
framework with :pep:`8` as design philosophy.


.. _PHP: http://www.php.net/
.. _Python: http://www.python.org/
.. _UCLV: http://www.uclv.edu.cu/