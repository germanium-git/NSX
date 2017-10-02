#! /usr/bin/env python

from nsx import NSX
from nsx import createbody
from nsx import credentials
from nsx import seldc
import yaml
from pprint import pprint
from termcolor import cprint
import sys


# Select the instance of NSX manager to be configured - as argument
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'
# Select the instance of NSX manager to be configured - manually
# inputs = raw_input("Choose NSX Manager credentila specification [%s]:"  % 'inputs/nsx.yml') or 'inputs/nsx.yml'


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
    sys.exit
else:
    # Create an instance of Class NSX
    cred = credentials(inputs)
    nsx = NSX(*cred)

    # Define XML Body
    xml_edge = createbody("templates/edge.j2", pe)

    # Create edge
    print('Wait for task to be completed')
    nsx.createedge(xml_edge)

    # Configure HA

    if pe['ha']:
        # Find edge id
        print('Configuring HA')
        #print('Searching for edge-id')
        edgeid = nsx.findedge(pe['name'])
        xml_ha = createbody("templates/ha.j2", pe)
        print('Enabling HA for {0}'.format(pe['name']))
        nsx.cfgha(xml_ha, edgeid)

        #print('Relocating appliances')
        #xml_appl = createbody("templates/appliances.j2", pe)
        #nsx.cfgappliances(xml_appl, edgeid)


