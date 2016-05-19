import importlib

import six
import venusian

from wiring.scanning.register import WIRING_VENUSIAN_CATEGORY


__all__ = (
    'scan_to_module',
    'scan_to_graph',
    'scan',
)


def scan_to_module(python_modules, module, ignore=tuple()):
    """
    Scans `python_modules` with :py:func:`scan` and adds found providers
    to `module`'s :py:attr:`wiring.configuration.Module.providers`.

    `ignore` argument is passed through to :py:func:`scan`.
    """
    def callback(specification, provider):
        module.providers[specification] = provider
    scan(python_modules, callback, ignore=ignore)


def scan_to_graph(python_modules, graph, ignore=tuple()):
    """
    Scans `python_modules` with :py:func:`scan` and registers found providers
    in `graph`.

    `ignore` argument is passed through to :py:func:`scan`.
    """
    def callback(specification, provider):
        graph.register_provider(specification, provider)
    scan(python_modules, callback, ignore=ignore)


def scan(python_modules, callback, ignore=tuple()):
    """
    Recursively scans `python_modules` for providers registered with
    :py:mod:`wiring.scanning.register` module and for each one calls `callback`
    with :term:`specification` as the first argument, and the provider object
    as the second.

    Each element in `python_modules` may be a module reference or a string
    representing a path to a module.

    Module paths given in `ignore` are excluded from scanning.
    """
    scanner = venusian.Scanner(callback=callback)
    for python_module in python_modules:
        if isinstance(python_module, six.string_types):
            python_module = importlib.import_module(python_module)
        scanner.scan(
            python_module,
            categories=[WIRING_VENUSIAN_CATEGORY],
            ignore=ignore
        )
