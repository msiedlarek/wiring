from wiring import FactoryProvider, InstanceProvider
from wiring.scanning import register


@register.register(FactoryProvider)
class PlainRegisterFactory(object):
    pass


@register.register(FactoryProvider, 'plain_register_named_factory')
class PlainRegisterNamedFactory(object):
    pass


@register.register(FactoryProvider, 'plain_register', 'tuple_factory')
class PlainRegisterTupleFactory(object):
    pass


@register.register(InstanceProvider)
class PlainRegisterInstance(object):
    pass


@register.register(InstanceProvider, 'plain_register_named_instance')
class PlainRegisterNamedInstance(object):
    pass


@register.register(InstanceProvider, 'plain_register', 'tuple_instance')
class PlainRegisterTupleInstance(object):
    pass
