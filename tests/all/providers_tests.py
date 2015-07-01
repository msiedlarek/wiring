import unittest

from wiring.dependency import inject, injected
from wiring.providers import (
    FactoryProvider,
    FunctionProvider,
    InstanceProvider,
    IProvider
)

from . import ModuleTest


class ProvidersModuleTest(ModuleTest):
    module = 'wiring.providers'


class FactoryProviderTest(unittest.TestCase):

    def test_basic(self):
        def factory():
            return 42
        provider = FactoryProvider(factory)
        IProvider.check_compliance(provider)
        self.assertDictEqual(provider.dependencies, {})
        self.assertEqual(provider(), 42)

    def test_dependencies(self):
        @inject(injected(12), None, ('foo', 14), foobar=4)
        def function(first, second, third, foo=injected('test'),
                     foobar=None):
            return (first, second, third, foo, foobar)
        provider = FactoryProvider(function)
        self.assertDictEqual(
            provider.dependencies,
            {
                0: 12,
                2: ('foo', 14),
                'foo': 'test',
                'foobar': 4,
            }
        )
        self.assertTupleEqual(
            provider(1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5)
        )

    def test_class(self):
        class TestClass(object):

            @inject(injected(12), None, ('foo', 14), foobar=4)
            def __init__(self, second, third, foo=injected('test'),
                         foobar=None):
                self.arguments = (second, third, foo)

        provider = FactoryProvider(TestClass)
        self.assertDictEqual(
            provider.dependencies,
            {
                0: 12,
                2: ('foo', 14),
                'foo': 'test',
                'foobar': 4,
            }
        )
        self.assertIsInstance(
            provider(1, 2, 3,),
            TestClass
        )
        self.assertTupleEqual(
            provider(1, 2, 3,).arguments,
            (1, 2, 3)
        )


class FunctionProviderTest(unittest.TestCase):

    def test(self):
        def foo(bar, foobar=injected('test')):
            return bar + foobar
        provider = FunctionProvider(foo)
        IProvider.check_compliance(provider)
        self.assertEqual(provider.function, foo)
        self.assertDictEqual(
            provider.dependencies,
            {
                'foobar': 'test',
            }
        )
        wrapped_function = provider(foobar=12)
        self.assertEqual(wrapped_function(5), 17)
        self.assertEqual(wrapped_function(6), 18)
        self.assertEqual(wrapped_function(-2), 10)
        wrapped_function = provider(foobar=1)
        self.assertEqual(wrapped_function(6), 7)
        self.assertEqual(wrapped_function(-2), -1)

    def test_variable_arguments(self):
        """
        This test is related to a problem with variable number of arguments
        and FunctionProvider, see issue #4.
        """
        def foo(*args):
            return tuple(args)
        provider = FunctionProvider(foo)
        wrapped_function = provider()
        self.assertSequenceEqual(wrapped_function(1, 2), (1, 2))
        self.assertSequenceEqual(wrapped_function(1), (1,))

    def test_kwargs_copy(self):
        def foo(*args, **kwargs):
            return tuple(args), dict(kwargs)

        provider = FunctionProvider(foo)
        wrapped_function = provider()
        self.assertSequenceEqual(
            wrapped_function(1, 2, test=1),
            ((1, 2), {'test': 1})
        )
        self.assertSequenceEqual(
            wrapped_function(1, 2, test=2),
            ((1, 2), {'test': 2})
        )
        self.assertSequenceEqual(
            wrapped_function(1, 2),
            ((1, 2), {})
        )

        provider = FunctionProvider(foo)
        wrapped_function = provider()
        self.assertSequenceEqual(
            wrapped_function(1, 2, test=1),
            ((1, 2), {'test': 1})
        )
        self.assertSequenceEqual(
            wrapped_function(test=2),
            ((), {'test': 2})
        )


class InstanceProviderTest(unittest.TestCase):

    def test(self):
        instance = object()
        provider = InstanceProvider(instance)
        IProvider.check_compliance(provider)
        self.assertDictEqual(provider.dependencies, {})
        self.assertEqual(provider(), instance)
