from wiring.scanning import register


@register.function()
def ignored_function():
    pass


@register.factory()
class IgnoredFactory():
    pass
