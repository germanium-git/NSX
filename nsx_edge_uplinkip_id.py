#! /usr/bin/env python

from nsx import NSX

edgeid = raw_input("Edge id: ")

inputs = 'inputs/nsx.yml'

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)


# Find uplink IP
print(nsx.getuplinkip(edgeid))


