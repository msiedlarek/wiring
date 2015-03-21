import logging.config

from werkzeug.serving import run_simple
from wiring import Graph

from guestbook.module import GuestbookModule
from guestbook.application import RequestScope


def get_application():
    graph = Graph()
    graph.register_scope(RequestScope, RequestScope())
    graph.register_instance(Graph, graph)
    GuestbookModule().add_to(graph)
    graph.validate()
    return graph.get('wsgi.application')


def serve():
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'guestbook': {
                'level': 'DEBUG',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    })
    run_simple(
        '127.0.0.1',
        8000,
        get_application(),
        use_debugger=True,
        use_reloader=True
    )
