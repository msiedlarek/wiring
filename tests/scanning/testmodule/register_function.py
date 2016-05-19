from wiring.scanning import register


@register.function()
def register_function():
    pass


@register.function('register_function_named_function')
class register_function_name(object):
    pass


@register.function('register_function', 'tuple_function')
class register_function_tuple(object):
    pass
