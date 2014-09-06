Wiring
******

.. image:: http://img.shields.io/pypi/v/wiring.svg?style=flat
   :target: https://pypi.python.org/pypi/wiring/
.. image:: http://img.shields.io/pypi/l/wiring.svg?style=flat
   :target: https://pypi.python.org/pypi/wiring/
.. image:: http://img.shields.io/travis/msiedlarek/wiring.svg?style=flat
   :target: https://travis-ci.org/msiedlarek/wiring
.. image:: http://img.shields.io/coveralls/msiedlarek/wiring.svg?style=flat
   :target: https://coveralls.io/r/msiedlarek/wiring
.. image:: https://readthedocs.org/projects/wiring/badge/?style=flat
   :target: http://wiring.readthedocs.org

**Wiring is a component management framework for Python** featuring:

* dependency injection
* interface definition and validation
* modular and declarative component configuration

Quick Peek
==========

::

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

Documentation
=============

Full documentation is available at `wiring.readthedocs.org
<http://wiring.readthedocs.org>`_.

Development
===========

You can install package for development and testing with::

   virtualenv environment
   . environment/bin/activate
   pip install sphinx tox flake8 wheel sphinx_rtd_theme
   pip install -e .

To run the test suite on supported Python versions use::

   tox

Or on a single version::

   tox -e py27

To validate PEP8 compliance and run code static checking::

   tox -e flake8

To generate test coverage report::

   rm -rf .coverage coverage
   tox -- --with-coverage
   open coverage/index.html

To generate html documentation::

   cd docs
   make html
   open _build/html/index.html

To release::

   git tag -s -u gpgkey@example.com v0.1.0
   python setup.py register
   python setup.py sdist upload -s -i gpgkey@example.com
   python setup.py bdist_wheel upload -s -i gpgkey@example.com
   git push origin v0.1.0

License
=======

Copyright 2014 Mikołaj Siedlarek <mikolaj@siedlarek.pl>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
