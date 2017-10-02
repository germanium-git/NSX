#! /usr/bin/env python

from nsx import NSX
from nsx import credentials


edgename = raw_input("Edge name: ")


inputs = 'inputs/nsx.yml'

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)

# Find edge
print('Searching for edge id')
edgeid = nsx.findedge(edgename)

# Delete edge
print('Deleting edge-' +  edgeid)
if edgeid:
    nsx.deledge(edgeid)

