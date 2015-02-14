import inspect

import six


__all__ = (
    'Factory',
    'UnrealizedInjection',
    'get_dependencies',
    'inject',
    'injected',
)


class Factory(tuple):
    """
    This class is a wrapper for a specification, declaring that instead of
    a created object for the specification, a callable returning the object
    should be injected.

    For example::

        @inject(db_factory=Factory('db.connection')):
        def get_user(id, db_factory=None):
            db = db_factory()
            return db.get_model('user', id=id)

    Unless an instance for `db.connection` specification is cached in a scope,
    each execution of `get_user()` will create a new database connection
    object.

    This feature is particularly useful when you need an object from a narrower
    scope, like a thread-scoped database connection in an application
    singleton. You cannot just get a connection object in the application
    constructor and save it, because when one of it methods is called from
    a different thread it will use the same connection object. That effectively
    defeats the purpose of thread scope.

    To prevent that you can inject and save in a constructor a factory of
    database connections and call it in every method to obtain a connection
    object for current thread.
    """

    __slots__ = []

    def __new__(cls, *specification):
        """
        You construct this class by giving it :term:`specification` elements.
        For example, if your specification is::

            (IDBConnection, 'archive')

        then you can declare the :term:`dependency` like this::

            @inject(db=Factory(IDBConnection, 'archive'))
            def foo(db=None):
                pass

        When no specification is given to the class constructor,
        a `ValueError` is raised.

        :raises:
            ValueError
        """
        if not specification:
            raise ValueError("No dependency specification given.")
        if len(specification) == 1:
            specification = specification[0]
        else:
            specification = tuple(specification)
        return super(Factory, cls).__new__(
            cls,
            (specification,)
        )

    @property
    def specification(self):
        """
        A :term:`specification` of an object of which a factory will be
        injected.
        """
        return self[0]

    def __repr__(self):
        specification = self.specification
        if not isinstance(specification, tuple):
            specification = '({})'.format(specification)
        return '<Factory{specification}>'.format(
            specification=specification
        )


class UnrealizedInjection(tuple):
    """
    Instances of this class are placeholders that can be used as default values
    for arguments to mark that they should be provided with injected
    :term:`dependency`, without using the :py:func:`inject()` decorator. For
    example::

        def __init__(self, db_connection=UnrealizedInjection(IDBConnection)):
            if not db_connection:
                raise ValueError()

    Note that instances of this class always evaluate to `False` when converted
    to boolean, to allow easy checking for dependencies that hasn't been
    injected.

    Instances of this class are immutable, `as any default argument value in
    Python should be
    <http://docs.python-guide.org/en/latest/writing/gotchas/#mutable-default-arguments>`_.

    There's also an :py:data:`injected` shortcut for this class in this
    package.
    """

    __slots__ = []

    def __new__(cls, *specification):
        """
        You construct this class by giving it :term:`specification` elements.
        For example, if your specification is::

            (IDBConnection, 'archive')

        then you can declare the :term:`dependency` like this::

            def foo(db=UnrealizedInjection(IDBConnection, 'archive')):
                pass

        When no specification is given to the class constructor,
        a `ValueError` is raised.

        :raises:
            ValueError
        """
        if not specification:
            raise ValueError("No dependency specification given.")
        if len(specification) == 1:
            specification = specification[0]
        else:
            specification = tuple(specification)
        return super(UnrealizedInjection, cls).__new__(
            cls,
            (specification,)
        )

    @property
    def specification(self):
        """
        A :term:`specification` of an object that should be injected in place
        of this placholder.
        """
        return self[0]

    def __repr__(self):
        specification = self.specification
        if not isinstance(specification, tuple):
            specification = '({})'.format(specification)
        return '<UnrealizedInjection{specification}>'.format(
            specification=specification
        )

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False


def get_dependencies(factory):
    """
    This function inspects a function to find its arguments marked for
    injection, either with :py:func:`inject()` decorator or
    :py:class:`UnrealizedInjection` class.  If `factory` is a class, then its
    constructor is inspected.

    Returned dictionary is a mapping of::

        [argument index/name] -> [specification]

    For example, dependencies for function::

        @inject(ILogger, db=(IDBConnection, 'archive'))
        def foo(log, db=None):
            pass

    would be::

        {
            0: ILogger,
            'db': (IDBConnection, 'archive'),
        }

    `Old-style classes`_ (from before Python 2.2) are not supported.

    .. _Old-style classes:
        https://docs.python.org/2/reference/datamodel.html#new-style-and-classic-classes
    """
    if inspect.isclass(factory):
        # If factory is a class we want to check constructor depdendencies.
        if six.PY3:
            init_check = inspect.isfunction
        else:
            init_check = inspect.ismethod
        dependencies = {}
        if hasattr(factory, '__init__') and init_check(factory.__init__):
            dependencies.update(get_dependencies(factory.__init__))
        if hasattr(factory, '__new__') and inspect.isfunction(factory.__new__):
            dependencies.update(get_dependencies(factory.__new__))
        return dependencies
    elif inspect.isfunction(factory) or inspect.ismethod(factory):
        function = factory
    else:
        raise TypeError("`factory` must be a class or a function.")

    if hasattr(function, '__injection__'):
        # Function has precollected dependencies (happens when using `inject()`
        # decorator. Nothing to do here.
        return function.__injection__

    dependencies = {}

    def process_dependency_tuples(tuples):
        for key, value in tuples:
            if isinstance(value, UnrealizedInjection):
                dependencies[key] = value.specification
    if six.PY3:
        argument_specification = inspect.getfullargspec(function)
        if argument_specification.kwonlydefaults:
            process_dependency_tuples(
                six.iteritems(argument_specification.kwonlydefaults)
            )
    else:
        argument_specification = inspect.getargspec(function)
    if argument_specification.defaults:
        process_dependency_tuples(zip(
            reversed(argument_specification.args),
            reversed(argument_specification.defaults)
        ))
    return dependencies


def inject(*positional_dependencies, **keyword_dependencies):
    """
    This decorator can be used to specify injection rules for decorated
    function arguments. Each argument to this decorator should be
    a :term:`specification` for injecting into related argument of decorated
    function.  `None` can be given instead of a specification to prevent
    argument from being injected. This is handy for positional arguments.

    Example::

        @inject(None, IDBConnection, logger=(ILogger, 'system'))
        def foo(noninjectable_argument, db_connection, logger=None):
            pass

    This decorator can be used multiple times and also with
    :py:class:`UnrealizedInjection` class. Specified dependencies are collected
    and when conflicting the outermost :term:`specification` is used::

        @inject(db=(IDBConnection, 'archive2'))
        @inject(db=IDBConnection)
        def foo(db=injected(IDBConnection, 'archive')):
            # In this example 'archive2' database connection will be injected.
            pass
    """
    def decorator(function):
        dependencies = get_dependencies(function)

        def process_dependency_tuples(tuples):
            for key, dependency_description in tuples:
                if dependency_description is None:
                    specification = None
                elif isinstance(dependency_description, UnrealizedInjection):
                    specification = dependency_description.specification
                else:
                    specification = dependency_description
                if specification is None:
                    try:
                        del dependencies[key]
                    except KeyError:
                        pass
                else:
                    dependencies[key] = specification

        process_dependency_tuples(enumerate(positional_dependencies))
        process_dependency_tuples(six.iteritems(keyword_dependencies))
        function.__injection__ = dependencies
        return function
    return decorator


injected = UnrealizedInjection
"""
Shortcut for :py:class:`UnrealizedInjection` to be used in method definition
arguments.
"""
