import unittest

from wiring.dependency import UnrealizedInjection, get_dependencies


class GetDependenciesTest(unittest.TestCase):

    def test_keyword_only_arguments(self):
        def function(foo, bar, somearg=UnrealizedInjection(11), *,
                     foobar=UnrealizedInjection('foo', 12), test=12,
                     other=UnrealizedInjection(42)):
            pass
        self.assertDictEqual(
            get_dependencies(function),
            {
                'somearg': 11,
                'foobar': ('foo', 12),
                'other': 42,
            }
        )

    def test_annotations_only(self):
        def function(foo, bar: 33, other_arg=5, somearg: 15 = None, *,
                other: 'foo' = 7, test=2):
            pass
        self.assertDictEqual(
            get_dependencies(function),
            {
                1: 33,
                'somearg': 15,
                'other': 'foo',
            }
        )

    def test_annotations_mixed(self):
        def function(foo, bar: 33, other_arg=UnrealizedInjection(5),
                somearg: 15 = None, *, other: 'foo' = 7,
                test=UnrealizedInjection(2)):
            pass
        self.assertDictEqual(
            get_dependencies(function),
            {
                1: 33,
                'somearg': 15,
                'other_arg': 5,
                'other': 'foo',
                'test': 2,
            }
        )
