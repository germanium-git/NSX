#! /usr/bin/env python

from nsx import NSX
from nsx import credentials
from nsx import createbody
from nsx import seldc
import yaml

from termcolor import cprint
import sys

# Select the instance of NSX manager to be configured - as argument
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'


# Specify parameters of the Edge to be created - as argument
p_or_s = 'None'

while p_or_s != 'p' and p_or_s != 's':
    p_or_s = raw_input("Which edge do you want to configure? \n primary - p, secondary - s    p/s[p]: ") or 'p'

if p_or_s == 'p':
    path = 'inputs/pe_primary_' + seldc(sys.argv[1:]) + '.yml'
else:
    path = 'inputs/pe_secondary_' + seldc(sys.argv[1:]) + '.yml'


# Create an instance of Class vSphere
cred = credentials(inputs)
nsx = NSX(*cred)

with open(path, 'r') as f:
    s = f.read()

# Read the directory of credentials from file
pe = yaml.load(s)


# Find the edge
print('\nSearching for edge-id')
try:
    edgeid = nsx.findedge(pe['name'])
except:
    print("Edge doesn't exist")
    sys.exit

# Check uplink IP address ---------------------------------------------------

# Get uplink IP address
print('\nChecking the uplink IP address')
pe['routerId'] = nsx.getuplinkip(edgeid)
if pe['routerId'] == 'None':
    print("Uplink port vNIC_0 has no Ip address")
    sys.exit


# Configure Router ID -----------------------------------------------------

# Define XML Body - Global Routing > router ID
xml_routerID = createbody("templates/routerid.j2", pe)


# Configure Router ID
print('\nConfiguring Router ID')
nsx.cfgglobrouting(xml_routerID, edgeid)



# Configure BGP peering -----------------------------------------------------

# Define XML Body - BGP
xml_BGP = createbody("templates/bgp.j2", pe['bgp'])

# Configure BGP
print('\nConfiguring BGP peering')
nsx.cfgbgp(xml_BGP, edgeid)


