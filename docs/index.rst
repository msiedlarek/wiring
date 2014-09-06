Wiring
======

.. image:: http://img.shields.io/pypi/v/wiring.svg?style=flat
   :target: https://pypi.python.org/pypi/wiring/
   :alt: Latest Version

.. image:: http://img.shields.io/pypi/l/wiring.svg?style=flat
   :target: https://pypi.python.org/pypi/wiring/
   :alt: License

.. image:: http://img.shields.io/travis/msiedlarek/wiring.svg?style=flat
   :target: https://travis-ci.org/msiedlarek/wiring
   :alt: Last Build

.. image:: http://img.shields.io/coveralls/msiedlarek/wiring.svg?style=flat
   :target: https://coveralls.io/r/msiedlarek/wiring
   :alt: Test Coverage

.. image:: https://readthedocs.org/projects/wiring/badge/?style=flat
   :target: http://wiring.readthedocs.org
   :alt: Documentation

.. A line break to separate badges from description.
|

**Wiring is a component management framework for Python** featuring:

* dependency injection
* interface definition and validation
* modular and declarative component configuration

This documentation is for Wiring version |release|. Wiring's versioning scheme
fully complies with `Semantic Versioning 2.0`_ specification.

.. _Semantic Versioning 2.0: http://semver.org/spec/v2.0.0.html

Quick Peek
----------

.. code-block:: python

   from wiring.graph import Graph
   from wiring.configuration import Module, provides, scope
   from wiring.scopes import ThreadScope
   from wiring.dependency import inject, injected
   from wiring.interface import interface, implements

   class DatabaseModule(Module):
      @provides('db_connection')
      @scope(ThreadScope)
      def provide_db_connection(self, database_url=injected('database_url')):
         return db_engine.connect(database_url)

   class IUserManager(Interface):
      def get(id):
         """Get user by ID."""

   @implements(IUserManager)
   class DefaultUserManager(object):

      @inject('db_connection')
      def __init__(self, db_connection):
         self.db = db_connection

      def get(self, id):
         self.db.sql('SELECT * FROM users WHERE id = :id', id=id)

   class UserModule(Module):
      factories = {
         IUserManager: DefaultUserManager,
      }

   graph = Graph()
   DatabaseModule().add_to(graph)
   UserModule().add_to(graph)
   graph.register_instance('database_url', 'sqlite://some.db')
   graph.validate()

   user_manager = graph.get(IUserManager)
   user = user_manager.get(12)

Contents
--------

.. toctree::
   :maxdepth: 2

   rationale
   license
   glossary
   api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
