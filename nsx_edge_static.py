#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Configures Static routing
   Date:           2017-10-04
===================================================================================================
"""

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

# Retrieving existing static routes -----------------------------------------------------
print('\nRetrieving existing static routes')
current_routes = nsx.getstatic(edgeid)

cprint('\nReview the static routes to be configured', 'red')
cprint('These are the existing static routes: ', 'yellow')
for i in range(len(current_routes)):
    print(current_routes[i]['route'] + ' -> ' + current_routes[i]['next_hop'] + ' -> vnic-' +
          str(current_routes[i]['vnic']) + ', AD ' + str(current_routes[i]['admin_distance']))

# List all routes to be added -----------------------------------------------------------

cprint('\nThese routes are to be added: ', 'yellow')
for i in range(len(pe['static'])):
    print(pe['static'][i]['route'] + ' -> ' + pe['static'][i]['next_hop'] + ' -> vnic-' +
          str(pe['static'][i]['vnic']) + ', AD ' + str(pe['static'][i]['admin_distance']))

# Remove dupplicate routes & check if any new routes will be added ----- ----------------
print('\nSearching for dupplicate routes')

ddiff = DeepDiff(current_routes, pe['static'], ignore_order=True)

try:
    unique_routes = (ddiff['iterable_item_added'].values())
    cprint('Only unique routes can be added: ', 'yellow')
    for i in range(len(unique_routes)):
        print(unique_routes[i]['route'] + ' -> ' + unique_routes[i]['next_hop'] + ' -> vnic-' +
              str(unique_routes[i]['vnic']) + ', AD ' + str(unique_routes[i]['admin_distance']))
except:
    unique_routes = []
    print("No new routes found")
    

# Check if the default route is to be configured ----------------------------------------
try:
    cprint('\nDefault route will be set to: %s' % pe['defaultRoute'])
except:
    print("\nDefault gateway won't be configured")
    if unique_routes == []:
        sys.exit(1)


print('\n')
cprint(pe['banner'], 'yellow')
agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')

# Replace the list of routes with list of unique routes withot dupplicates
pe['static'] = current_routes + unique_routes


# Check if the default route is to be configured ----------------------------------------
try:
    cprint('\nDefault route will be set to: %s' % pe['defaultRoute'])
except:
    pass

# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Configure Static routing ----------------------------------------------------------
    # Define XML Body - Static
    xml_Static = createbody("templates/static.j2", pe)

    #print(xml_Static)
    # Configure Static routes
    print('\nConfiguring Static routes')
    nsx.cfgstatic(xml_Static, edgeid)


