#! /usr/bin/env python

from nsx import NSX
from nsx import createbody
from nsx import credentials


inputs = 'inputs/nsx.yml'

switchid = raw_input("Logical switch id: ")

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)


# Delete logical switch
nsx.delsw(switchid)


