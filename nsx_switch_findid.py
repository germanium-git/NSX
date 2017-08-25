#! /usr/bin/env python

from nsx import NSX
from nsx import createbody
from nsx import credentials


inputs = 'inputs/nsx.yml'

lswitchname =  raw_input("Logical switch name: ")

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)


# Find dvswitch-id and VXLAN VNI
print(nsx.findswitch(lswitchname))
