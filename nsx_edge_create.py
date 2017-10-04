#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Create an NSX edge
   Date:           2017-10-04
===================================================================================================
"""

from nsx import NSX
from nsx import createbody
from nsx import credentials
from nsx import seldc
import yaml
from termcolor import cprint
import sys


# Select the instance of NSX manager to be configured - as argument
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'


# Specify parameters of the Edge to be created - as argument
p_or_s = 'None'

while p_or_s != 'p' and p_or_s != 's':
    p_or_s = raw_input("What kind of Provider Edge do you want to create? \n primary - p, secondary - s    p/s[p]: ") or 'p'

if p_or_s == 'p':
    path = 'inputs/pe_primary_' + seldc(sys.argv[1:]) + '.yml'
else:
    path = 'inputs/pe_secondary_' + seldc(sys.argv[1:]) + '.yml'

# Specify parameters of the Edge to be created - manually
# path = raw_input("Path to input YAML file specifying PE parameters: ")

dvportgroup = raw_input("Specify the Uplink port - dvportgroup-x: ")

vw = raw_input("Specify the CE IC port - virtualwire-x: ")


# Read PE parameters
with open(path, 'r') as f:
    edge_spec = f.read()

# Read the directory of credentials from file
pe = yaml.load(edge_spec)

pe['dvswitchpg'] = 'dvportgroup-' + str(dvportgroup)
pe['lswitch'] = 'virtualwire-' + str(vw)

# Print configuration summary
print('\n')
cprint(pe['banner'], 'yellow')
cprint('\nReview the new edge to be created:', 'red')
print('  Name:               %s' % pe['name'])
print('  Uplink IP:          %s' % pe['uplink']['address'])
print('  Uplink dvportgroup: dvportgroup-%s' % dvportgroup)
print('  CE interconnect IP: %s' % pe['interconnect']['address'])
print('  CE interconnect sw: virtualwire-%s' % vw)
print('\n')

agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Proceed with updating configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Create an instance of Class NSX
    cred = credentials(inputs)
    nsx = NSX(*cred)

    # Define XML Body
    xml_edge = createbody("templates/edge.j2", pe)

    # Create edge
    print('Wait for tasks to be completed')
    print('Deploying the edge VM - {0} ---------'.format(pe['name']))
    nsx.createedge(xml_edge)

    # Configure HA

    if pe['ha']:
        print('Searching for edge-id')
        edgeid = nsx.findedge(pe['name'])
        xml_ha = createbody("templates/ha.j2", pe)
        print('Enabling HA ---------')
        nsx.cfgha(xml_ha, edgeid)


