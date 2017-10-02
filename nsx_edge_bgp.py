#! /usr/bin/env python

from nsx import NSX
from nsx import credentials
from nsx import createbody
import yaml


inputs = 'inputs/nsx.yml'

# Specify manually the logical switch name to be created
path = raw_input("Path to input YAML file specifying PE parameters: ")


# Create an instance of Class vSphere
cred = credentials(inputs)
nsx = NSX(*cred)

with open(path, 'r') as f:
    s = f.read()

# Read the directory of credentials from file
pe = yaml.load(s)


# Find the edge
try:
    edgeid = nsx.findedge(pe['name'])
except:
    print("Edge doesn't exist")
    sys.exit

# Check uplink IP address ---------------------------------------------------

# Get uplink IP address
pe['routerId'] = nsx.getuplinkip(edgeid)
if pe['routerId'] == 'None':
    print("Uplink port vNIC_0 has no Ip address")
    sys.exit


# Configure Router ID -----------------------------------------------------

# Define XML Body - Global Routing > router ID
xml_routerID = createbody("templates/routerid.j2", pe)


# Configure Router ID
print('Configuring Router ID')
nsx.cfgglobrouting(xml_routerID, edgeid)



# Configure BGP peering -----------------------------------------------------

# Define XML Body - BGP
xml_BGP = createbody("templates/bgp.j2", pe)

# Configure BGP
print('Configuring BGP peering')
nsx.cfgbgp(xml_BGP, edgeid)


