"""

ljson.slapdash is basically the messy little brother
of ljson.

slapdash is oriented on document-oriented databases.
The main difference to ljson is that slapdash rows
do not get typechecked and there is no way to ensure
homogenity.

However the header might provide some information about
the data, for instance, what fields are most common,
most unique.


"""

from .mem import Table
from .generic import SlapdashHeader
