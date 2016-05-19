import venusian

from wiring import FactoryProvider, FunctionProvider, InstanceProvider


WIRING_VENUSIAN_CATEGORY = 'wiring'
"""
A `Venusian`_ category under which all Wiring callbacks are registered.

.. _Venusian: https://pypi.python.org/pypi/venusian
"""


def register(provider_factory, *args, **kwargs):
    """
    Returns a decorator that registers its arguments for scanning, so it can be
    picked up by :py:func:`wiring.scanning.scan.scan`.

    First argument - `provider_factory` - is a callable that is invoked during
    scanning with decorated argument and `kwargs` as arguments, and it should
    return a :term:`provider` to be registered.

    Rest of the positional arguments (`args`) are used to build the
    :term:`specification` for registration. If there is only one - it is used
    directly as a specification. If there are more - a tuple of them is used as
    a specification. If there are none - the decorated object itself is used as
    a specification.

    Example::

        @register(FactoryProvider)
        class MyClass:
            pass

        graph = Graph()
        scan_to_graph([__package__], graph)
        assert isinstance(graph.get(MyClass), MyClass)

    Another example::

        @register(FactoryProvider, 'my_factory')
        class MyClass:
            pass

        graph = Graph()
        scan_to_graph([__package__], graph)
        assert isinstance(graph.get('my_factory'), MyClass)
    """
    def decorator(target):
        def callback(scanner, name, target):
            if not args:
                specification = target
            elif len(args) == 1:
                specification = args[0]
            else:
                specification = tuple(args)
            scanner.callback(
                specification,
                provider_factory(target, **kwargs)
            )
        venusian.attach(target, callback, category=WIRING_VENUSIAN_CATEGORY)
        return target
    return decorator


def factory(*args, **kwargs):
    """
    A shortcut for using :py:func:`register` with
    :py:class:`wiring.providers.FactoryProvider`.

    Example::

        from wiring.scanning import register

        @register.factory()
        class MyClass:
            pass
    """
    return register(FactoryProvider, *args, **kwargs)


def function(*args, **kwargs):
    """
    A shortcut for using :py:func:`register` with
    :py:class:`wiring.providers.FunctionProvider`.

    Example::

        from wiring.scanning import register

        @register.function()
        def my_function():
            pass
    """
    return register(FunctionProvider, *args, **kwargs)


def instance(*args, **kwargs):
    """
    A shortcut for using :py:func:`register` with
    :py:class:`wiring.providers.FunctionProvider`.

    Example::

        from wiring.scanning import register

        class MyGlobal:
            pass

        my_global = MyGlobal()
        register.instance('my_global')(my_global)
    """
    return register(InstanceProvider, *args, **kwargs)
