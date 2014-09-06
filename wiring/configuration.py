import inspect
import collections

import six

from wiring.providers import (
    FactoryProvider,
    FunctionProvider,
    InstanceProvider,
)


# TODO(msiedlarek): add `get_provided()`
# TODO(msiedlarek): add `get_scope()`

__all__ = (
    'InvalidConfigurationError',
    'Module',
    'provides',
    'scope',
)


class InvalidConfigurationError(Exception):
    """
    Raised when there is some problem with a :term:`module` class, for example
    when module defines more than one :term:`provider` for a single
    :term:`specification`.
    """

    def __init__(self, module, message):
        self.module = module
        """A :term:`module` class where the problem was found."""
        self.message = message
        """A message describing the problem."""

    def __str__(self):
        return "Configuration error in module {module}: {message}".format(
            module='.'.join((self.module.__module__, self.module.__name__)),
            message=self.message
        )


class ModuleMetaclass(type):
    """
    This metaclass analyzes special attributes of a new :term:`module` classes
    and generates `providers` attribute, which is a mapping of
    :term:`specifications <specification>` and related :term:`providers
    <provider>`.

    Supported attributes are:

        `providers`
            A dictionary mapping specifications to provider objects,
            implementing :py:interface:`wiring.providers.IProvider` interface.

        `instances`
            A dictionary mapping specifications to objects that will be wrapped
            in :py:class:`wiring.providers.InstanceProvider`.

        `factories`
            A dictionary mapping specifications to callable that will be
            wrapped in :py:class:`wiring.providers.FactoryProvider`. If
            dictionary value is a tuple, first element is treated as callable
            and the second as scope type for this provider.

        `functions`
            A dictionary mapping specifications to callable that will be
            wrapped in :py:class:`wiring.providers.FunctionProvider`.

    Three last attributes are provided for convinience and will be merged into
    the first one by this metaclass.  For example this module::

        class SomeModule(Module):
            providers = {
                'foo': CustomProvider('foo'),
            }
            instances = {
                'db_url': 'sqlite://somedb',
            }
            factories = {
                'db_connection': (DatabaseConnection, ThreadScope),
                'bar': create_bar,
            }
            functions = {
                'foobarize': foobarize,
            }

            @provides('fizz')
            def provide_fizz(self, db_connection=injected('db_connection')):
                return db_connection.sql('SELECT fizz FROM buzz;')

    is an equivalent of::

        class SomeModule(Module):
            providers = {
                'foo': CustomProvider('foo'),
                'db_url': InstanceProvider('sqlite://somedb'),
                'db_connection': FactoryProvider(
                    DatabaseConnection,
                    scope=ThreadScope
                ),
                'bar': FactoryProvider(create_bar),
                'foobarize': FunctionProvider(foobarize),
            }

            @provides('fizz')
            def provide_fizz(self, db_connection=injected('db_connection')):
                return db_connection.sql('SELECT fizz FROM buzz;')

    Defined modules can be later register their providers into an :term:`object
    graph` using :py:meth:`Module.add_to`.

    When there is more than one provider declared for a single specification,
    :py:exc:`InvalidConfigurationError` is raised.

    :raises:
        :py:exc:`InvalidConfigurationError`
    """

    def __new__(cls, module_name, bases, attributes):
        special_attributes = (
            'providers',
            'instances',
            'factories',
            'functions',
        )
        module = super(ModuleMetaclass, cls).__new__(
            cls,
            module_name,
            bases,
            {
                key: value for key, value in six.iteritems(attributes)
                if key not in special_attributes
            }
        )

        providers = {}

        for ancestor in reversed(inspect.getmro(module)):
            if cls._is_module_class(ancestor):
                providers.update(ancestor.providers)

        already_provided = set()

        providers_attribute = attributes.get('providers', {})
        providers.update(providers_attribute)
        already_provided.update(six.iterkeys(providers_attribute))

        def check_specification(key):
            if key in already_provided:
                raise InvalidConfigurationError(
                    module,
                    "Multiple sources defined for specification {spec}".format(
                        spec=repr(key)
                    )
                )
            already_provided.add(key)

        for key, value in six.iteritems(attributes.get('instances', {})):
            check_specification(key)
            providers[key] = InstanceProvider(value)
        for key, value in six.iteritems(attributes.get('factories', {})):
            check_specification(key)
            if not isinstance(value, collections.Iterable):
                value = [value]
            if len(value) < 1 or len(value) > 2:
                raise InvalidConfigurationError(
                    module,
                    (
                        "Wrong number of arguments for {spec} in"
                        " `factories`."
                    ).format(
                        spec=repr(key)
                    )
                )
            providers[key] = FactoryProvider(
                value[0],
                scope=(value[1] if len(value) > 1 else None)
            )
        for key, value in six.iteritems(attributes.get('functions', {})):
            check_specification(key)
            providers[key] = FunctionProvider(value)

        for key, value in six.iteritems(attributes):
            if hasattr(value, '__provides__'):
                check_specification(value.__provides__)

        module.providers = providers

        return module

    @classmethod
    def _is_module_class(cls, other_class):
        if not isinstance(other_class, cls):
            # Other class didn't came from this metaclass.
            return False
        if all(map(lambda b: not isinstance(b, cls), other_class.__bases__)):
            # Other class is Module class from this module.
            return False
        return True


@six.add_metaclass(ModuleMetaclass)
class Module(object):
    __doc__ = """
    A base class for :term:`module` classes, using the
    :py:class:`ModuleMetaclass`.
    """ + ModuleMetaclass.__doc__

    providers = {}
    """
    A dictionary mapping specifications to provider objects, implementing
    :py:interface:`wiring.providers.IProvider` interface.
    """

    def add_to(self, graph):
        """
        Register all of declared provider into a given :term:`object graph`.
        """
        for specification, provider in six.iteritems(self.providers):
            graph.register_provider(specification, provider)
        for name in dir(self):
            value = getattr(self, name)
            if hasattr(value, '__provides__'):
                graph.register_factory(
                    value.__provides__,
                    value,
                    scope=getattr(value, '__scope__', None)
                )


def provides(*specification):
    """
    Decorator marking wrapped :py:class:`Module` method as :term:`provider` for
    given :term:`specification`.

    For example::

        class ApplicationModule(Module):

            @provides('db_connection')
            def provide_db_connection(self):
                return DBConnection(host='localhost')
    """
    if len(specification) == 1:
        specification = specification[0]
    else:
        specification = tuple(specification)

    def decorator(function):
        function.__provides__ = specification
        return function

    return decorator


def scope(scope):
    """
    Decorator specifying a :term:`scope` for wrapped :py:class:`Module`
    :term:`provider` method. `scope` should be a scope type that will later be
    registered in an :term:`object graph`.

    For example::

        class ApplicationModule(Module):

            @provides('db_connection')
            @scope(ThreadScope)
            def provide_db_connection(self):
                return DBConnection(host='localhost')
    """
    def decorator(function):
        function.__scope__ = scope
        return function
    return decorator
