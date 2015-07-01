import multiprocessing
import threading
import unittest

from wiring.scopes import IScope, ProcessScope, SingletonScope, ThreadScope

from . import ModuleTest


class ScopesModuleTest(ModuleTest):
    module = 'wiring.scopes'


class SingletonScopeTest(unittest.TestCase):

    def test_interface(self):
        IScope.check_compliance(SingletonScope())

    def test(self):
        scope1 = SingletonScope()
        scope2 = SingletonScope()

        scope1['foo'] = 12
        scope2['bar'] = 15

        self.assertNotIn('foo', scope2)
        self.assertIn('foo', scope1)
        self.assertEqual(scope1['foo'], 12)
        scope1['foo'] = 13
        self.assertEqual(scope1['foo'], 13)

        self.assertNotIn('bar', scope1)
        self.assertIn('bar', scope2)
        self.assertEqual(scope2['bar'], 15)
        scope2['bar'] = 16
        self.assertEqual(scope2['bar'], 16)

        def thread_function():
            self.assertNotIn('foo', scope2)
            self.assertIn('foo', scope1)
            self.assertEqual(scope1['foo'], 13)
            scope1['foo'] = 14
            self.assertEqual(scope1['foo'], 14)

            self.assertNotIn('bar', scope1)
            self.assertIn('bar', scope2)
            self.assertEqual(scope2['bar'], 16)
            scope2['bar'] = 17
            self.assertEqual(scope2['bar'], 17)

        thread = threading.Thread(target=thread_function)
        thread.start()
        thread.join(10)

        self.assertEqual(scope1['foo'], 14)
        self.assertEqual(scope2['bar'], 17)


class ProcessScopeTest(unittest.TestCase):

    def test_interface(self):
        IScope.check_compliance(ProcessScope())

    def test(self):
        scope1 = ProcessScope()
        scope2 = ProcessScope()

        scope1['foo'] = 12
        scope2['bar'] = 15

        self.assertNotIn('foo', scope2)
        self.assertIn('foo', scope1)
        self.assertEqual(scope1['foo'], 12)
        scope1['foo'] = 13
        self.assertEqual(scope1['foo'], 13)

        self.assertNotIn('bar', scope1)
        self.assertIn('bar', scope2)
        self.assertEqual(scope2['bar'], 15)
        scope2['bar'] = 16
        self.assertEqual(scope2['bar'], 16)

        def process_function():
            self.assertNotIn('foo', scope1)
            self.assertNotIn('foo', scope2)
            self.assertNotIn('bar', scope1)
            self.assertNotIn('bar', scope2)

            scope1['foo'] = 80
            self.assertEqual(scope1['foo'], 80)
            scope2['bar'] = 90
            self.assertEqual(scope2['bar'], 90)

        process = multiprocessing.Process(target=process_function)
        process.start()
        process.join(10)

        self.assertEqual(scope1['foo'], 13)
        self.assertEqual(scope2['bar'], 16)

        def thread_function():
            self.assertIn('foo', scope1)
            self.assertEqual(scope1['foo'], 13)
            self.assertIn('bar', scope2)
            self.assertEqual(scope2['bar'], 16)

            scope1['from_thread'] = 97
            self.assertEqual(scope1['from_thread'], 97)

        thread = threading.Thread(target=thread_function)
        thread.start()
        thread.join(10)

        self.assertEqual(scope1['from_thread'], 97)


class ThreadScopeTest(unittest.TestCase):

    def test_interface(self):
        IScope.check_compliance(ThreadScope())

    def test(self):
        scope1 = ThreadScope()
        scope2 = ThreadScope()

        scope1['foo'] = 12
        scope2['bar'] = 15

        self.assertNotIn('foo', scope2)
        self.assertIn('foo', scope1)
        self.assertEqual(scope1['foo'], 12)
        scope1['foo'] = 13
        self.assertEqual(scope1['foo'], 13)

        self.assertNotIn('bar', scope1)
        self.assertIn('bar', scope2)
        self.assertEqual(scope2['bar'], 15)
        scope2['bar'] = 16
        self.assertEqual(scope2['bar'], 16)

        def thread_function():
            self.assertNotIn('foo', scope1)
            self.assertNotIn('foo', scope2)
            self.assertNotIn('bar', scope1)
            self.assertNotIn('bar', scope2)

            scope1['foo'] = 80
            self.assertEqual(scope1['foo'], 80)
            scope2['bar'] = 90
            self.assertEqual(scope2['bar'], 90)

        thread = threading.Thread(target=thread_function)
        thread.start()
        thread.join(10)

        self.assertEqual(scope1['foo'], 13)
        self.assertEqual(scope2['bar'], 16)
