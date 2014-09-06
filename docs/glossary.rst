Glossary
========

.. glossary::

   dependency
      is a relation between two :term:`providers <provider>` when product of
      one provider is needed by the second provider. For example database
      connection provider may need the result of a configuration provider, to
      retrieve connection parameters.

      Dependencies are declared using :term:`specifications <specification>`.

   dependency cycle
      is a situation when dependencies for a given :term:`provider` cannot be
      realized, because one of them is dependent on a said provider, or
      the provider is dependent on itself.

   interface
      is a definition of an object describing attributes and methods an object
      must have to conform to the interface. It is useful for testing whether
      some interchangable module can be used in a given context.

      Interfaces are defined as subclasses of
      :py:class:`wiring.interface.Interface`.

   module
      is a unit of configuration, a :py:class:`wiring.configuration.Module`
      subclass that defines some set of :term:`specifications <specification>`
      and their :term:`providers <provider>`. This allows for easy and modular
      registration of entire application parts into the object graph.

   object graph
      is an object that manages :term:`providers <provider>` and their
      :term:`dependencies <dependency>`, and can be used to retrieve objects
      with all their dependencies satisfied.

      See :py:class:`wiring.graph.Graph`.

   provider
      is a callable object implementing
      :py:interface:`wiring.providers.IProvider` interface, that an
      :term:`object graph` uses to retrieve objects for particular
      :term:`specification`.

      It contains declaration of dependencies that will be injected from the
      object graph when the provider is called, and a type of the scope that
      the graph will use to cache the result.

   scope
      is an object implementing :py:interface:`wiring.scopes.IScope` interface,
      that manages object cached in an :term:`object graph`.

      For example when an object is costly to create (like a database
      connection) but can be reused, :py:class:`wiring.scopes.ThreadScope`
      can be used. Then, its provider will be called only once for each thread
      and its result will be reused whenever database connection is retrieved
      from the object graph in this particular thread.

   specification
      is a hashable object used as an unique identifier of some kind of object
      in an :term:`object graph`. This identifier can be used to register
      provider for that kind of object, declare the provider's dependencies on
      other kinds of objects and retrieve the object from the graph.

      Example specifications could be::

         DBConnection
         (DBConnection, 'test_db')
         'database_url'

