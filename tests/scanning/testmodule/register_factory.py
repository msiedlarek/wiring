from wiring.scanning import register


@register.factory()
class RegisterFactoryFactory(object):
    pass


@register.factory('register_factory_named_factory')
class RegisterFactoryNamedFactory(object):
    pass


@register.factory('register_factory', 'tuple_factory')
class RegisterFactoryTupleFactory(object):
    pass
