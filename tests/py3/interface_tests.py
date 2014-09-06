import unittest
import inspect

import six

from wiring.interface import (
    MethodValidationError,
    Method,
)


class MethodTest(unittest.TestCase):

    def _example_method_definition(foo, bar=12, *, foobar):
        """Some example method."""

    def _example_method_implementation(self, foo, bar=12, *, foobar):
        pass

    @classmethod
    def _example_method_classmethod(cls, foo, bar=12, *, foobar):
        pass

    @staticmethod
    def _example_method_static(foo, bar=12, *, foobar):
        pass

    def _get_argspec(self):
        return inspect.getfullargspec(self._example_method_definition)

    def test_construction(self):
        argspec = self._get_argspec()

        method = Method(argspec)
        self.assertEqual(method.argument_specification, argspec)
        self.assertIsNone(method.docstring)

        method = Method(argspec, docstring="Some docstring.")
        self.assertEqual(method.argument_specification, argspec)
        self.assertEqual(method.docstring, "Some docstring.")

    def test_repr(self):
        argspec = self._get_argspec()

        method = Method(argspec)
        self.assertEqual(repr(method), '<Method(foo, bar=12, *, foobar)>')

        method = Method(argspec, docstring="Some docstring.")
        self.assertEqual(repr(method), '<Method(foo, bar=12, *, foobar)>')

    def test_check_compliance(self):
        argspec = self._get_argspec()

        method = Method(argspec)
        method.check_compliance(self._example_method_implementation)
        method.check_compliance(self._example_method_classmethod)
        method.check_compliance(self._example_method_static)

        def other_implementation(foo, bar=12, *, foobar):
            pass
        method.check_compliance(other_implementation)

        def invalid_implementation1(foo, bar=12):
            pass
        with self.assertRaises(MethodValidationError):
            method.check_compliance(invalid_implementation1)

        def invalid_implementation2(foo, bar=13, *, foobar):
            pass
        with self.assertRaises(MethodValidationError):
            method.check_compliance(invalid_implementation2)
