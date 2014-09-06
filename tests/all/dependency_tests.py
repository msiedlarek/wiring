import unittest

import six

from wiring.dependency import (
    UnrealizedInjection,
    get_dependencies,
    inject,
    injected,
)

from . import ModuleTest


class DependencyModuleTest(ModuleTest):
    module = 'wiring.dependency'


class UnrealizedInjectionTest(unittest.TestCase):

    def test(self):
        injection = UnrealizedInjection('foo', 2, 3)
        self.assertTupleEqual(injection.specification, ('foo', 2, 3))
        self.assertFalse(injection)
        self.assertEqual(
            repr(injection),
            "<UnrealizedInjection('foo', 2, 3)>"
        )

        injection = UnrealizedInjection(42)
        self.assertEqual(injection.specification, 42)
        self.assertFalse(injection)
        self.assertEqual(
            repr(injection),
            "<UnrealizedInjection(42)>"
        )

    def test_shortcut(self):
        self.assertEqual(injected, UnrealizedInjection)

    def test_hash(self):
        injection = UnrealizedInjection('test')
        self.assertIsInstance(hash(injection), six.integer_types)
        injection = UnrealizedInjection([])
        with self.assertRaises(TypeError):
            # List is an unhashable type.
            hash(injection)

    def test_immutability(self):
        injection = UnrealizedInjection('test')
        self.assertFalse(hasattr(injection, '__dict__'))
        with self.assertRaises(AttributeError):
            injection.specification = 'test2'
        with self.assertRaises(AttributeError):
            injection.foobar = 12


class GetDependenciesTest(unittest.TestCase):

    def test_preprocessed(self):
        def function(foo):
            pass
        function.__injection__ = {'foo': 42}
        self.assertDictEqual(
            get_dependencies(function),
            {'foo': 42}
        )

    def test_exception(self):
        with self.assertRaises(TypeError):
            get_dependencies(42)

    def test_keyword_arguments(self):
        def function(foo, bar, foobar=UnrealizedInjection('foo', 12), test=12,
                     other=UnrealizedInjection(42)):
            pass
        self.assertDictEqual(
            get_dependencies(function),
            {
                'foobar': ('foo', 12),
                'other': 42,
            }
        )

    def test_class(self):
        class Foo(object):
            def __init__(self, bar=UnrealizedInjection('bar')):
                pass

        self.assertDictEqual(
            get_dependencies(Foo),
            {
                'bar': 'bar',
            }
        )

    def test_class_with_new(self):
        class Foo(tuple):
            __slots__ = []

            def __new__(self, bar=UnrealizedInjection('bar')):
                pass

        self.assertDictEqual(
            get_dependencies(Foo),
            {
                'bar': 'bar',
            }
        )

    def test_class_with_both_init_and_new(self):
        class Foo(object):

            def __init__(self, foo=UnrealizedInjection('foo'), **kwargs):
                pass

            def __new__(self, bar=UnrealizedInjection('bar'), **kwargs):
                pass

        self.assertDictEqual(
            get_dependencies(Foo),
            {
                'foo': 'foo',
                'bar': 'bar',
            }
        )


class InjectTest(unittest.TestCase):

    def test_basic(self):
        @inject(injected(12), None, ('foo', 14), foobar=4)
        def function(first, second, third, foo=injected('test'),
                     foobar=None):
            return (first, second, third, foo, foobar)

        self.assertDictEqual(
            function.__injection__,
            {
                0: 12,
                2: ('foo', 14),
                'foo': 'test',
                'foobar': 4,
            }
        )
        self.assertTupleEqual(
            function(1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5)
        )

    def test_class(self):
        class TestClass(object):

            @inject(injected(12), None, ('foo', 14), foobar=4)
            def __init__(self, first, second, third, foo=injected('test'),
                         foobar=None):
                pass

        self.assertDictEqual(
            TestClass.__init__.__injection__,
            {
                0: 12,
                2: ('foo', 14),
                'foo': 'test',
                'foobar': 4,
            }
        )

    def test_overriding(self):
        @inject(12, None, ('foo', 14), foobar=4)
        def function(first, second, third, foobar=injected(7)):
            pass
        self.assertDictEqual(
            function.__injection__,
            {
                0: 12,
                2: ('foo', 14),
                'foobar': 4,
            }
        )

    def test_removing(self):
        @inject(foobar=None)
        def function(foobar=injected(7)):
            pass
        self.assertDictEqual(
            function.__injection__,
            {}
        )

    def test_recursion(self):
        @inject(11)
        @inject(foobar=injected(7))
        def function(test, foobar=None):
            pass
        self.assertDictEqual(
            function.__injection__,
            {
                0: 11,
                'foobar': 7,
            }
        )
