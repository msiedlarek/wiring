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

**Wiring provides architectural foundation for Python applications**,
featuring:

* dependency injection
* interface definition and validation
* modular component configuration
* small, extremely pedantic codebase

Wiring is supported and tested on Python 2.7, Python 3.3, Python 3.4,
PyPy and PyPy 3.

Source code and issue tracker are `available at GitHub`_.

Support is provided on a best-effort basis, through `Stack Overflow
<https://stackoverflow.com>`_. Please tag your question `wiring`.

This documentation is for Wiring version |release|. Wiring's versioning scheme
fully complies with `Semantic Versioning 2.0`_ specification.

.. _Semantic Versioning 2.0: http://semver.org/spec/v2.0.0.html
.. _available at GitHub: https://github.com/msiedlarek/wiring

Quick Peek
----------

.. code-block:: python

   import wiring
   from wiring import provides, scope, inject, injected, implements

   class DatabaseModule(wiring.Module):
      @provides('db_connection')
      @scope(wiring.ThreadScope)
      def provide_db_connection(self, database_url=injected('database_url')):
         return db_engine.connect(database_url)

   class IUserManager(wiring.Interface):
      def get(id):
         """Get user by ID."""

   @implements(IUserManager)
   class DefaultUserManager(object):

      @inject('db_connection')
      def __init__(self, db_connection):
         self.db = db_connection

      def get(self, id):
         return self.db.sql('SELECT * FROM users WHERE id = :id', id=id)

   class UserModule(wiring.Module):
      factories = {
         IUserManager: DefaultUserManager,
      }

   graph = wiring.Graph()
   DatabaseModule().add_to(graph)
   UserModule().add_to(graph)
   graph.register_instance('database_url', 'sqlite://some.db')
   graph.validate()

   user_manager = graph.get(IUserManager)
   user = user_manager.get(12)

Support
-------

If you have a question about Wiring please `post it on Stack Overflow
<https://stackoverflow.com/questions/ask>`_ tagging it `wiring`. I'll try my
best to help you whenever I find time.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   rationale
   dependency_injection
   interfaces
   license
   glossary
   api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
