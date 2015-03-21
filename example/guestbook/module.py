import pkg_resources
import jinja2
from wiring import Module, provides, scope, inject, SingletonScope
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.routing import Map, Rule

from guestbook.application import Application, ApplicationModule
from guestbook.response import TemplateRenderer
from guestbook import views


class GuestbookModule(Module):

    factories = {
        TemplateRenderer: TemplateRenderer,
    }

    functions = {
        'views.home': views.home,
    }

    routes = [
        Rule('/', endpoint='views.home'),
    ]

    def add_to(self, graph):
        ApplicationModule().add_to(graph)
        super(GuestbookModule, self).add_to(graph)

    @provides('wsgi.application')
    @scope(SingletonScope)
    @inject(application=Application)
    def provide_wsgi_application(self, application=None):
        application = SharedDataMiddleware(application, {
            '/static': pkg_resources.resource_filename(__name__, 'static')
        })
        return application

    @provides(Map)
    @scope(SingletonScope)
    def provide_url_map(self):
        return Map(self.routes)

    @provides(jinja2.Environment)
    @scope(SingletonScope)
    def provide_jinja_environment(self, url=None, static=None):
        return jinja2.Environment(
            loader=jinja2.PackageLoader(__name__),
            auto_reload=True
        )
