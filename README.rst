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

   python setup.py register
   python setup.py sdist upload -s -i gpgkey@example.com
   python setup.py bdist_wheel upload -s -i gpgkey@example.com

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
