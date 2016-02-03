import inspect

from sphinx.domains.python import PyClasslike, PyXRefRole
from sphinx.ext import autodoc
from sphinx.locale import _
from sphinx.util import force_decode
from sphinx.util.docstrings import prepare_docstring

from wiring.interface import Interface, Method, get_implemented_interfaces


class InterfaceDesc(PyClasslike):

    def get_index_text(self, modname, name_cls):
        return '{name} (interface in {module})'.format(
            name=name_cls[0],
            module=modname
        )


class InterfaceDocumenter(autodoc.ClassDocumenter):

    objtype = 'interface'
    member_order = 20

    def __init__(self, *args, **kwargs):
        super(InterfaceDocumenter, self).__init__(*args, **kwargs)
        self.options.show_inheritance = True

    def add_directive_header(self, sig):
        if self.doc_as_attr:
            self.directivetype = 'attribute'
        autodoc.Documenter.add_directive_header(self, sig)
        bases = [
            base for base in self.object.__bases__ if base is not Interface
        ]
        if not self.doc_as_attr and self.options.show_inheritance and bases:
            self.add_line(u'', '<autodoc>')
            bases = [
                u':class:`{module}.{name}`'.format(
                    module=base.__module__,
                    name=base.__name__
                )
                for base in bases
            ]
            self.add_line(
                u'   Extends: {}'.format(', '.join(bases)),
                '<autodoc>'
            )

    def format_args(self):
        return ''

    def document_members(self, all_members=True):
        oldindent = self.indent

        members = list(self.object.attributes.items())
        if self.options.members is not autodoc.ALL:
            specified = []
            for line in (self.options.members or []):
                specified.extend(line.split())
            members = {
                name: value for name, value in members if name in specified
            }

        member_order = (
            self.options.member_order or self.env.config.autodoc_member_order
        )
        if member_order == 'alphabetical':
            members.sort()
        if member_order == 'groupwise':
            members.sort(key=lambda e: isinstance(e[1], Method))
        elif member_order == 'bysource' and self.analyzer:
            name = self.object.__name__
            def keyfunc(entry):
                return self.analyzer.tagorder.get(
                    '.'.join((name, entry[0])),
                    len(self.analyzer.tagorder)
                )
            members.sort(key=keyfunc)

        for name, specification in members:
            self.add_line(u'', '<autointerface>')
            if isinstance(specification, Method):
                self.add_line(
                    u'.. method:: {name}{arguments}'.format(
                        name=name,
                        arguments=inspect.formatargspec(
                            *specification.argument_specification
                        )
                    ),
                    '<autointerface>'
                )
            else:
                self.add_line(
                    u'.. attribute:: {name}'.format(name=name),
                    '<autointerface>'
                )

            doc = specification.docstring
            if doc:
                self.add_line(u'', '<autointerface>')
                self.indent += self.content_indent
                sourcename = u'docstring of %s.%s' % (self.fullname, name)
                docstrings = [prepare_docstring(force_decode(doc, None))]
                for i, line in enumerate(self.process_doc(docstrings)):
                    self.add_line(line, sourcename, i)
                self.add_line(u'', '<autointerface>')
                self.indent = oldindent


def class_interface_documenter(app, what, name, obj, options, lines):
    if what != 'class':
        return
    if options.show_interfaces:
        interfaces = [
            u':py:interface:`{name} <{module}.{name}>`'.format(
                module=interface.__module__,
                name=interface.__name__
            )
            for interface in get_implemented_interfaces(obj)
        ]
        lines.insert(
            0,
            _(u'Implements: {}').format(', '.join(interfaces))
        )
        lines.insert(1, u'')


def method_interface_documenter(app, what, name, obj, options, lines):
    if what != 'method':
        return
    if lines:
        return
    if not getattr(obj, 'im_class'):
        return
    interfaces = get_implemented_interfaces(obj.im_class)
    for interface in interfaces:
        if obj.__name__ in interface.attributes:
            docstring = interface.attributes[obj.__name__].docstring
            lines.extend(
                prepare_docstring(force_decode(docstring, None))
            )


def setup(app):
    app.add_directive_to_domain('py', 'interface', InterfaceDesc)
    app.add_role_to_domain('py', 'interface', PyXRefRole())
    app.add_autodocumenter(InterfaceDocumenter)

    autodoc.ClassDocumenter.option_spec['show-interfaces'] = lambda arg: True

    app.connect('autodoc-process-docstring', class_interface_documenter)
    app.connect('autodoc-process-docstring', method_interface_documenter)
