import unittest
import importlib

import six


class ModuleTest(unittest.TestCase):

    module = 'wiring'

    def test_import_all(self):
        package = importlib.import_module(self.module)
        if not hasattr(package, '__all__'):
            return
        for name in package.__all__:
            self.assertTrue(
                hasattr(package, name),
                msg=(
                    "Module `{module}` is missing `{name}` which was declared"
                    " in `__all__`."
                ).format(
                    module=self.module,
                    name=name
                )
            )


class InitTest(unittest.TestCase):

    imported_modules = (
        'wiring.configuration',
        'wiring.dependency',
        'wiring.graph',
        'wiring.interface',
        'wiring.providers',
        'wiring.scopes',
    )

    def test_imports(self):
        import wiring
        for module in self.imported_modules:
            package = importlib.import_module(module)
            if not hasattr(package, '__all__'):
                continue
            for name in package.__all__:
                self.assertTrue(
                    hasattr(wiring, name),
                    msg=(
                        "Module `wiring` is missing `{name}` which should be"
                        " wildcard-imported from `{module}`."
                    ).format(
                        name=name,
                        module=module
                    )
                )

    def test_metadata(self):
        import wiring

        self.assertIsInstance(wiring.__title__, six.string_types)
        self.assertRegexpMatches(wiring.__title__, r'^\w+$')

        self.assertIsInstance(wiring.__version__, six.string_types)
        self.assertRegexpMatches(wiring.__version__, r'^\d+\.\d+\.\d+$')
