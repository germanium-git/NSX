#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Resolves edge name to edge-id
   Date:           2017-10-04
===================================================================================================
"""

from nsx import NSX
from nsx import credentials
from nsx import seldc
import sys

# Select the vSphere to be modified
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'


# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)



print(nsx.getedges())
