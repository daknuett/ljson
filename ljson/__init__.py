"""
The python3 module to access ljson files.

``ljson.base.mem.Table`` and ``ljson.base.generic.Header``
are imported automatically.

You should see the ``ljson.base`` documentation for 
some info about Table objects.

"""


__all__ = ["base"]


from .base.mem import Table
from .base.generic import Header
