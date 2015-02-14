Interfaces Guide
================

.. note::

   To understand what interfaces are and why are they useful, head to the
   :doc:`rationale`.

When building a large, modular Python application it's easy to lost track of
what exactly this function argument can be or which properties of that class
are used where. For big application that does not fit entirely into a single
programmer's mind, lack of static typing can be a problem.

Dependency injection, with all it merits, also makes this problem worse. When
you're only marking some argument as a ``'db_connection'`` you're not really
helping other programmers reason about it's properties. What attributes does
this object have, what methods?

And what if you want to switch to a new database engine, and need to write
a new ``'db_connection'``? How do you know what properties should it have? Even
if you'll find the original implementation, it may not be obvious which
methods, and particularly, which attributes are part of its API.

That's why Wiring provides a hint of static typing for Python - interface
system - as a natural counterweight for its dependency injection feature.

Defining Interfaces
-------------------

:term:`Interfaces <interface>` are objects that describe what attributes and
methods some other object has. Let's jump right in with an example interface:

.. code-block:: python

   from wiring import Interface

   class IUser(Interface):

      email = """User's contact e-mail."""

      def change_password(old_password, new_password):
	 """
	 Changes user's password to `new_password`, providing that
	 `old_password` is he's valid, current password.
	 """

Interfaces are defined by declaring classes inheriting from
:py:class:`Interface <wiring.interface.Interface>` class.  Their names should
start with a capital ``I`` to easily distinguish between them and their
implementations.

This interface declares two requirements that an object must meet to be
considered its implementation:

#. It needs to have an `email` property.
#. It needs to have a `change_password` method with two arguments named exactly
   `old_password` and `new_password`.

Both argument and method declaration can be easily documented with docstrings.

Implementing Interfaces
-----------------------

Implementing class of objects conforming to the interface is rather
straightforward:

.. code-block:: python

   from wiring import Interface, implements

   class IUser(Interface):

      email = """User's contact e-mail."""

      def change_password(old_password, new_password):
	 """
	 Changes user's password to `new_password`, providing that
	 `old_password` is he's valid, current password.
	 """

   @implements(IUser)
   class User(object):

      def __init__(self):
	 self.email = None

      def change_password(self, old_password, new_password):
	 # ...

There are three important things to notice here:

#. To implement interface you just need to create an object conforming to it.
   There is an :py:func:`@implements <wiring.interface.implements>` decorator,
   but it is purely optional. An object doesn't have to be an instance of
   a class annotated with this decorator to be considered an implementation of
   the interface. Using the decorator is considered a good practice, as it aids
   other programmers in reasoning about the class and can actually serve as its
   documentation.
#. Interface describes **properties of an object, not of a class**. Notice that
   `email` attribute belongs to a `User` instance, not the class.
#. Interface describes API of an object, not its implementation. Notice that
   there is no `self` argument in interface definition of `change_password`
   method. That's because a user of the API doesn't have to actually provide
   it.

Validating Interfaces
---------------------

Unlike in statically-typed languages, interface implementations are not
implicitly validated. That's because just by looking at a class in Python we
cannot determine what properties will its instance have. That's why it is
recommended to construct an object of the class and run it trough interface
validation as part of your unit tests.

.. code-block:: python

   user = User()
   IUser.check_compliance(user)

The :py:meth:`Interface.check_compliance()
<wiring.interface.Interface.check_compliance>` method will raise
:py:exc:`InterfaceComplianceError <wiring.interface.InterfaceComplianceError>`
if it detects any errors in the implementation.

Using Interfaces with Dependency Injection
------------------------------------------

Interfaces make perfect compations to the dependency injection pattern. They
serve as fantastic :term:`specifications <specification>`. To lear why, please
read the :ref:`Powers Combined section of Rationale
<rationale-powerscombined>`.
