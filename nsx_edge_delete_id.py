#! /usr/bin/env python

from nsx import NSX

inputs = 'inputs/nsx.yml'

edgeid = raw_input("Edge id: ")

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)


# Delete logical router
nsx.deledge(edgeid)

