import threading

from werkzeug.wrappers import Request
from werkzeug.routing import Map, MapAdapter
from werkzeug.exceptions import HTTPException
from wiring import (
    Graph,
    Module,
    provides,
    scope,
    inject,
    Factory,
    implements,
    IScope,
)

from guestbook.response import LazyResponse


class Application(object):

    _threadlocal = threading.local()

    @inject(
        graph=Graph,
        get_url_map_adapter=Factory(MapAdapter)
    )
    def __init__(self, graph=None, get_url_map_adapter=None):
        self.graph = graph
        self.get_url_map_adapter = get_url_map_adapter

    def __call__(self, environment, start_response):
        self._threadlocal.request = Request(environment)
        try:
            return self.dispatch(self._threadlocal.request)(
                environment,
                start_response
            )
        finally:
            self._threadlocal.request = None

    def dispatch(self, request):
        adapter = self.get_url_map_adapter()
        try:
            endpoint, values = adapter.match()
            response = self.graph.get(endpoint)(request, **values)
            if isinstance(response, LazyResponse):
                renderer = self.graph.get(response.renderer)
                response = renderer.__call__(
                    response,
                    response.renderer_context,
                    **response.renderer_configuration
                )
            return response
        except HTTPException, error:
            return error

    @classmethod
    def get_current_request(cls):
        try:
            return cls._threadlocal.request
        except AttributeError:
            return None


@implements(IScope)
class RequestScope(object):

    def _get_storage(self):
        request = Application.get_current_request()
        if not hasattr(request, 'scope_storage'):
            request.scope_storage = {}
        return request.scope_storage

    def __getitem__(self, specification):
        self._get_storage().__getitem__(specification)

    def __setitem__(self, specification, instance):
        self._get_storage().__setitem__(specification, instance)

    def __contains__(self, specification):
        self._get_storage().__contains__(specification)


class ApplicationModule(Module):

    factories = {
        Application: Application,
    }

    @provides(Request)
    def provide_request(self):
        return Application.get_current_request()

    @provides(MapAdapter)
    @scope(RequestScope)
    @inject(Map, Request)
    def provide_map_adapter(self, url_map, request):
        return url_map.bind_to_environ(request.environ)
