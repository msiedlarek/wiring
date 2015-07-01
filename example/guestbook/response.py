import jinja2
from werkzeug.wrappers import Response
from wiring import inject


class TemplateRenderer(object):

    @inject(jinja2.Environment)
    def __init__(self, environment):
        self.environment = environment

    def __call__(self, response, context, template=None):
        response.set_data(
            self.environment.get_template(template).render(context)
        )
        return response


class LazyResponse(Response):

    def __init__(self, renderer, configuration, context, **kwargs):
        self.renderer = renderer
        self.renderer_configuration = configuration
        self.renderer_context = context
        super(LazyResponse, self).__init__(**kwargs)


class TemplateResponse(LazyResponse):

    def __init__(self, template, context={}, **kwargs):
        kwargs.setdefault('mimetype', 'text/html')
        super(TemplateResponse, self).__init__(
            TemplateRenderer,
            {
                'template': template,
            },
            context,
            **kwargs
        )
