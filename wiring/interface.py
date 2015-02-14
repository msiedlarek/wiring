import inspect
import collections
import operator

import six


__all__ = (
    'InterfaceComplianceError',
    'MissingAttributeError',
    'MethodValidationError',
    'Attribute',
    'Method',
    'Interface',
    'get_implemented_interfaces',
    'set_implemented_interfaces',
    'add_implemented_interfaces',
    'implements',
    'implements_only',
    'isimplementation',
)


class InterfaceComplianceError(Exception):
    """
    Common base for all interface compliance validation errors.
    """


class MissingAttributeError(InterfaceComplianceError):
    """
    Exception raised when an object is validated against :py:class:`Interface`
    (by :py:meth:`Interface.check_compliance`) and is found to be missing
    a required attribute.
    """

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        """Name of the missing attribute."""

    def __str__(self):
        return "Validated object is missing `{attribute}` attribute.".format(
            attribute=self.attribute_name
        )


class MethodValidationError(InterfaceComplianceError):
    """
    Exception raised when a function is validated against :py:class:`Method`
    specification (e.g. by :py:meth:`Interface.check_compliance`) and some of
    the arguments differ.
    """

    def __init__(self, function, expected_argspec, observed_argspec):
        self.function = function
        """
        Function object that didn't pass the check.
        """
        self.expected_argspec = expected_argspec
        """
        An `inspect.ArgSpec` or `inspect.FullArgSpec` (depending on Python
        version) named tuple specifying expected function arguments.
        """
        self.observed_argspec = observed_argspec
        """
        An `inspect.ArgSpec` or `inspect.FullArgSpec` (depending on Python
        version) named tuple specifying arguments that the validated
        function actually takes.
        """

    def __str__(self):
        return (
            "Function `{function}` does not comply with interface definition."
            " Expected arguments: {expected}"
            " Observed arguments: {observed}"
        ).format(
            function=self.function.__name__,
            expected=inspect.formatargspec(*self.expected_argspec),
            observed=inspect.formatargspec(*self.observed_argspec)
        )


class Attribute(object):
    """
    This class stores a specification of an object attribute, namely its
    docstring. It is used by :py:class:`InterfaceMetaclass` to store
    information about required attributes of an :term:`interface`.
    """

    def __init__(self, docstring=None):
        self.docstring = docstring
        """
        Docstring of a described attribute.
        """

    def __repr__(self):
        if self.docstring:
            return '<Attribute("{}")>'.format(self.docstring)
        else:
            return '<Attribute()>'


class Method(Attribute):
    """
    This class stores a specification of a method, describing its arguments and
    holding its docstring. It is used by :py:class:`InterfaceMetaclass` to
    store information about required methods of an :term:`interface`.
    """

    def __init__(self, argument_specification, docstring=None):
        super(Method, self).__init__(docstring)
        self.argument_specification = argument_specification
        """
        An `inspect.ArgSpec` or `inspect.FullArgSpec` (depending on Python
        version) named tuple specifying arguments taken by described method.
        These will not include implied `self` argument.
        """

    def __repr__(self):
        return '<Method{}>'.format(
            inspect.formatargspec(*self.argument_specification)
        )

    def check_compliance(self, function):
        """
        Checks if a given `function` complies with this specification. If an
        inconsistency is detected a :py:exc:`MethodValidationError` exception
        is raised.

        .. note::
            This method will not work as expected when `function` is an unbound
            method (``SomeClass.some_method``), as in Python 3 there is no way
            to recognize that this is in fact a method. Therefore, the implied
            `self` argument will not be ignored.

        :raises:
            :py:exc:`MethodValidationError`
        """
        argument_specification = _get_argument_specification(function)
        if inspect.ismethod(function):
            # Remove implied `self` argument from specification if function is
            # a method.
            argument_specification = argument_specification._replace(
                args=argument_specification.args[1:]
            )
        if argument_specification != self.argument_specification:
            raise MethodValidationError(
                function,
                self.argument_specification,
                argument_specification
            )


class InterfaceMetaclass(type):
    """
    This metaclass analyzes declared attributes and methods of new
    :term:`interface` classes and turns them into a dictionary of
    :py:class:`Attribute` and :py:class:`Method` specifications which is stored
    as `attributes` dictionary of an interface class. It also handles
    inheritance of those declarations.

    It also collects (and stores in `implied` attribute) a set of this and all
    base interfaces, as it never changes after the class is declared and is
    very commonly needed.
    """

    def __new__(cls, interface_name, bases, attributes):
        ignored_attribute_names = (
            '__module__',
            '__qualname__',
            '__locals__',
            '__doc__',
        )
        ignored_attributes = {}
        processed_attributes = {}

        # Filter out private attributes which should not be treated as
        # interface declarations.
        for name, value in six.iteritems(attributes):
            if (isinstance(value, classmethod)
                    or isinstance(value, staticmethod)
                    or name in ignored_attribute_names):
                ignored_attributes[name] = value
            else:
                processed_attributes[name] = value

        interface = super(InterfaceMetaclass, cls).__new__(
            cls,
            interface_name,
            bases,
            ignored_attributes
        )

        # Precalculate a tuple of this and all base interfaces in method
        # resolution order.

        interface.implied = tuple((
            ancestor for ancestor in inspect.getmro(interface)
            if cls._is_interface_class(ancestor)
        ))

        interface.attributes = {}

        for base in reversed(bases):
            if cls._is_interface_class(base):
                interface.attributes.update(base.attributes)

        for name, value in six.iteritems(processed_attributes):
            if isinstance(value, Attribute):
                interface.attributes[name] = value
            elif inspect.isfunction(value):
                docstring = inspect.getdoc(value)
                argument_specification = _get_argument_specification(value)
                interface.attributes[name] = Method(
                    argument_specification,
                    docstring=docstring
                )
            else:
                if isinstance(value, six.string_types):
                    docstring = value
                else:
                    docstring = None
                interface.attributes[name] = Attribute(docstring=docstring)

        return interface

    @classmethod
    def _is_interface_class(cls, other_class):
        if not isinstance(other_class, cls):
            # Other class didn't came from this metaclass.
            return False
        if all(map(lambda b: not isinstance(b, cls), other_class.__bases__)):
            # Other class is Interface class from this module.
            return False
        return True


@six.add_metaclass(InterfaceMetaclass)
class Interface(object):
    __doc__ = """
    A base class for :term:`interface` classes, using the
    :py:class:`InterfaceMetaclass`.
    """ + InterfaceMetaclass.__doc__

    implied = frozenset()
    """
    A `frozenset` of this and all base :term:`interfaces <interface>`.
    """

    attributes = {}
    """
    Dictionary describing provided attributes, including methods. Keys are
    attribute names and values are :py:class:`Attribute` or :py:class:`Method`
    instances.
    """

    @classmethod
    def check_compliance(cls, instance):
        """
        Checks if given `instance` complies with this :term:`interface`. If
        `instance` is found to be invalid a :py:exc:`InterfaceComplianceError`
        subclass is raised.

        `instance`'s class doesn't have to declare it implements an interface
        to be validated against it.

        .. note::
            Classes cannot be validated against an interface, because instance
            attributes couldn't be checked.

        :raises:
            :py:exc:`MissingAttributeError`,
            :py:exc:`MethodValidationError`
        """
        if inspect.isclass(instance):
            raise TypeError(
                "Only instances, not classes, can be validated against an"
                " interface."
            )
        for name, value in six.iteritems(cls.attributes):
            if not hasattr(instance, name):
                raise MissingAttributeError(name)
            if isinstance(value, Method):
                value.check_compliance(getattr(instance, name))


def get_implemented_interfaces(cls):
    """
    Returns a set of :term:`interfaces <interface>` declared as implemented by
    class `cls`.
    """
    if hasattr(cls, '__interfaces__'):
        return cls.__interfaces__
    return six.moves.reduce(
        lambda x, y: x.union(y),
        map(
            get_implemented_interfaces,
            inspect.getmro(cls)[1:]
        ),
        set()
    )


def set_implemented_interfaces(cls, interfaces):
    """
    Declares :term:`interfaces <interface>` as implemented by class `cls`.
    Those already declared are overriden.
    """
    setattr(
        cls,
        '__interfaces__',
        frozenset(
            six.moves.reduce(
                lambda x, y: x.union(y),
                map(operator.attrgetter('implied'), interfaces),
                set()
            )
        )
    )


def add_implemented_interfaces(cls, interfaces):
    """
    Adds :term:`interfaces <interface>` to those already declared as
    implemented by class `cls`.
    """
    implemented = set(
        six.moves.reduce(
            lambda x, y: x.union(y),
            map(operator.attrgetter('implied'), interfaces),
            set()
        )
    )
    implemented.update(*map(
        get_implemented_interfaces,
        inspect.getmro(cls)
    ))
    setattr(cls, '__interfaces__', frozenset(implemented))


def implements(*interfaces):
    """
    Decorator declaring :term:`interfaces <interface>` implemented by
    a decorated class.
    """
    def wrapper(cls):
        add_implemented_interfaces(cls, interfaces)
        return cls
    return wrapper


def implements_only(*interfaces):
    """
    Decorator declaring :term:`interfaces <interface>` implemented by
    a decorated class. Previous declarations including inherited declarations
    are overridden.
    """
    def wrapper(cls):
        set_implemented_interfaces(cls, interfaces)
        return cls
    return wrapper


def isimplementation(obj, interfaces):
    """
    Returns `True` if `obj` is a class implementing all of `interfaces` or an
    instance of such class.

    `interfaces` can be a single :term:`interface` class or an iterable of
    interface classes.
    """
    if not inspect.isclass(obj):
        isimplementation(obj.__class__, interfaces)
    if not isinstance(interfaces, collections.Iterable):
        interfaces = [interfaces]
    return frozenset(interfaces).issubset(
        get_implemented_interfaces(obj)
    )


if six.PY3:
    _get_argument_specification = inspect.getfullargspec
else:
    _get_argument_specification = inspect.getargspec
