#! /usr/bin/env python

from nsx import NSX

edgename = raw_input("Edge name: ")


inputs = 'inputs/nsx.yml'

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)

# Find edge
edgeid = nsx.findedge(edgename)

# Delete edge
if edgeid:
    nsx.deledge(edgeid)

