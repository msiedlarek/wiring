Rationale
=========

While writing medium-to-large applications in Python (or any dynamically typed
language for that matter) can be a very bad idea, this just happens, and quite
often Python developer must deal with them. Sometimes the technology was chosen
by the buzzword-driven management and sometimes the application is so old it
doesn't even matter anymore.

Programming environments like Java, designed and used for years in enterprise
settings have already developed tools to tackle architectural problems specific
to big, object-oriented applications. Java language costructs like interfaces
and frameworks like `Spring`_ or `Guice`_, while commonly ridiculed by Python
community, can be in fact very useful in this context.

Wiring was created from the real need of a real application I've been working
on and aims to solve its problems by adapting some of those proven ideas to the
Python environment, while staying away from blindly copying APIs from other
languages and libraries.

.. _Spring: http://spring.io
.. _Guice: https://github.com/google/guice

Dependency Injection
--------------------

`Inversion of Control`_ - commonly realized through dependency injection - is
a popular pattern in object-oriented applications, allowing loose coupling
while promoting object composition. Instead of getting its dependencies from
some predefined location or creating them on the spot, an object can only
declare what it needs and rely on external mechanism to provide it.

For example, this is how an object **without** dependency injection could look
like::

   from myapp.database import database_connection
   from myapp.security import Encryptor

   class UserManager(object):
      def __init__(self):
         self.db = database_connection
         self.encryptor = Encryptor(algo='bcrypt')

   class Application(object):
      def __init__(self):
         self.user_manager = UserManager()

      def run(self):
         pass

   application = Application()
   application.run()

While many applications are built like that, this approach has some major
drawbacks, which are becoming really visible while the application grows:

#. Tight coupling. User management module is strongly connected with database
   and security modules. If you'd like to replace the security module with some
   other implementation, you'd need to also modify the user management module.

#. It uses a global variable `database_connection`. This implies that whatever
   context this class might be used in, the database connection is always the
   same. If in future you'd want to use `UserManager` on some kind of archival
   database, while the rest of your application simultaneously works on the
   default database, you'd be in trouble. Also you need to replace a global
   variable for unit testing.

#. The `UserManager` creates its own `Encryptor` object. This means that if
   you'd need to change password hashing algorithm for one deployment (for
   example due to local government security restrictions), you'd have to modify
   the `UserManager` to use some kind of global setting or provide the
   algorithm as an argument with each use of the class.

Those problems can be easily solved with dependency injection::

   from wiring.dependency import injected
   from wiring.graph import Graph
   from myapp.database import database_connection
   from myapp.security import Encryptor

   class UserManager(object):
      def __init__(self, db=injected('db_connection'),
            encryptor=injected('password_encryptor')):
         self.db = db
         self.encryptor = encryptor

   class Application(object):
      def __init__(self, user_manager=injected('user_manager')):
         self.user_manager = user_manager

      def run(self):
         pass

   graph = Graph()
   # Wiring has much more convenient methods of registering components. This is
   # just for the clarity of the example.
   graph.register_factory('user_manager', UserManager)
   graph.register_factory('application', Application)
   graph.register_instance('db_connection', database_connection)
   graph.register_instance('password_encryptor', Encryptor(algo='bcrypt'))

   application = graph.get('application')
   application.run()

This may look like a silly overheas when presented in one file, but if this was
split in three separate modules we'd have all of our previously mentioned
problems solved:

#. It's now loosely coupled. If you want to replace the security module, you
   just need to reconfigure your :term:`object graph`. `UserManager` doesn't
   even know that `myapp.security` exists.
#. There are no global variables that are used between the modules - if you
   want to replace database connection for unit testing you just need to
   configure your object graph differently.
#. You want to use different password hashing algorithm for one deployment? Not
   a problem - you just configure your object graph differently on that
   deployment. No need to search the code for every single use of `Encryptor`
   class and really no need to modify security or user management modules at
   all.

Those benefits, while not that obvious in a small example, become pretty
obvious in big applications - most importantly those with multiple, differing
deployments.

There's a little amount of solid tools to tackle big Python applications
architecture problem:

* `zope.component`_, while having some truly brilliant ideas, does not provide
  dependency injection and above all is **a complete utter mess**. Its code is
  a mess and its documentation is a mess. If you don't believe me, just go and
  look at it.
* `pinject`_ is not very flexible and relies on class and argument names to do
  the injection, which is very limiting. Also its latest commit while I'm
  writing this is over a year old, while there are several issues open.
* `injector`_ while quite good, also lacks flexibility and leaves out many
  possibilities.

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

Powers Combined
---------------

There is an important reason those two tools - dependency injection and
interfaces - are coupled together into this package. Let's bring back
a fragment of the dependency injection example::

   class UserManager(object):
      def __init__(self, db=injected('db_connection')):
         self.db = db

If a programmer is asked to change some behavior of `UserManager` and encouters
this code, he has no way of knowing what exactly can it do with `db` variable.
What are its methods and attributes?  He has to trace component configuration
looking for specific implementation that is registered under ``db_connection``.
Fortunately, there's a better way::

   class IDatabaseConnection(object):

      version = """Version of the used database engine."""

      def sql(query):
         """Runs a given `query` and returns its result as a list of tuples."""

   class UserManager(object):
      def __init__(self, db=injected(IDatabaseConnection)):
         self.db = db

Interfaces make perfect :term:`specifications <specification>` for dependency
injection. Now anyone visiting `UserManager`'s code can easily trace what
properties `db` variable will always have. Also, when replacing the database
component its also obvious what properties new component should have to fit in
place of the old one. It just have to conform to the `IDatabaseConnection`
interface.
