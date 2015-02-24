import copy
import operator

import six

from wiring.dependency import Factory
from wiring.providers import (
    FactoryProvider,
    FunctionProvider,
    InstanceProvider,
)
from wiring.scopes import (
    SingletonScope,
    ProcessScope,
    ThreadScope,
)


__all__ = (
    'GraphValidationError',
    'SelfDependencyError',
    'MissingDependencyError',
    'DependencyCycleError',
    'UnknownScopeError',
    'Graph',
)


class GraphValidationError(Exception):
    """
    Common base for all :term:`object graph` validation exceptions, allowing
    general except clauses and `instanceof()` testing.
    """


class SelfDependencyError(GraphValidationError):
    """
    Raised when one of :term:`graph <object graph>` :term:`providers
    <provider>` is :term:`dependent <dependency>` on a :term:`specification` it
    itself provides.
    """

    def __init__(self, specification):
        self.specification = specification
        """A :term:`specification` that was dependent on itself."""

    def __str__(self):
        return "Provider for {} is dependent on itself.".format(
            repr(self.specification)
        )


class MissingDependencyError(GraphValidationError):
    """
    Raised when one of :term:`provider`'s :term:`dependencies <dependency>`
    cannot be satisfied within the :term:`object graph`.
    """

    def __init__(self, dependant, dependency):
        self.dependant = dependant
        """
        Specification of a :term:`provider` of which :term:`dependency` cannot
        be satisfied.
        """
        self.dependency = dependency
        """
        :term:`Specification <specification>` of a missing :term:`dependency`.
        """

    def __str__(self):
        return (
            "Cannot find dependency {dependency} for {dependant} provider."
        ).format(
            dependency=repr(self.dependency),
            dependant=repr(self.dependant),
        )


class DependencyCycleError(GraphValidationError):
    """
    Raised when there is a :term:`dependency cycle` in an :term:`object graph`.
    """

    def __init__(self, cycle):
        self.cycle = tuple(cycle)
        """
        A tuple containing all :term:`specifications <specification>` in
        a cycle, in such an order that each element depends on previous element
        and the first element depends on the last one.
        """

    def __str__(self):
        return "Dependency cycle: {cycle}.".format(
            cycle=' -> '.join(
                list(map(repr, self.cycle)) + [repr(self.cycle[0])]
            )
        )


class UnknownScopeError(Exception):
    """
    Raised when registering :term:`provider` with a :term:`scope` type that
    hasn't been previously registered in the :term:`object graph`.
    """

    def __init__(self, scope_type):
        self.scope_type = scope_type
        """Type of the scope that hasn't been properly registered."""

    def __str__(self):
        return (
            "Scope type {scope} was not registered within the object graph."
        ).format(
            scope=repr(self.scope_type)
        )


class Graph(object):
    """
    Respresents an :term:`object graph`. Contains registered scopes and
    providers, and can be used to validate and resolve provider dependencies
    and creating provided objects.
    """

    def __init__(self):
        self.providers = {}
        """
        Dictionary mapping :term:`specifications <specification>` to
        :py:interface:`wiring.providers.IProvider` implementers that can
        provide the specified object.
        """
        self.scopes = {}
        """
        Dictionary mapping :term:`scope` types to their instances. Scope
        instances must conform to :py:interface:`wiring.scopes.IScope`
        interface.
        """
        self.register_scope(SingletonScope, SingletonScope())
        self.register_scope(ProcessScope, ProcessScope())
        self.register_scope(ThreadScope, ThreadScope())

    def acquire(self, specification, arguments=None):
        """
        Returns an object for `specification` injecting its provider
        with a mix of its :term:`dependencies <dependency>` and given
        `arguments`. If there is a conflict between the injectable
        dependencies and `arguments`, the value from `arguments` is
        used.

        When one of `arguments` keys is neither an integer nor a string
        a `TypeError` is raised.

        :param specification:
            An object :term:`specification`.
        :param arguments:
            A dictionary of arguments given to the object :term:`provider`,
            overriding those that would be injected or filling in for those
            that wouldn't.  Positional arguments should be stored under 0-based
            integer keys.
        :raises:
            TypeError
        """
        if arguments is None:
            realized_dependencies = {}
        else:
            realized_dependencies = copy.copy(arguments)
        provider = self.providers[specification]
        if provider.scope is not None:
            if specification in provider.scope:
                return provider.scope[specification]
        dependencies = six.iteritems(provider.dependencies)
        for argument, dependency_specification in dependencies:
            if argument not in realized_dependencies:
                if isinstance(dependency_specification, Factory):
                    def _factory(*args, **kwargs):
                        return self.get(
                            dependency_specification.specification,
                            *args,
                            **kwargs
                        )
                    realized_dependencies[argument] = _factory
                else:
                    realized_dependencies[argument] = self.acquire(
                        dependency_specification
                    )
        args = []
        kwargs = {}
        for argument, value in six.iteritems(realized_dependencies):
            if isinstance(argument, six.integer_types):
                # Integer keys are for positional arguments.
                args.append((argument, value))
            elif isinstance(argument, six.string_types):
                # String keys are for keyword arguments.
                kwargs[argument] = value
            else:
                raise TypeError(
                    "{} is not a valid argument key".format(repr(argument))
                )
        args = map(
            operator.itemgetter(1),
            sorted(args, key=operator.itemgetter(0))
        )
        instance = provider(*args, **kwargs)
        if provider.scope is not None:
            provider.scope[specification] = instance
        return instance

    def get(self, specification, *args, **kwargs):
        """
        A more convenient version of :py:meth:`acquire()` for when you can
        provide positional arguments in a right order.
        """
        arguments = dict(enumerate(args))
        arguments.update(kwargs)
        return self.acquire(specification, arguments=arguments)

    def register_provider(self, specification, provider):
        """
        Registers a :term:`provider` (a :py:class:`wiring.providers.Provider`
        instance) to be called when an object specified by
        :term:`specification` is needed. If there was already a provider for
        this specification it is overriden.
        """
        self.providers[specification] = provider

    def unregister_provider(self, specification):
        """
        Removes :term:`provider` for given `specification` from the graph.
        """
        del self.providers[specification]

    def register_factory(self, specification, factory, scope=None):
        """
        Shortcut for creating and registering
        a :py:class:`wiring.providers.FactoryProvider`.
        """
        if scope is not None:
            try:
                scope = self.scopes[scope]
            except KeyError:
                raise UnknownScopeError(scope)
        self.register_provider(
            specification,
            FactoryProvider(factory, scope=scope)
        )

    def register_function(self, specification, function, scope=None):
        """
        Shortcut for creating and registering
        a :py:class:`wiring.providers.FunctionProvider`.
        """
        if scope is not None:
            try:
                scope = self.scopes[scope]
            except KeyError:
                raise UnknownScopeError(scope)
        self.register_provider(
            specification,
            FunctionProvider(function, scope=scope)
        )

    def register_instance(self, specification, instance):
        """
        Registers given `instance` to be used as-is when an object specified by
        given :term:`specification` is needed. If there was already a provider
        for this specification it is overriden.
        """
        self.register_provider(specification, InstanceProvider(instance))

    def register_scope(self, scope_type, instance):
        """
        Register instance of a :term:`scope` for given scope type. This scope
        may be later referred to by providers using this type.
        """
        self.scopes[scope_type] = instance

    def unregister_scope(self, scope_type):
        """
        Removes a :term:`scope` type from the graph.
        """
        del self.scopes[scope_type]

    def validate(self):
        """
        Asserts that every declared :term:`specification` can actually be
        realized, meaning that all of its :term:`dependencies <dependency>` are
        present and there are no self-dependencies or :term:`dependency cycles
        <dependency cycle>`. If such a problem is found, a proper exception
        (deriving from :py:class:`GraphValidationError`) is raised.

        :raises:
            :py:exc:`MissingDependencyError`,
            :py:exc:`SelfDependencyError`,
            :py:exc:`DependencyCycleError`
        """
        # This method uses Tarjan's strongly connected components algorithm
        # with added self-dependency check to find dependency cyclces.

        # Index is just an integer, it's wrapped in a list as a workaround for
        # Python 2's lack of `nonlocal` keyword, so the nested
        # `strongconnect()` may modify it.
        index = [0]

        indices = {}
        lowlinks = {}
        stack = []

        def strongconnect(specification):
            # Set the depth index for the node to the smallest unused index.
            indices[specification] = index[0]
            lowlinks[specification] = index[0]
            index[0] += 1
            stack.append(specification)
            provider = self.providers[specification]
            dependencies = six.itervalues(provider.dependencies)
            for dependency in dependencies:
                if isinstance(dependency, Factory):
                    dependency = dependency.specification
                if dependency not in self.providers:
                    raise MissingDependencyError(specification, dependency)
                if dependency == specification:
                    raise SelfDependencyError(specification)
                if dependency not in indices:
                    # Dependency has not yet been visited; recurse on it.
                    strongconnect(dependency)
                    lowlinks[specification] = min(
                        lowlinks[specification],
                        lowlinks[dependency]
                    )
                elif dependency in stack:
                    # Dependency is in stack and hence in the current strongly
                    # connected component.
                    lowlinks[specification] = min(
                        lowlinks[specification],
                        indices[dependency]
                    )
            if lowlinks[specification] == indices[specification]:
                component = []
                while True:
                    component.append(stack.pop())
                    if component[-1] == specification:
                        break
                if len(component) > 1:
                    raise DependencyCycleError(reversed(component))

        for specification, provider in six.iteritems(self.providers):
            if specification not in indices:
                strongconnect(specification)
