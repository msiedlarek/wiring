import functools

from wiring import interface
from wiring.dependency import get_dependencies


__all__ = (
    'IProvider',
    'FactoryProvider',
    'FunctionProvider',
    'InstanceProvider',
)


class IProvider(interface.Interface):
    """
    Interface defining a :term:`provider` object.
    """

    dependencies = """
    A dictionary of provider dependencies, required to provide an object.
    A mapping of::

        [argument index/name] -> [specification]
    """

    scope = """
    A :term:`scope` object managing how provided instances will be
    cached, or None when not applicable.
    """

    def __call__(*args, **kwargs):
        """
        Called with dependencies (specified in :py:attr:`dependencies`
        attribute) as arguments (and possibly other, additional arguments)
        returns a provided object. Provider is not responsible for caching
        objects in scopes and should never return a cached object.
        """


class ProviderBase(object):

    def __init__(self):
        self.dependencies = {}
        self.scope = None


@interface.implements(IProvider)
class FactoryProvider(ProviderBase):
    """
    A :term:`provider` that wraps a :py:attr:`factory` callable and when called
    passes required dependencies to it and returns its result.

    For example::

        class DBConnection(object):
            def __init__(self, url=injected('db_url')):
                self._connection = engine.open(url)

        graph = Graph()
        graph.register_instance('db_url', 'somedb://localhost')
        graph.register_provider('db_connection', FactoryProvider(DBConnection))

        # `url` is automatically injected from the graph
        db_connection = graph.get('db_connection')
    """

    def __init__(self, factory, scope=None):
        super(FactoryProvider, self).__init__()
        self.dependencies = get_dependencies(factory)
        self.factory = factory
        """A callable that returns an object to be provided."""
        self.scope = scope

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)


@interface.implements(IProvider)
class FunctionProvider(ProviderBase):
    """
    A :term:`provider` that wraps a :py:attr:`function` to provide a version of
    it with automatically injected dependencies, as defined in
    :py:attr:`dependencies` attribute.

    For example::

        def get_user(id, db_connection=injected('db_connection')):
            return db_connection.sql(
                'SELECT * FROM users WHERE id = :id',
                id=id
            )

        graph = Graph()
        graph.register_instance('db_connection', connection)
        graph.register_provider('get_user', FunctionProvider(get_user))

        # Database connection is automatically injected from the object graph,
        # but we provide `id` manually.
        user = graph.get('get_user')(12)
    """

    def __init__(self, function):
        super(FunctionProvider, self).__init__()
        self.dependencies = get_dependencies(function)
        self.function = function
        """Wrapped function object."""

    def __call__(self, *args, **kwargs):
        # We need to update it later, so we need to make sure it's not a tuple.
        args = list(args)

        @functools.wraps(self.function)
        def wrapper(*call_args, **call_kwargs):
            args[:len(call_args)] = call_args
            kwargs.update(call_kwargs)
            return self.function(*args, **kwargs)

        return wrapper


@interface.implements(IProvider)
class InstanceProvider(ProviderBase):
    """
    A :term:`provider` wrapping already created singleton object.  Always
    returns the object given to the constructor.
    """

    def __init__(self, instance):
        super(InstanceProvider, self).__init__()
        self.instance = instance
        """A single object that will be provided on every call."""

    def __call__(self, *args, **kwargs):
        return self.instance
