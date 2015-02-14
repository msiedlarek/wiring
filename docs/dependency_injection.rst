Dependency Injection Guide
==========================

.. note::

   To understand what dependency injection is and why is it useful, head to the
   :doc:`rationale`.

Object Graph
------------

When you create an object-oriented program, you divide it into many enclosed
parts called objects. This process is called encapsultation, and allows you to
clearly link the data and the logic that operates on them. However, all those
sepatate objects still need to be able to collaborate to do your program's job
- they need to have access to each other.

These dependencies between objects can be represented by a directed acyclic
graph. Consider this example:

.. code-block:: python

   class Database:

      def __init__(self, url):
	 self.url = url

      # ....

   class UserManager:

      def __init__(self, database):
	 self.database = database

      def get_user(self, id):
	 self.database.get_model('user', id)

   class EmailSystem:

      # ...

   class Application:

      def __init__(self, user_manager=None, email_system=None):
	 self.user_manager = user_manager
	 self.email_system = email_system

      def send_welcome_email(self, user_id):
	 self.email_system.send_email(
	    self.user_manager.get_user(user_id).email,
	    "Welcome!"
	 )

Relationships between these objects can be represented in a graph like this:

.. image:: dependency_injection/example1.*
   :width: 248px

In Wiring, graphs like this one are represented by
:py:class:`wiring.graph.Graph`. Usually an application has a single
object graph, that can be checked for :term:`dependency cycles
<dependency cycle>` and missing dependencies, and from which the
application gets its entry point. The graph takes care of providing each
object with its dependencies, hence wiring them together.

You'll see all that in a moment, but first we need to explain where are
all those objects coming from.

Specifications
--------------

To actually know which constructor arguments are dependencies and what value
should they be given, the graph needs some sort of hint. The argument name
alone is not enough - you can have two classes with `database` argument in
their constructor, when they should actually use two entirely different
databases.

Instead of argument names, Wiring uses :term:`specifications
<specification>`.  Specification is basically a hashable object used as
an unique identifier of some kind of object in the object graph. Example
specifications could be:

.. code-block:: python

   Database
   (Database, 'archival')
   'db.archive'

There are two ways to specify the dependencies and their specifications for
a function.

:py:func:`@inject <wiring.dependency.inject>` decorator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the simplest, and recommended one, but a little bit more verbose.

.. code-block:: python

   from wiring import inject

   class Database:
      @inject('db.url', read_only='db.read_only')
      def __init__(self, url, read_only=None):
	 self.url = url

:py:attr:`injected <wiring.dependency.injected>` object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This one works only for keyword arguments, but is a little bit less verbose.

.. code-block:: python

   from wiring import inject

   class Database:
      def __init__(self, url=inject('db.url'), read_only=inject('db.read_only')):
	 self.url = url

If you use the `Database` class outside of the object graph (for example in
unit tests) the default value for `url` and `read_only` will be
:py:class:`wiring.dependency.UnrealizedDependency` instances. These always
evaluate to `False`, so you can easily test if you were actually provided with
needed dependencies.

.. code-block:: python

   from wiring import inject

   class Database:
      def __init__(self, url=inject('db.url')):
	 if not url:
	    raise ValueError("No database URL provided.")
	 self.url = url

Example
^^^^^^^

Let's use the :py:func:`@inject <wiring.dependency.inject>` decorator to
annotate the code from out first example.

.. code-block:: python

   from wiring import inject

   class Database:

      @inject('db.url')
      def __init__(self, url):
	 self.url = url

      # ....

   class UserManager:

      @inject('db')
      def __init__(self, database):
	 self.database = database

      def get_user(self, id):
	 self.database.get_model('user', id)

   class EmailSystem:

      # ...

   class Application:

      @inject(user_manager='managers.user', email_system='systems.email')
      def __init__(self, user_manager=None, email_system=None):
	 self.user_manager = user_manager
	 self.email_system = email_system

      def send_welcome_email(self, user_id):
	 self.email_system.send_email(
	    self.user_manager.get_user(user_id).email,
	    "Welcome!"
	 )

Providers
---------

When the graph needs to create an `Application` object, it first needs to get
object for specifications `managers.user` and `systems.email`. To obtain object
instances for given specification the graph will use the :term:`provider`
registered for this specification.

A provider is a callable object implementing
:py:interface:`wiring.providers.IProvider` interface. When called, it returns
an instance of an object it provides. It also declares all dependencies
required to provide an object - the graph takes care of collecting them and
passing them to the provider. There are three basic providers implemented in
Wiring:

:py:class:`FactoryProvider <wiring.providers.FactoryProvider>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This provider wraps a callable that returns the desired object, exposing its
dependencies to a graph. Note that a class is actually also a callable
returning an object.

.. code-block:: python

   from wiring import inject, FactoryProvider

   class MyClass:

     @inject(dependency='foo')
     def __init__(self, dependency=None):
	self.dependency = dependency

     def __str__(self):
	return 'MyClass({})'.format(self.dependency)

   provider = FactoryProvider(MyClass)
   print(provider.dependencies)  # Prints: {'dependency': 'foo'}
   print(provider(dependency=1))  # Prints: MyClass(1)

:py:class:`FunctionProvider <wiring.providers.FunctionProvider>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This provider wraps a callable and returns a new callable with the dependencies
fulfilled, but non-injectable arguments intact. Note that a class is actually
also a callable.

.. code-block:: python

   from wiring import inject, FunctionProvider

   @inject(two='number.two')
   def plus_two(number, two=None):
      return number + two

   provider = FunctionProvider(plus_two)
   print(provider.dependencies)  # Prints: {'two': 'number.two'}
   function = provider(two=2)
   print(function(3)) # Prints: 5

:py:class:`InstanceProvider <wiring.providers.InstanceProvider>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This provider is the simplest one - it just wraps an already created object to
conform to the provider interface. It always returns the object it is given.

.. code-block:: python

   from wiring import InstanceProvider

   provider = InstanceProvider('foobar')
   print(provider.dependencies)  # Prints: {}
   print(provider()) # Prints: foobar

Using providers in a graph
^^^^^^^^^^^^^^^^^^^^^^^^^^

Getting back to the classes from our first example, here's how a graph
can be configured to create fully functional `Application` object:

.. code-block:: python

   from wiring import Graph, FactoryProvider

   graph = Graph()
   graph.register_provider('db.url', InstanceProvider('sqlite:///tmp/test.db'))
   graph.register_provider('application', FactoryProvider(Application))
   graph.register_provider('db', FactoryProvider(Database))
   graph.register_provider('managers.user', FactoryProvider(UserManager))
   graph.register_provider('systems.email', FactoryProvider(EmailSystem))
   application = graph.get('application')
   application.send_welcome_email(213)

Graph also has some shortcut methods for basic providers, so this example can
also be written like this:

.. code-block:: python

   from wiring import Graph

   graph = Graph()
   graph.register_instance('db.url', 'sqlite:///tmp/test.db')
   graph.register_factory('application', Application)
   graph.register_factory('db', Database)
   graph.register_factory('managers.user', UserManager)
   graph.register_factory('systems.email', EmailSystem)
   application = graph.get('application')
   application.send_welcome_email(213)

There is a more convenient way of creating providers and registering them in
the graph, called :term:`modules <module>`, which you'll see shortly.

Scopes
------

Sometimes creating an object is a costly operation (think connecting to
a database) or you just want to use a single object of given specification
throughout your application (think plugin registry). Basically, you want your
object graph to reuse objects when fulfilling dependencies.

Quite often you also have to put some restrictions on how the object is
reused.  What if a database connection object is not thread-safe? You
want to create a new one for new threads, but reuse existing on threads
that already have their connection.

This is what :term:`scopes <scope>` are for.  Scopes are objects implementing
:py:interface:`wiring.scopes.IScope` interface, that manage object cached for
an :term:`object graph`. There are three basic scopes provided by Wiring.

:py:class:`SingletonScope <wiring.scopes.SingletonScope>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objects in this scope are cached forever. Only one instance of the object is
created and reused though the program lifetime. Forked processes also use
a copy of cached instance.

:py:class:`ProcessScope <wiring.scopes.ProcessScope>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objects in this scope are cached per-process. When the program forks, new
process will have to create a new instance of the object.

:py:class:`ThreadScope <wiring.scopes.ThreadScope>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Objects in this scope are cached per-thread. An instance will be created for
each thread, and reused, but only in the thread it was created in.

Using scopes
^^^^^^^^^^^^

Let's assume that we want to reuse `Database` object from our previous
examples, as connecting to the database is costly, but we know that the
connection is not thread-safe. We'll want to put the `Database` object in
a :py:class:`ThreadScope <wiring.scopes.ThreadScope>`.

.. code-block:: python

   from wiring import Graph, ThreadScope

   graph = Graph()
   graph.register_instance('db.url', 'sqlite:///tmp/test.db')
   graph.register_factory('application', Application)
   graph.register_factory('db', Database, scope=ThreadScope)
   graph.register_factory('managers.user', UserManager)
   graph.register_factory('systems.email', EmailSystem)
   application = graph.get('application')
   application.send_welcome_email(213)

Yes, that little ``scope=ThreadScope`` is all it takes.

Injecting Factories
-------------------

The Problem
^^^^^^^^^^^

Scopes have one little caveat. This code is an example of a quite subtle bug:

.. code-block:: python

   from wiring import Graph, inject

   class Database:
      # ...

   class UserManager:

      @inject('db')
      def __init__(self, database):
	 self.database = database

      def get_user(self, id):
	 return self.database.get_model('user', id)

   graph = Graph()
   graph.register_factory('db', Database, scope=ThreadScope)
   graph.register_factory('managers.user', UserManager, scope=SingletonScope)

Notice the scope that providers of those objects were registered with.
The database object is cached per-thread, but user manager is
a singleton. While a single `SingletonScope` lasts through entire
program lifetime, a `ThreadScope` can change multiple times. This means
that the `ThreadScope` is a *narrower* scope than the `SingletonScope`.

Noticed the bug yet? `UserManager` is created only once and reused for all
threads. When it is created, it is provided with a `Database` instance **for
current thread** which it saves as an attribute. This means that when many
different threads will call the `get_user()` method, they will all use a single
`Database` object!  This is why you shouldn't inject objects from a narrower
scope.

The Solution
^^^^^^^^^^^^

The solution is to wrap the dependency specification in a :py:class:`Factory
<wiring.dependency.Factory>` class. When the object graph sees this wrapper,
instead of a ready object it provides a function that, when called, will lazily
return the object from the graph.

.. code-block:: python

   from wiring import Graph, inject, Factory

   class Database:
      # ...

   class UserManager:

      @inject(Factory('db'))
      def __init__(self, db_factory):
	 self.db_factory = db_factory

      def get_user(self, id):
	 database = self.db_factory()
	 return database.get_model('user', id)

   graph = Graph()
   graph.register_factory('db', Database, scope=ThreadScope)
   graph.register_factory('managers.user', UserManager, scope=SingletonScope)

Now each call to `get_user()` will hit the `ThreadScope` and retrieve a proper
instance of database connection for a current thread.

Partial Injection
-----------------

Sometimes you want to have some arguments injected and some provided manually
by user. Lets say that we want to have our `Application` class configurable
with a language code.

.. code-block:: python

   from wiring import inject

   class Application:

      @inject(user_manager='managers.user', email_system='systems.email')
      def __init__(self, language_code, user_manager=None, email_system=None):
         self.language_code = language_code
	 self.user_manager = user_manager
	 self.email_system = email_system

      def send_welcome_email(self, user_id):
	 self.email_system.send_email(
	    self.user_manager.get_user(user_id).email,
	    "Welcome!"
	 )

   # ...

   graph = Graph()
   ApplicationModule().add_to(graph)
   DataModule().add_to(graph)
   application_en = graph.get('application', 'en')
   application_en.send_welcome_email(213)
   application_de = graph.get('application', 'de')
   application_de.send_welcome_email(208)

By providing additional, non-injectable arguments to :py:meth:`Graph.get()
<wiring.graph.Graph.get>` you can easily create customized objects without
worrying about dependencies.

Modules
-------

Registering all your specifications and providers using graph methods is
neither very convenient nor modular. Everything goes in one place full
of tedious code repetition. Fortunately, there's a better way.

Wiring provides a :py:class:`Module <wiring.configuration.Module>` class that
can conveniently gather all the specifications that some part of your
application provides and register them all into the graph with a single line of
code. Let's replace our previous registration code:

.. code-block:: python

   from wiring import Graph, ThreadScope

   graph = Graph()
   graph.register_instance('db.url', 'sqlite:///tmp/test.db')
   graph.register_factory('application', Application)
   graph.register_factory('db', Database, scope=ThreadScope)
   graph.register_factory('managers.user', UserManager, scope=SingletonScope)
   graph.register_factory('systems.email', EmailSystem)
   application_en = graph.get('application', 'en')
   application_en.send_welcome_email(213)
   application_de = graph.get('application', 'de')
   application_de.send_welcome_email(208)

with :term:`modules <module>`:

.. code-block:: python

   from wiring import Graph, Module, SingletonScope, ThreadScope

   class DataModule(Module):
      instances = {
	 'db.url': 'sqlite:///tmp/test.db',
      }
      factories = {
	 'db': (Database, ThreadScope),
	 'managers.user': (UserManager, SingletonScope),
      }

   class ApplicationModule(Module):
      factories = {
	 'application': Application,
	 'systems.email': EmailSystem,
      }

   graph = Graph()
   ApplicationModule().add_to(graph)
   DataModule().add_to(graph)
   application_en = graph.get('application', 'en')
   application_en.send_welcome_email(213)
   application_de = graph.get('application', 'de')
   application_de.send_welcome_email(208)

Now, that's much better. Not only is there less repetition. You can also easily
put your data and application modules in different files, or even replace
entire data module with a new one - just by changing a single line of code.

Factories as module methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is just one little trick you can do with modules. Let's assume that you
need to read the database URL from a file. you could create a separate function
and register it as a `db.url` factory, but you can also put this logic right
in your module.

.. code-block:: python

   from wiring import Module, SingletonScope, ThreadScope, provides, scope

   class DataModule(Module):
      instances = {
	 'db.url_file': 'my_database.txt',
      }
      factories = {
	 'db': (Database, ThreadScope),
	 'managers.user': (UserManager, SingletonScope),
      }

      @provides('db.url')
      @scope(SingletonScope)
      @inject('db.url_file')
      def provide_db_url(self, url_file_path):
	 with open(url_file_path) as url_file:
	    return url_file.read().strip()

That's it, the `provide_db_url()` will be turned into a `FactoryProvider` and
registered in a graph for `db.url` specification, in the `SingletonScope`.

Graph Validation
----------------

As a final touch let's add a single line to our graph building code:

.. code-block:: python

   from wiring import Graph

   graph = Graph()
   ApplicationModule().add_to(graph)
   DataModule().add_to(graph)
   graph.validate()
   application_en = graph.get('application', 'en')
   application_en.send_welcome_email(213)
   application_de = graph.get('application', 'de')
   application_de.send_welcome_email(208)

This line (``graph.validate()``) will check our graph for
:term:`dependency cycles <dependency cycle>` and missing dependencies,
and raise an exception if any problem is found. This is an easy way to
find out if we didn't miss something and `fail fast`_. It's a good practice
to always do this after modyfying the graph and before its first use.

.. _fail fast: https://en.wikipedia.org/wiki/Fail-fast

Final Example
-------------

Finally, let's see the entire example code that slowly evolved throughout this
guide:

.. code-block:: python

   from wiring import (
      inject,
      Module,
      ThreadScope,
      SingletonScope,
      provides,
      scope,
      Graph,
   )

   class Database:

      @inject('db.url')
      def __init__(self, url):
	 self.url = url

      # ....

   class UserManager:

      @inject('db')
      def __init__(self, database):
	 self.database = database

      def get_user(self, id):
	 self.database.get_model('user', id)

   class EmailSystem:

      # ...

   class Application:

      @inject(user_manager='managers.user', email_system='systems.email')
      def __init__(self, language_code, user_manager=None, email_system=None):
         self.language_code = language_code
	 self.user_manager = user_manager
	 self.email_system = email_system

      def send_welcome_email(self, user_id):
	 self.email_system.send_email(
	    self.user_manager.get_user(user_id).email,
	    "Welcome!"
	 )

   class DataModule(Module):
      instances = {
	 'db.url_file': 'my_database.txt',
      }
      factories = {
	 'db': (Database, ThreadScope),
	 'managers.user': (UserManager, SingletonScope),
      }

      @provides('db.url')
      @scope(SingletonScope)
      @inject('db.url_file')
      def provide_db_url(self, url_file_path):
	 with open(url_file_path) as url_file:
	    return url_file.read().strip()

   class ApplicationModule(Module):
      factories = {
	 'application': Application,
	 'systems.email': EmailSystem,
      }

   graph = Graph()
   ApplicationModule().add_to(graph)
   DataModule().add_to(graph)
   application_en = graph.get('application', 'en')
   application_en.send_welcome_email(213)
   application_de = graph.get('application', 'de')
   application_de.send_welcome_email(208)

That's it. Our little example is now fully modular. Each component is easily
replacable and testable, separately from it's dependencies. But even that can
be improved with interfaces, so be sure to also read :doc:`interfaces`.
