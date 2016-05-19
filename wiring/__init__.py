"""
This module imports everything from all other wiring modules, so you can easily
import anything without actually remembering where it was declared::

    from wiring import injected
"""

from wiring.categories import *  # noqa
from wiring.configuration import *  # noqa
from wiring.dependency import *  # noqa
from wiring.graph import *  # noqa
from wiring.interface import *  # noqa
from wiring.providers import *  # noqa
from wiring.scopes import *  # noqa


__title__ = 'wiring'
"""Name of this package."""

__version__ = '0.4.0'
"""
Version of this package, compatible with
`Semantic Versioning 2.0 <http://semver.org/spec/v2.0.0.html>`_.
"""
