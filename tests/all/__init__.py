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

    def test(self):
        import wiring

        self.assertIsInstance(wiring.__title__, six.string_types)
        self.assertRegexpMatches(wiring.__title__, r'^\w+$')

        self.assertIsInstance(wiring.__version__, six.string_types)
        self.assertRegexpMatches(wiring.__version__, r'^\d+\.\d+\.\d+$')

        self.assertIsInstance(wiring.__author__, six.text_type)
        self.assertTrue(wiring.__author__.strip())

        self.assertIsInstance(wiring.__license__, six.text_type)
        self.assertTrue(wiring.__license__.strip())

        self.assertIsInstance(wiring.__copyright__, six.text_type)
        self.assertTrue(wiring.__copyright__.strip())
