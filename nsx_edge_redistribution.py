#! /usr/bin/env python

from nsx import NSX
from nsx import credentials
from nsx import createbody
from nsx import seldc
import yaml

from termcolor import cprint
import sys

from deepdiff import DeepDiff

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
    sys.exit(1)

# Retrieving existing static routes --------------------------------------------
print('\nRetrieving existing static routes')
current_routes = nsx.getstatic(edgeid)

cprint('\nReview the configuration changes', 'red')
cprint('These are the existing static routes already configured on the edge: ', 'yellow')
for i in range(len(current_routes)):
    #print(current_routes[i]['route'] + ' -> ' + current_routes[i]['next_hop'] + ' -> vnic-' +  current_routes[i]['vnic'])
    print(current_routes[i]['route'] + ' -> ' + current_routes[i]['next_hop'] + ' -> vnic-' +  str(current_routes[i]['vnic']) + ', AD ' + str(current_routes[i]['admin_distance']))

"""
# List all routes to be added into redistribution -------------------------------------------

cprint('\nThese are the routes which   : ', 'yellow')
for i in range(len(pe['static'])):
    print(pe['static'][i]['route'] + ' -> ' + pe['static'][i]['next_hop'] + ' -> vnic-' +  str(pe['static'][i]['vnic']) + ', AD ' + str(pe['static'][i]['admin_distance']))
"""

# Remove dupplicate routes --------------------------------------------

ddiff = DeepDiff(current_routes, pe['static'], ignore_order=True)

try:
    new_routes = (ddiff['iterable_item_added'].values())
except:
    new_routes = []


# Remove the default route --------------------------------------------
pe['redistrib'] = []

pe['static'] = current_routes + new_routes

for i in range(len(pe['static'])):
    if pe['static'][i]['route'] != '0.0.0.0/0':
        pe['redistrib'].append(pe['static'][i])

cprint('These static routes will be redistributed into BGP: ', 'yellow')
print('Note: dupplicate routes and the default route have been removed')
for i in range(len(pe['redistrib'])):
    print(pe['redistrib'][i]['route'] + ' -> ' + pe['redistrib'][i]['next_hop'] + ' -> vnic-' +  str(pe['redistrib'][i]['vnic']) + ', AD ' + str(pe['redistrib'][i]['admin_distance']))
print('\n')

cprint(pe['banner'], 'yellow')
agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')



# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Configure route redistribution from Static to BGP  routing -----------------------------------------------------

    # Define XML Body - Redistribution
    xml_Redistrib = createbody("templates/bgp_redistrib.j2", pe)

    print(xml_Redistrib)
    # Configure redistribution
    print('\nReconfiguring BGP and route redistribution from Static to BGP')
    nsx.cfgbgp(xml_Redistrib, edgeid)


