import unittest

from wiring.dependency import (
    UnrealizedInjection,
    get_dependencies,
)


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
