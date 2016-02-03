import unittest

from wiring.configuration import (
    InvalidConfigurationError,
    Module,
    provides,
    scope
)
from wiring.dependency import inject
from wiring.graph import Graph
from wiring.providers import (
    FactoryProvider,
    FunctionProvider,
    InstanceProvider
)
from wiring.scopes import ProcessScope

from . import ModuleTest


class DependencyModuleTest(ModuleTest):
    module = 'wiring.configuration'


class ModuleTest(unittest.TestCase):

    def test(self):
        class SomeClass(object):
            pass

        def foobar():
            return 7

        class SomeModule(Module):
            providers = {
                'test': InstanceProvider('test'),
            }
            instances = {
                'foo': 12,
            }
            factories = {
                'bar': SomeClass,
                'singleton': (SomeClass, ProcessScope),
            }
            functions = {
                'foobar': foobar,
            }

            @provides('fizz')
            def provide_fizz(self):
                return 'fizz!'

            @provides('buzz', 12)
            @scope(ProcessScope)
            def provide_buzz_12(self):
                return 'buzz12!'

        self.assertSetEqual(
            set(SomeModule.providers.keys()),
            {'test', 'foo', 'bar', 'singleton', 'foobar'}
        )
        self.assertIsInstance(SomeModule.providers['test'], InstanceProvider)
        self.assertIsInstance(SomeModule.providers['foo'], InstanceProvider)
        self.assertIsInstance(SomeModule.providers['bar'], FactoryProvider)
        self.assertIsInstance(
            SomeModule.providers['singleton'],
            FactoryProvider
        )
        self.assertIsInstance(SomeModule.providers['foobar'], FunctionProvider)

        graph = Graph()
        module = SomeModule()

        module.add_to(graph)

        self.assertSetEqual(
            set(graph.providers.keys()),
            {'test', 'foo', 'bar', 'singleton', 'foobar', 'fizz', ('buzz', 12)}
        )
        self.assertIsInstance(graph.providers['test'], InstanceProvider)
        self.assertIsInstance(graph.providers['foo'], InstanceProvider)
        self.assertIsInstance(graph.providers['bar'], FactoryProvider)
        self.assertIsInstance(
            graph.providers['singleton'],
            FactoryProvider
        )
        self.assertIs(graph.get('singleton'), graph.get('singleton'))
        self.assertIsInstance(graph.providers['foobar'], FunctionProvider)
        self.assertIsInstance(graph.providers[('buzz', 12)], FactoryProvider)
        self.assertIs(
            graph.providers[('buzz', 12)].scope,
            ProcessScope
        )
        self.assertIsInstance(graph.providers['fizz'], FactoryProvider)
        self.assertIsNone(graph.providers['fizz'].scope)

        self.assertEqual(graph.get('fizz'), 'fizz!')
        self.assertEqual(graph.get(('buzz', 12)), 'buzz12!')

    def test_duplicate_validation(self):
        with self.assertRaises(InvalidConfigurationError) as cm:
            class SomeModule(Module):
                providers = {
                    'foo': InstanceProvider(11),
                }
                instances = {
                    'foo': 12,
                }

        self.assertEqual(cm.exception.module.__name__, 'SomeModule')
        self.assertIn("Multiple sources", cm.exception.message)
        self.assertIn("foo", cm.exception.message)
        self.assertIn(cm.exception.message, str(cm.exception))

        with self.assertRaises(InvalidConfigurationError) as cm:
            class OtherModule(Module):
                instances = {
                    'fizzbuzz': 12,
                }

                @provides('fizzbuzz')
                def provide_fizzbuzz(self):
                    return 13

        self.assertEqual(cm.exception.module.__name__, 'OtherModule')
        self.assertIn("Multiple sources", cm.exception.message)
        self.assertIn("fizzbuzz", cm.exception.message)
        self.assertIn(cm.exception.message, str(cm.exception))

    def test_factory_args_count_validation(self):
        with self.assertRaises(InvalidConfigurationError) as cm:
            class WrongNumberModule1(Module):
                factories = {
                    'foo': (lambda: 12, ProcessScope, 'invalid'),
                }

        self.assertEqual(cm.exception.module.__name__, 'WrongNumberModule1')
        self.assertIn("Wrong number", cm.exception.message)
        self.assertIn("foo", cm.exception.message)
        self.assertIn(cm.exception.message, str(cm.exception))

        with self.assertRaises(InvalidConfigurationError) as cm:
            class WrongNumberModule2(Module):
                factories = {
                    'foo': tuple(),
                }

        self.assertEqual(cm.exception.module.__name__, 'WrongNumberModule2')
        self.assertIn("Wrong number", cm.exception.message)
        self.assertIn("foo", cm.exception.message)
        self.assertIn(cm.exception.message, str(cm.exception))

    def test_provides_positional_arguments(self):
        class SomeModule(Module):
            instances = {
                'buzz': 12,
            }

            @provides('fizzbuzz')
            @inject('buzz')
            def provide_fizzbuzz(self, buzz):
                return 13, buzz

        graph = Graph()
        SomeModule().add_to(graph)

        fizz, buzz = graph.get('fizzbuzz')
        self.assertEqual(fizz, 13)
        self.assertEqual(buzz, 12)
