#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Remove NSX edge
   Date:           2017-10-04
===================================================================================================
"""

from nsx import NSX
from nsx import credentials
from nsx import seldc
import sys


# Select the instance of NSX manager to be configured - as argument
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'


# Input the name of edge
edgename = raw_input("Edge name: ")


# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)

# Find edge
print('Searching for edge id')
edgeid = nsx.findedge(edgename)

# Delete edge
print('Deleting edge-' + edgeid)
if edgeid:
    nsx.deledge(edgeid)

