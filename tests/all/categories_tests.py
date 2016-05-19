import unittest

import six

from wiring import Category


class A(Category):
    pass


class B(Category):
    pass


class CategoriesTest(unittest.TestCase):

    def test_tuplicity(self):
        c = A(1, 2, "foo", "bar")
        self.assertIsInstance(c, tuple)
        self.assertSequenceEqual(c, (1, 2, "foo", "bar"))

    def test_equality_int(self):
        self.assertEqual(A(1), A(1))
        self.assertNotEqual(A(1), A(2))
        self.assertNotEqual(A(1), B(1))
        self.assertNotEqual(A(1), B(2))

    def test_hash_int(self):
        self.assertEqual(hash(A(1)), hash(A(1)))
        self.assertNotEqual(hash(A(1)), hash(A(2)))
        self.assertNotEqual(hash(A(1)), hash(B(1)))
        self.assertNotEqual(hash(A(1)), hash(B(2)))

    def test_equality_string(self):
        self.assertEqual(A('foo'), A('foo'))
        self.assertNotEqual(A('foo'), A('bar'))
        self.assertNotEqual(A('foo'), B('foo'))
        self.assertNotEqual(A('foo'), B('bar'))

    def test_hash_string(self):
        self.assertEqual(hash(A('foo')), hash(A('foo')))
        self.assertNotEqual(hash(A('foo')), hash(A('bar')))
        self.assertNotEqual(hash(A('foo')), hash(B('foo')))
        self.assertNotEqual(hash(A('foo')), hash(B('bar')))

    def test_equality_tuple(self):
        self.assertEqual(A(1, 'foo'), A(1, 'foo'))
        self.assertNotEqual(A(1, 'foo'), A(1, 'bar'))
        self.assertNotEqual(A(1, 'foo'), B(1, 'foo'))
        self.assertNotEqual(A(1, 'foo'), B(1, 'bar'))

    def test_hash_tuple(self):
        self.assertEqual(hash(A(1, 'foo')), hash(A(1, 'foo')))
        self.assertNotEqual(hash(A(1, 'foo')), hash(A(1, 'bar')))
        self.assertNotEqual(hash(A(1, 'foo')), hash(B(1, 'foo')))
        self.assertNotEqual(hash(A(1, 'foo')), hash(B(1, 'bar')))

    def test_repr(self):
        c = A(1, 2, 'foo', 'bar')
        self.assertEqual(repr(c), "A(1, 2, 'foo', 'bar')")
        self.assertEqual(six.text_type(c), six.u("A(1, 2, 'foo', 'bar')"))
