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


# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)

# Input the name of edge
edgename = raw_input("Edge name: ")

# Select the instance of NSX manager to be configured - as argument
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'


print(nsx.findedge(edgename))

