Rationale
=========

While I would discourage writing medium-to-big applications in Python (or any
dynamically typed language for that matter), this just happens for whatever
reason and you need to be prepared for when you encounter such application.

* If your object-oriented application exceeds 200k significant lines of Python
  code and you feel that you may be in trouble...
* If your simple Django app has turned into a horrific monstrocity maintained
  by many people and deployed in many configurations...
* If you're planning on doing something *big* in Python...

...this may be the library for you.

Dependency Injection
--------------------

Most big, object-oriented applications could probably benefit from `Inversion
of Control`_ pattern. For applications that need to have interchangable
components - there's no *probably*. Dependency injection has some major
benefits:

* Loose coupling. Each component can be tested separately from others and
  changed for another without any modification in dependent components.
* Interchangeability. It's easy to change some aspect of a single
  deployment without affecting others, as which component will be used is
  a matter of configuration.

Those are achieved by mentioned Inversion of Control - component no longer just
*gets* what it needs - it *declares what it needs* and separate logic must
provide it basing on some configuration.

There's a little amount of solid tools to tackle big Python applications
infrastructure problem:

* `zope.component`_, while having some truly brilliant ideas, does not provide
  dependency injection and above all is **a complete utter mess**. Its code is
  a mess and its documentation is a mess. If you don't believe me, just go and
  look at it.
* `pinject`_ is not very flexible and relies on class and argument names to do
  the injection, which is very limiting. Also its latest commit while I'm
  writing this is over a year old, while there are several issues open.
* `injector`_ while quite good is just not flexible enough for my tastes.

.. _Inversion of Control: http://www.martinfowler.com/articles/injection.html
.. _zope.component: https://pypi.python.org/pypi/zope.component
.. _pinject: https://pypi.python.org/pypi/pinject
.. _injector: https://pypi.python.org/pypi/injector

Interfaces
----------

Many would argue that interfaces are useful only in languages like Java, where
typing is static and multiple inheritance seriously limited. Those people view
interfaces only as a tool to enable polymorphism, failing to recognise other
use - definition and validation of objects.

Python uses idea of duck typing, as the saying goes - *if it looks like a duck,
swims like a duck, and quacks like a duck, then it probably is a duck*.  The
problem with this approach is when you want to replace some component - said
duck - you must know exactly how to create your own duck, that is *what it
means to be a duck*.

Most popular approach to this is documenting required methods and attributes of
a duck in project's documentation. While basically valid, this has two
problems:

* It moves away the duck description from the code to the external
  documentation. This may easily create a divergence between the documentation
  and the code and requires programmer to know where to look for the duck
  description.
* You have no way of automatically testing whether the duck you created is
  a valid duck. What if a duck definition changes in a future? You must
  remember to update your implementation.

Interfaces as implemented in :py:mod:`wiring.interface` solve exactly those two
problems:

* They are defined in code, and implementing classes can declare them in code.
  They're also presented in a simplest possible form for the programmer to
  read -- in the form of Python code.
* Any object can be tested against them and proved to have valid attributes and
  methods. This can be checked for example in unit tests.

As to why create new interface implementation, when there is `zope.interface`_
available... I encourage you to look at just one file of Zope's implementation.
Any file. Just one.

.. _zope.interface: https://pypi.python.org/pypi/zope.interface
