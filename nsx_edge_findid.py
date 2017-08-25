#! /usr/bin/env python

from nsx import NSX


edgename = raw_input("Edge name: ")

inputs = 'inputs/nsx.yml'

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)


print(nsx.findedge(edgename))
