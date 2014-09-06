wiring.interface
================

.. automodule:: wiring.interface

Interface
---------

.. autoclass:: Interface

   .. autoattribute:: implied
      :annotation:
   .. autoattribute:: attributes
      :annotation:
   .. automethod:: check_compliance

@implements
-----------

.. autofunction:: implements

@implements_only
----------------

.. autofunction:: implements_only

isimplementation
----------------

.. autofunction:: isimplementation

get_implemented_interfaces
--------------------------

.. autofunction:: get_implemented_interfaces

set_implemented_interfaces
--------------------------

.. autofunction:: set_implemented_interfaces

add_implemented_interfaces
--------------------------

.. autofunction:: add_implemented_interfaces

Attribute
---------

.. autoclass:: Attribute

   .. autoinstanceattribute:: docstring
      :annotation:

Method
------

.. autoclass:: Method
   :show-inheritance:

   .. autoinstanceattribute:: argument_specification
      :annotation:
   .. automethod:: check_compliance

MissingAttributeError
---------------------

.. autoexception:: MissingAttributeError
   :show-inheritance:

   .. autoinstanceattribute:: attribute_name
      :annotation:

MethodValidationError
---------------------

.. autoexception:: MethodValidationError
   :show-inheritance:

   .. autoinstanceattribute:: function
      :annotation:
   .. autoinstanceattribute:: expected_argspec
      :annotation:
   .. autoinstanceattribute:: observed_argspec
      :annotation:

InterfaceComplianceError
------------------------

.. autoexception:: InterfaceComplianceError
