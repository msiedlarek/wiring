import unittest

from wiring.dependency import Factory, inject, injected
from wiring.graph import (
    DependencyCycleError,
    Graph,
    MissingDependencyError,
    SelfDependencyError,
    UnknownScopeError
)
from wiring.scopes import ProcessScope

from . import ModuleTest


class GraphModuleTest(ModuleTest):
    module = 'wiring.graph'


class GraphTest(unittest.TestCase):

    def test_valid(self):
        db_hostname = 'example.com'

        def get_database_connection(db_hostname=injected('db.hostname')):
            if db_hostname == 'example.com':
                return {
                    'connected': True,
                }
            else:
                raise Exception("Injection went wrong.")

        class TestClass(object):
            @inject('db_connection')
            def __init__(self, db):
                self.is_ok = db['connected']

        graph = Graph()
        graph.register_instance('db.hostname', db_hostname)
        graph.register_factory('db_connection', get_database_connection)
        graph.register_function(
            'db_connection_function',
            get_database_connection
        )
        graph.register_factory(TestClass, TestClass)
        graph.validate()

        self.assertEqual(graph.get('db.hostname'), 'example.com')
        self.assertDictEqual(
            graph.get('db_connection_function')(),
            {'connected': True}
        )
        test_instance = graph.get(TestClass)
        self.assertIsInstance(test_instance, TestClass)
        self.assertTrue(test_instance.is_ok)

    def test_some_positional_arguments(self):
        @inject(None, 'foo')
        def function(first, second):
            return first, second
        graph = Graph()
        graph.register_instance('foo', 'bar')
        graph.register_function('function', function)
        graph.validate()

        function_instance = graph.get('function')
        first, second = function_instance(123)
        self.assertEqual(first, 123)
        self.assertEqual(second, 'bar')

    def test_some_positional_arguments_class(self):
        class TestClass(object):
            @inject(None, 'foo')
            def __init__(self, first, second):
                self.first = first
                self.second = second

            def test(self):
                return self.first, self.second
        graph = Graph()
        graph.register_instance('foo', 'bar')
        graph.register_factory(TestClass, TestClass)
        graph.validate()

        test_class = graph.get(TestClass, 123)
        first, second = test_class.test()
        self.assertEqual(first, 123)
        self.assertEqual(second, 'bar')

    def test_factory(self):
        class DBConnection(object):
            counter = 0

            def __init__(self):
                DBConnection.counter += 1
                self.id = DBConnection.counter

        @inject(Factory('db'))
        def foo(db_factory):
            self.assertNotIsInstance(db_factory, DBConnection)
            db = db_factory()
            self.assertIsInstance(db, DBConnection)
            return db.id

        graph = Graph()
        graph.register_factory('db', DBConnection)
        graph.register_function('foo', foo)
        graph.validate()

        foo_instance = graph.get('foo')
        self.assertEqual(foo_instance(), 1)
        self.assertEqual(foo_instance(), 2)
        self.assertEqual(foo_instance(), 3)

    def test_factory_arguments(self):
        class DBConnection(object):
            counter = 0

            def __init__(self):
                DBConnection.counter += 1
                self.id = DBConnection.counter

        @inject(db_factory=Factory('db'))
        def foo(multiplier, db_factory=None):
            self.assertNotIsInstance(db_factory, DBConnection)
            db = db_factory()
            self.assertIsInstance(db, DBConnection)
            return multiplier * db.id

        graph = Graph()
        graph.register_factory('db', DBConnection)
        graph.register_function('foo', foo)
        graph.validate()

        foo_instance = graph.get('foo')
        self.assertEqual(foo_instance(100), 100)
        self.assertEqual(foo_instance(1), 2)
        self.assertEqual(foo_instance(100), 300)

    def test_factory_scope(self):
        class DBConnection(object):
            counter = 0

            def __init__(self):
                DBConnection.counter += 1
                self.id = DBConnection.counter

        @inject(Factory('db'))
        def foo(db_factory):
            self.assertNotIsInstance(db_factory, DBConnection)
            db = db_factory()
            self.assertIsInstance(db, DBConnection)
            return db.id

        graph = Graph()
        graph.register_factory('db', DBConnection, scope=ProcessScope)
        graph.register_function('foo', foo)
        graph.validate()

        foo_instance = graph.get('foo')
        self.assertEqual(foo_instance(), 1)
        self.assertEqual(foo_instance(), 1)
        self.assertEqual(foo_instance(), 1)

    def test_self_dependency(self):
        @inject('foobar')
        def function(foo):
            pass
        graph = Graph()
        graph.register_factory('foobar', function)
        with self.assertRaises(SelfDependencyError) as cm:
            graph.validate()
        self.assertEqual(cm.exception.specification, 'foobar')
        self.assertEqual(
            str(cm.exception),
            "Provider for 'foobar' is dependent on itself."
        )

    def test_missing_dependency(self):
        @inject('foobar')
        def function(foo):
            return foo + 1

        graph = Graph()
        graph.register_factory('function', function)
        with self.assertRaises(MissingDependencyError) as cm:
            graph.validate()
        self.assertEqual(cm.exception.dependency, 'foobar')
        self.assertEqual(cm.exception.dependant, 'function')
        self.assertEqual(
            str(cm.exception),
            "Cannot find dependency 'foobar' for 'function' provider."
        )

        graph.register_instance('foobar', 42)
        graph.validate()
        self.assertEqual(graph.get('function'), 43)

    def test_dependency_cycle(self):
        @inject('c')
        def a(c):
            pass

        @inject('a')
        def b(a):
            pass

        @inject('b')
        def c(b):
            pass

        graph = Graph()
        graph.register_factory('a', a)
        graph.register_factory('b', b)
        graph.register_factory('c', c)
        with self.assertRaises(DependencyCycleError) as cm:
            graph.validate()
        self.assertSetEqual(
            frozenset(cm.exception.cycle),
            frozenset(('a', 'b', 'c'))
        )
        message = str(cm.exception)
        self.assertIn("Dependency cycle: ", message)
        self.assertIn("'a'", message)
        self.assertIn("'b'", message)
        self.assertIn("'c'", message)

    def test_acquire_arguments(self):
        @inject(1, None, 3, foo=4)
        def function(a, b, c, foo=None, bar=None):
            return (a, b, c, foo, bar)

        graph = Graph()
        graph.register_instance(1, 11)
        graph.register_instance(3, 33)
        graph.register_instance(4, 44)
        graph.register_factory('function', function)
        graph.validate()

        self.assertTupleEqual(
            graph.acquire('function', arguments={1: 22, 'bar': 55}),
            (11, 22, 33, 44, 55)
        )
        self.assertTupleEqual(
            graph.acquire(
                'function',
                arguments={
                    1: 22,
                    'bar': 55,
                    'foo': 100,
                }
            ),
            (11, 22, 33, 100, 55)
        )
        with self.assertRaises(TypeError):
            graph.acquire(
                'function',
                arguments={
                    1: 22,
                    ('invalid', 'argument', 'key'): 55,
                }
            )

    def test_get_arguments(self):
        def function(a, b=None, c=injected(1)):
            return (a, b, c)

        graph = Graph()
        graph.register_instance(1, 11)
        graph.register_factory('function', function)
        graph.validate()

        self.assertTupleEqual(
            graph.get('function', 33, b=22),
            (33, 22, 11)
        )
        self.assertTupleEqual(
            graph.get('function', 33, b=22, c=44),
            (33, 22, 44)
        )

    def test_scope_factory(self):
        notlocal = [0]

        def factory():
            notlocal[0] += 1
            return notlocal[0]

        graph = Graph()
        graph.register_factory('scoped', factory, scope=ProcessScope)
        graph.register_factory('unscoped', factory)

        self.assertEqual(graph.get('scoped'), 1)
        self.assertEqual(graph.get('scoped'), 1)
        self.assertEqual(graph.get('scoped'), 1)
        self.assertEqual(graph.get('scoped'), 1)
        self.assertEqual(graph.get('scoped'), 1)

        self.assertEqual(graph.get('unscoped'), 2)
        self.assertEqual(graph.get('unscoped'), 3)

        self.assertEqual(graph.get('scoped'), 1)
        self.assertEqual(graph.get('scoped'), 1)

        self.assertEqual(graph.get('unscoped'), 4)

    def test_scope_function(self):
        notlocal = [0]

        def factory():
            notlocal[0] += 1
            return notlocal[0]

        @inject(i='i')
        def function(i):
            return i

        graph = Graph()
        graph.register_factory('i', factory)
        graph.register_function('function', function, scope=ProcessScope)

        self.assertEqual(graph.get('function')(), 1)
        self.assertEqual(graph.get('function')(), 1)
        self.assertEqual(graph.get('function')(), 1)

    def test_unknown_scope(self):
        class FooBarScope(object):
            pass

        graph = Graph()

        with self.assertRaises(UnknownScopeError) as cm:
            graph.register_factory('foo', lambda: None, scope=FooBarScope)
        self.assertEqual(cm.exception.scope_type, FooBarScope)
        self.assertIn('FooBarScope', str(cm.exception))

        with self.assertRaises(UnknownScopeError) as cm:
            graph.register_function('foo', lambda: None, scope=FooBarScope)
        self.assertEqual(cm.exception.scope_type, FooBarScope)
        self.assertIn('FooBarScope', str(cm.exception))

    def test_unregister_provider(self):
        graph = Graph()
        graph.register_instance('foo', 'bar')
        self.assertEqual(graph.get('foo'), 'bar')
        graph.unregister_provider('foo')
        with self.assertRaises(KeyError):
            graph.get('foo')

    def test_unregister_scope(self):
        graph = Graph()
        graph.register_factory('foo', lambda: None, scope=ProcessScope)
        graph.unregister_scope(ProcessScope)
        with self.assertRaises(UnknownScopeError):
            graph.register_factory('bar', lambda: None, scope=ProcessScope)
