#! /usr/bin/env python

"""
===================================================================================================
   Description:    template for quick testing of NSX methods
===================================================================================================
"""

from nsx import NSX
from nsx import credentials
cred = credentials('inputs/nsx_mylab.yml')
nsx = NSX(*cred)

# Continue with calling methods of NSX class etc.
nsx.getedges()
nsx.getswitches()
