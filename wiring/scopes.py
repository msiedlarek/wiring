import threading

from wiring import interface


__all__ = (
    'IScope',
    'ProcessScope',
    'ThreadScope',
)


class IScope(interface.Interface):
    """
    Interface defining a :term:`scope` object.
    """

    def __getitem__(specification):
        """
        Returns a cached instance for given :term:`specification`. Raises
        `KeyError` if there is none.

        :raises:
            KeyError
        """

    def __setitem__(specification, instance):
        """
        Saves a cached `instance` for given :term:`specification`. If there was
        already a cached instance for this specification, it is overriden.
        """

    def __contains__(specification):
        """
        Returns `True` if there is cached instance for given
        :term:`specification` and `False` otherwise.
        """


@interface.implements(IScope)
class ProcessScope(object):
    """
    :term:`Scope` where provided instances are cached per-process.

    .. note::

        If you're looking for a `SingletonScope` you just found it.
    """

    def __init__(self):
        self._cache = {}

    def __getitem__(self, specification):
        return self._cache[specification]

    def __setitem__(self, specification, instance):
        self._cache[specification] = instance

    def __contains__(self, specification):
        return (specification in self._cache)


@interface.implements(IScope)
class ThreadScope(object):
    """
    :term:`Scope` where provided instances are cached per-thread.
    """

    def __init__(self):
        self._local = threading.local()

    def __getitem__(self, specification):
        self._validate()
        return self._local.cache[specification]

    def __setitem__(self, specification, instance):
        self._validate()
        self._local.cache[specification] = instance

    def __contains__(self, specification):
        self._validate()
        return (specification in self._local.cache)

    def _validate(self):
        if not hasattr(self._local, 'cache'):
            self._local.cache = {}
