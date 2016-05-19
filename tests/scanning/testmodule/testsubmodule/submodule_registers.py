from wiring.scanning import register


@register.function()
def submodule_function():
    pass


@register.factory()
class SubmoduleFactory():
    pass
