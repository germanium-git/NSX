#! /usr/bin/env python

from nsx import NSX
from nsx import createbody
from nsx import credentials


inputs = 'inputs/nsx.yml'

# Specify manually the distributed port group to be created
dportgroup = raw_input("Distributed port group: ")
vlanid = ''
while not vlanid.isdigit():
    vlanid = raw_input("VLAN-ID: ")



# Create an instance of Class vSphere
cred = credentials(inputs)
nsx = NSX(*cred)


my_vars = { 'lswitchname': lswitchname }

nsx = NSX(nsx_ip, account, passw)


# Define XML Body - Global Routing > router ID
xml_switch = createbody("templates/switch.j2", my_vars)

# Configure Router ID
nsx.createsw(xml_switch)


