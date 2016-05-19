__all__ = (
    'Category',
)


class Category(tuple):
    """
    This type acts as tuple with one key difference - two instances of it are
    equal only when they have the same type. This allows you to easily mitigate
    collisions when using common types (like string) in a dict or as a Wiring
    :term:`specification`.

    Example::

        from wiring import Graph, Category

        class Public(Category):
            pass

        class Secret(Category):
            pass

        graph = Graph()
        graph.register_instance(Public('database', 1), 'db://public/1')
        graph.register_instance(Private('database', 1), 'db://private/1')

        assert Public('database', 1) != Private('database', 1)
        assert (
            graph.get(Public('database', 1))
                != graph.get(Private('database', 1))
        )
    """

    def __new__(cls, *args):
        return super(Category, cls).__new__(cls, args)

    def __repr__(self):
        return type(self).__name__ + super(Category, self).__repr__()

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return (
            type(self) == type(other) and super(Category, self).__eq__(other)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((
            type(self),
            super(Category, self).__hash__()
        ))
