wiring.graph
============

.. automodule:: wiring.graph

Graph
-----

.. autoclass:: Graph

   .. autoinstanceattribute:: providers
      :annotation:
   .. autoinstanceattribute:: scopes
      :annotation:
   .. automethod:: acquire
   .. automethod:: get
   .. automethod:: register_provider
   .. automethod:: unregister_provider
   .. automethod:: register_factory
   .. automethod:: register_instance
   .. automethod:: register_scope
   .. automethod:: unregister_scope
   .. automethod:: validate

GraphValidationError
--------------------

.. autoexception:: GraphValidationError

SelfDependencyError
-------------------

.. autoexception:: SelfDependencyError
   :show-inheritance:

   .. autoinstanceattribute:: specification
      :annotation:

MissingDependencyError
----------------------

.. autoexception:: MissingDependencyError
   :show-inheritance:

   .. autoinstanceattribute:: dependency
      :annotation:
   .. autoinstanceattribute:: dependant
      :annotation:

DependencyCycleError
--------------------

.. autoexception:: DependencyCycleError
   :show-inheritance:

   .. autoinstanceattribute:: cycle
      :annotation:

UnknownScopeError
-----------------

.. autoexception:: UnknownScopeError

   .. autoinstanceattribute:: scope_type
      :annotation:
