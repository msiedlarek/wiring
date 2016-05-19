from wiring.scanning import register


class MyInstance(object):
    pass


instance = MyInstance()
register.instance()(instance)


named_instance = MyInstance()
register.instance('register_instance_named_instance')(named_instance)


tuple_instance = MyInstance()
register.instance('register_instance', 'tuple_instance')(tuple_instance)
