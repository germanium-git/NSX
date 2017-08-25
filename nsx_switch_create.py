#! /usr/bin/env python

from nsx import NSX
from nsx import createbody
from nsx import credentials


inputs = 'inputs/nsx.yml'

# Specify manually the logical switch name to be created
lswitchname = raw_input("Distributed port group: ")

# Create an instance of Class vSphere
cred = credentials(inputs)
nsx = NSX(*cred)

my_vars = {'lswitchname': lswitchname}


# Define XML Body - Global Routing > router ID
xml_switch = createbody("templates/switch.j2", my_vars)

# Create logical switch
nsx.createsw(xml_switch)


