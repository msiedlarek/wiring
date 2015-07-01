import inspect
import unittest

import six

from wiring.interface import (
    Attribute,
    Interface,
    InterfaceComplianceError,
    Method,
    MethodValidationError,
    MissingAttributeError,
    get_implemented_interfaces,
    implements,
    implements_only,
    isimplementation
)

from . import ModuleTest


class InterfaceModuleTest(ModuleTest):
    module = 'wiring.interface'


class AttributeTest(unittest.TestCase):

    def test_construction(self):
        attribute = Attribute()
        self.assertIsNone(attribute.docstring)

        attribute = Attribute(docstring="Some docstring.")
        self.assertEqual(attribute.docstring, "Some docstring.")

    def test_repr(self):
        attribute = Attribute()
        self.assertEqual(repr(attribute), '<Attribute()>')

        attribute = Attribute(docstring="Some docstring.")
        self.assertEqual(repr(attribute), '<Attribute("Some docstring.")>')


class MethodTest(unittest.TestCase):

    def _example_method_definition(foo, bar=12):
        """Some example method."""

    def _example_method_implementation(self, foo, bar=12):
        pass

    @classmethod
    def _example_method_classmethod(cls, foo, bar=12):
        pass

    @staticmethod
    def _example_method_static(foo, bar=12):
        pass

    def _get_argspec(self, function):
        if six.PY3:
            return inspect.getfullargspec(function)
        else:
            return inspect.getargspec(function)

    def test_construction(self):
        argspec = self._get_argspec(self._example_method_definition)

        method = Method(argspec)
        self.assertEqual(method.argument_specification, argspec)
        self.assertIsNone(method.docstring)

        method = Method(argspec, docstring="Some docstring.")
        self.assertEqual(method.argument_specification, argspec)
        self.assertEqual(method.docstring, "Some docstring.")

    def test_repr(self):
        argspec = self._get_argspec(self._example_method_definition)

        method = Method(argspec)
        self.assertEqual(repr(method), '<Method(foo, bar=12)>')

        method = Method(argspec, docstring="Some docstring.")
        self.assertEqual(repr(method), '<Method(foo, bar=12)>')

    def test_check_compliance(self):
        argspec = self._get_argspec(self._example_method_definition)

        method = Method(argspec)
        method.check_compliance(self._example_method_implementation)
        method.check_compliance(self._example_method_classmethod)
        method.check_compliance(self._example_method_static)

        def other_implementation(foo, bar=12):
            pass
        method.check_compliance(other_implementation)

        def invalid_implementation(foo, bar=13):
            pass
        with self.assertRaises(MethodValidationError) as cm:
            method.check_compliance(invalid_implementation)
        self.assertEquals(
            cm.exception.expected_argspec,
            argspec
        )
        self.assertEquals(
            cm.exception.observed_argspec,
            self._get_argspec(invalid_implementation)
        )
        self.assertEquals(
            str(cm.exception),
            (
                "Function `invalid_implementation` does not comply with"
                " interface definition. Expected arguments: (foo, bar=12)"
                " Observed arguments: (foo, bar=13)"
            )
        )


class InterfaceTest(unittest.TestCase):

    def assertAttributes(self, interface, attributes):
        self.assertSetEqual(
            frozenset(six.iterkeys(interface.attributes)),
            frozenset(attributes)
        )

    def test_elements(self):
        class IPerson(Interface):
            first_name = Attribute("""First name.""")
            last_name = """Last name."""
            age = 17

            def get_full_name():
                """Returns person's full name."""

            def add_friend(friend, close=False):
                pass

        self.assertAttributes(
            IPerson,
            [
                'first_name',
                'last_name',
                'age',
                'get_full_name',
                'add_friend',
            ]
        )

        first_name = IPerson.attributes['first_name']
        self.assertIsInstance(first_name, Attribute)
        self.assertEqual(first_name.docstring, "First name.")

        last_name = IPerson.attributes['last_name']
        self.assertIsInstance(last_name, Attribute)
        self.assertEqual(last_name.docstring, "Last name.")

        age = IPerson.attributes['age']
        self.assertIsInstance(age, Attribute)
        self.assertIsNone(age.docstring)

        get_full_name = IPerson.attributes['get_full_name']
        self.assertIsInstance(get_full_name, Method)
        self.assertEqual(
            get_full_name.docstring,
            "Returns person's full name."
        )
        if six.PY3:
            self.assertEqual(
                get_full_name.argument_specification,
                inspect.FullArgSpec(
                    args=[],
                    varargs=None,
                    varkw=None,
                    defaults=None,
                    kwonlyargs=[],
                    kwonlydefaults=None,
                    annotations={}
                )
            )
        else:
            self.assertEqual(
                get_full_name.argument_specification,
                inspect.ArgSpec(
                    args=[],
                    varargs=None,
                    keywords=None,
                    defaults=None
                )
            )

        add_friend = IPerson.attributes['add_friend']
        self.assertIsInstance(add_friend, Method)
        self.assertIsNone(add_friend.docstring)
        if six.PY3:
            self.assertEqual(
                add_friend.argument_specification,
                inspect.FullArgSpec(
                    args=['friend', 'close'],
                    varargs=None,
                    varkw=None,
                    defaults=(False,),
                    kwonlyargs=[],
                    kwonlydefaults=None,
                    annotations={}
                )
            )
        else:
            self.assertEqual(
                add_friend.argument_specification,
                inspect.ArgSpec(
                    args=['friend', 'close'],
                    varargs=None,
                    keywords=None,
                    defaults=(False,)
                )
            )

    def test_inheritance(self):
        class IEntity(Interface):
            id = Attribute("""Entity ID.""")

        class IItem(IEntity):
            name = Attribute("""Item name.""")

        class ICreature(IEntity):
            name = Attribute("""Creature name.""")

            def give(item):
                pass

        class ISprite(Interface):
            name = Attribute("""Sprite name.""")

            def get_frame(time):
                pass

        class IPlayer(ICreature, ISprite):
            email = Attribute("""E-mail address.""")

            def login():
                pass

        self.assertAttributes(
            IEntity,
            ['id']
        )

        self.assertAttributes(
            IItem,
            ['id', 'name']
        )
        self.assertEqual(
            IItem.attributes['name'].docstring,
            "Item name."
        )

        self.assertAttributes(
            ICreature,
            [
                'id',
                'name',
                'give',
            ]
        )
        self.assertEqual(
            ICreature.attributes['name'].docstring,
            "Creature name."
        )

        self.assertAttributes(
            ISprite,
            [
                'name',
                'get_frame',
            ]
        )

        self.assertAttributes(
            IPlayer,
            [
                'id',
                'name',
                'give',
                'get_frame',
                'email',
                'login',
            ]
        )

    def test_check_compliance(self):
        class IPerson(Interface):
            first_name = """First name."""
            last_name = """Last name."""

            def get_full_name():
                """Returns person's full name."""

        class ValidPerson(object):
            def __init__(self):
                self.first_name = "Jimmy"
                self.last_name = "Example"

            def get_full_name(self):
                return ' '.join((self.first_name, self.last_name))

        class MissingAttributePerson(object):
            def __init__(self):
                self.last_name = "Example"

            def get_full_name(self):
                return self.last_name

        class BadMethodPerson(object):
            def __init__(self):
                self.first_name = "Jimmy"
                self.last_name = "Example"

            def get_full_name(self, foobar):
                return ' '.join((self.first_name, self.last_name))

        with self.assertRaises(TypeError):
            IPerson.check_compliance(ValidPerson)
        IPerson.check_compliance(ValidPerson())

        with self.assertRaises(MissingAttributeError) as cm:
            IPerson.check_compliance(MissingAttributePerson())
        self.assertIsInstance(cm.exception, InterfaceComplianceError)
        self.assertEquals(cm.exception.attribute_name, 'first_name')
        self.assertEquals(
            str(cm.exception),
            "Validated object is missing `first_name` attribute."
        )

        bad_method_person = BadMethodPerson()
        with self.assertRaises(MethodValidationError) as cm:
            IPerson.check_compliance(bad_method_person)
        self.assertIsInstance(cm.exception, InterfaceComplianceError)
        self.assertEquals(
            cm.exception.function,
            bad_method_person.get_full_name
        )

    def test_check_compliance_inheritance(self):
        class IEntity(Interface):
            id = """Database ID"""

        class ICommon(Interface):
            added = """Creation date"""

        class IPerson(IEntity, ICommon):
            name = """Full name"""

        class IManager(IPerson):
            annoying = """True/True"""

        self.assertTupleEqual(
            IEntity.implied,
            (IEntity,)
        )
        self.assertTupleEqual(
            ICommon.implied,
            (ICommon,)
        )
        self.assertTupleEqual(
            IPerson.implied,
            (IPerson, IEntity, ICommon,)
        )
        self.assertTupleEqual(
            IManager.implied,
            (IManager, IPerson, IEntity, ICommon,)
        )

        self.assertAttributes(
            IEntity,
            ['id']
        )
        self.assertAttributes(
            ICommon,
            ['added']
        )
        self.assertAttributes(
            IPerson,
            [
                'id',
                'added',
                'name',
            ]
        )
        self.assertAttributes(
            IManager,
            [
                'id',
                'added',
                'name',
                'annoying',
            ]
        )

        class InvalidManager1(object):
            def __init__(self):
                self.annoying = True

        with self.assertRaises(MissingAttributeError) as cm:
            IManager.check_compliance(InvalidManager1())

        class InvalidManager2(object):
            def __init__(self):
                self.name = "John Doe"
                self.added = None
                self.annoying = True

        with self.assertRaises(MissingAttributeError) as cm:
            IManager.check_compliance(InvalidManager2())
        self.assertEqual(cm.exception.attribute_name, 'id')

        class ValidManager(object):
            def __init__(self):
                self.id = 1
                self.added = None
                self.annoying = True
                self.name = "John Doe"

        IManager.check_compliance(ValidManager())

    def test_docstring(self):
        class IObject(Interface):
            """Foo bar."""
        self.assertAttributes(
            IObject,
            []
        )
        self.assertEqual(IObject.__doc__, "Foo bar.")


class DeclarationTest(unittest.TestCase):

    def assertIsImplementation(self, obj, interfaces):
        self.assertTrue(isimplementation(obj, interfaces))

    def assertNotIsImplementation(self, obj, interfaces):
        self.assertFalse(isimplementation(obj, interfaces))

    def test_implements(self):
        class ICreature(Interface):
            age = """Age in years."""

        class IPerson(ICreature):
            first_name = Attribute("""First name.""")
            last_name = Attribute("""Last name.""")

            def get_full_name():
                """Returns person's full name."""

        class IObject(Interface):
            id = """Database ID."""

        class IDuck(Interface):
            def quack():
                pass

        class IEmployee(Interface):
            salary = """Salary in USD."""

        @implements(IPerson, IObject)
        class Person(object):
            """Person class."""

            def __init__(self):
                self.id = 1
                self.first_name = 'Foo'
                self.last_name = 'Bar'

            def get_full_name(self):
                return '{} {}'.format(self.first_name, self.last_name)

        @implements(IEmployee)
        class Employee(Person):
            """Employee class."""

        # Make sure the decorator didn't spoil the metadata.
        self.assertEqual(Person.__name__, 'Person')
        self.assertEqual(inspect.getdoc(Person), "Person class.")
        self.assertEqual(Employee.__name__, 'Employee')
        self.assertEqual(inspect.getdoc(Employee), "Employee class.")

        for cls in (Person, Employee,):
            self.assertIsImplementation(cls, [])
            self.assertIsImplementation(cls, ICreature)
            self.assertIsImplementation(cls, IPerson)
            self.assertIsImplementation(cls, IObject)
            self.assertIsImplementation(cls, [IPerson])
            self.assertIsImplementation(cls, [IObject])
            self.assertIsImplementation(cls, [IObject, IPerson])
            self.assertIsImplementation(cls, [ICreature, IObject, IPerson])

            self.assertNotIsImplementation(cls, IDuck)
            self.assertNotIsImplementation(cls, [IPerson, IDuck])
            self.assertNotIsImplementation(cls, [IDuck, IObject])
            self.assertNotIsImplementation(cls, [IObject, IPerson, IDuck])

        self.assertIsImplementation(Employee, IEmployee)
        self.assertNotIsImplementation(Person, IEmployee)

        for obj in (Person(), Employee(),):
            self.assertIsImplementation(obj, [])
            self.assertIsImplementation(obj, ICreature)
            self.assertIsImplementation(obj, IPerson)
            self.assertIsImplementation(obj, IObject)
            self.assertIsImplementation(obj, [IPerson])
            self.assertIsImplementation(obj, [IObject])
            self.assertIsImplementation(obj, [IObject, IPerson])
            self.assertIsImplementation(obj, [ICreature, IObject, IPerson])

            self.assertNotIsImplementation(obj, IDuck)
            self.assertNotIsImplementation(obj, [IPerson, IDuck])
            self.assertNotIsImplementation(obj, [IDuck, IObject])
            self.assertNotIsImplementation(obj, [IObject, IPerson, IDuck])

        self.assertIsImplementation(Employee(), IEmployee)
        self.assertNotIsImplementation(Person(), IEmployee)

    def test_implements_only(self):
        class ICreature(Interface):
            age = """Age in years."""

        class IPerson(ICreature):
            first_name = Attribute("""First name.""")
            last_name = Attribute("""Last name.""")

            def get_full_name():
                """Returns person's full name."""

        class IObject(Interface):
            id = """Database ID."""

        class IDuck(Interface):
            def quack():
                pass

        @implements(IPerson, IObject)
        class Person(object):
            """Person class."""

            def __init__(self):
                self.id = 1
                self.first_name = 'Foo'
                self.last_name = 'Bar'

            def get_full_name(self):
                return '{} {}'.format(self.first_name, self.last_name)

        @implements_only(IDuck)
        class Duck(Person):
            """Duck class."""

            def quack(self):
                pass

        self.assertSetEqual(
            get_implemented_interfaces(Duck),
            set([IDuck])
        )
        self.assertSetEqual(
            get_implemented_interfaces(Person),
            set([ICreature, IPerson, IObject])
        )

        # Make sure the decorator didn't spoil the metadata.
        self.assertEqual(Duck.__name__, 'Duck')
        self.assertEqual(inspect.getdoc(Duck), "Duck class.")

        self.assertIsImplementation(Duck, [])
        self.assertIsImplementation(Duck, IDuck)
        self.assertIsImplementation(Duck, [IDuck])

        self.assertNotIsImplementation(Duck, IPerson)
        self.assertNotIsImplementation(Duck, IObject)
        self.assertNotIsImplementation(Duck, [IPerson, IDuck])
        self.assertNotIsImplementation(Duck, [IDuck, IObject, IPerson])

        duck = Duck()

        self.assertIsImplementation(duck, [])
        self.assertIsImplementation(duck, IDuck)
        self.assertIsImplementation(duck, [IDuck])

        self.assertNotIsImplementation(duck, IPerson)
        self.assertNotIsImplementation(duck, IObject)
        self.assertNotIsImplementation(duck, [IPerson, IDuck])
        self.assertNotIsImplementation(duck, [IDuck, IObject, IPerson])
