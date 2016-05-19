import unittest

from wiring import (
    FactoryProvider,
    FunctionProvider,
    Graph,
    InstanceProvider,
    Module
)
from wiring.scanning import scan, scan_to_graph, scan_to_module


class ScanningTest(unittest.TestCase):

    def test_module_autoscan(self):
        class FirstModule(Module):
            scan = ['tests.scanning.testmodule']
            scan_ignore = ['tests.scanning.testmodule.ignoredsubmodule']
        module = FirstModule()
        self._validate_providers(module.providers)

        from . import testmodule

        class SecondModule(Module):
            scan = [testmodule]
            scan_ignore = ['tests.scanning.testmodule.ignoredsubmodule']
        module = FirstModule()
        self._validate_providers(module.providers)

    def test_scan(self):
        providers = {}

        def callback(specification, provider):
            providers[specification] = provider

        scan(
            ['tests.scanning.testmodule'],
            callback,
            ignore=['tests.scanning.testmodule.ignoredsubmodule']
        )
        self._validate_providers(providers)

        from . import testmodule

        providers = {}

        def callback(specification, provider):
            providers[specification] = provider

        scan(
            [testmodule],
            callback,
            ignore=['tests.scanning.testmodule.ignoredsubmodule']
        )
        self._validate_providers(providers)

    def test_scan_to_graph(self):
        graph = Graph()
        scan_to_graph(
            ['tests.scanning.testmodule'],
            graph,
            ignore=['tests.scanning.testmodule.ignoredsubmodule']
        )
        self._validate_providers(graph.providers)

        from . import testmodule

        graph = Graph()
        scan_to_graph(
            [testmodule],
            graph,
            ignore=['tests.scanning.testmodule.ignoredsubmodule']
        )
        self._validate_providers(graph.providers)

    def test_scan_to_module(self):
        module = Module()
        scan_to_module(
            ['tests.scanning.testmodule'],
            module,
            ignore=['tests.scanning.testmodule.ignoredsubmodule']
        )
        self._validate_providers(module.providers)

        from . import testmodule

        module = Module()
        scan_to_module(
            [testmodule],
            module,
            ignore=['tests.scanning.testmodule.ignoredsubmodule']
        )
        self._validate_providers(module.providers)

    def _validate_providers(self, providers):
        # register.register()

        from .testmodule.plain_register import PlainRegisterFactory
        provider = providers[PlainRegisterFactory]
        self.assertIsInstance(provider, FactoryProvider)
        self.assertIs(provider.factory, PlainRegisterFactory)

        from .testmodule.plain_register import PlainRegisterNamedFactory
        provider = providers['plain_register_named_factory']
        self.assertIsInstance(provider, FactoryProvider)
        self.assertIs(provider.factory, PlainRegisterNamedFactory)

        from .testmodule.plain_register import PlainRegisterTupleFactory
        provider = providers[('plain_register', 'tuple_factory')]
        self.assertIsInstance(provider, FactoryProvider)
        self.assertIs(provider.factory, PlainRegisterTupleFactory)

        from .testmodule.plain_register import PlainRegisterInstance
        provider = providers[PlainRegisterInstance]
        self.assertIsInstance(provider, InstanceProvider)
        self.assertIs(provider.instance, PlainRegisterInstance)

        from .testmodule.plain_register import PlainRegisterNamedInstance
        provider = providers['plain_register_named_instance']
        self.assertIsInstance(provider, InstanceProvider)
        self.assertIs(provider.instance, PlainRegisterNamedInstance)

        from .testmodule.plain_register import PlainRegisterTupleInstance
        provider = providers[('plain_register', 'tuple_instance')]
        self.assertIsInstance(provider, InstanceProvider)
        self.assertIs(provider.instance, PlainRegisterTupleInstance)

        # register.factory()

        from .testmodule.register_factory import RegisterFactoryFactory
        provider = providers[RegisterFactoryFactory]
        self.assertIsInstance(provider, FactoryProvider)
        self.assertIs(provider.factory, RegisterFactoryFactory)

        from .testmodule.register_factory import RegisterFactoryNamedFactory
        provider = providers['register_factory_named_factory']
        self.assertIsInstance(provider, FactoryProvider)
        self.assertIs(provider.factory, RegisterFactoryNamedFactory)

        from .testmodule.register_factory import RegisterFactoryTupleFactory
        provider = providers[('register_factory', 'tuple_factory')]
        self.assertIsInstance(provider, FactoryProvider)
        self.assertIs(provider.factory, RegisterFactoryTupleFactory)

        # register.function()

        from .testmodule.register_function import register_function
        provider = providers[register_function]
        self.assertIsInstance(provider, FunctionProvider)
        self.assertIs(provider.function, register_function)

        from .testmodule.register_function import register_function_name
        provider = providers['register_function_named_function']
        self.assertIsInstance(provider, FunctionProvider)
        self.assertIs(provider.function, register_function_name)

        from .testmodule.register_function import register_function_tuple
        provider = providers[('register_function', 'tuple_function')]
        self.assertIsInstance(provider, FunctionProvider)
        self.assertIs(provider.function, register_function_tuple)

        # register.instance()

        from .testmodule.register_instance import instance
        provider = providers[instance]
        self.assertIsInstance(provider, InstanceProvider)
        self.assertIs(provider.instance, instance)

        from .testmodule.register_instance import named_instance
        provider = providers['register_instance_named_instance']
        self.assertIsInstance(provider, InstanceProvider)
        self.assertIs(provider.instance, named_instance)

        from .testmodule.register_instance import tuple_instance
        provider = providers[('register_instance', 'tuple_instance')]
        self.assertIsInstance(provider, InstanceProvider)
        self.assertIs(provider.instance, tuple_instance)

        # submodule

        from .testmodule.testsubmodule.submodule_registers import (
            submodule_function,
            SubmoduleFactory,
        )
        self.assertIn(submodule_function, providers)
        self.assertIn(SubmoduleFactory, providers)

        # ignored

        from .testmodule.ignoredsubmodule.ignored_registers import (
            ignored_function,
            IgnoredFactory,
        )
        self.assertNotIn(ignored_function, providers)
        self.assertNotIn(IgnoredFactory, providers)
