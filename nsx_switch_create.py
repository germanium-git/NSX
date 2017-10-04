#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Configures logical switch
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
# Select the instance of NSX manager to be configured - manually
# inputs = raw_input("Choose NSX Manager credentila specification [%s]:"  % 'inputs/nsx.yml') or 'inputs/nsx.yml'


# Path to YAML file specifying Logical Switch parameters - same as credentials
with open(inputs, 'r') as f:
    s = f.read()

# Read the directory of credentials and vdnScopeId
sw = yaml.load(s)


# Specify manually the logical switch name to be created
print('Logical switch name should follow this convention: %s' % sw['lsw_name'])

lswitchname = raw_input("Logical switch: ")


# Print configuration summary
print('\n')
cprint(sw['banner'], 'yellow')
cprint('\nReview the logical switch to be created:', 'red')
print('  Name:  %s' % lswitchname)
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

    # Put the name of logical switch into a directory to render jinja2 template
    my_vars = { 'lswitchname': lswitchname }


    # Define XML Body - Global Routing > router ID
    xml_switch = createbody("templates/switch.j2", my_vars)

    # Configure Logical Switch in appropriate Transport Zone
    print('\nCreating logical switch')
    nsx.createsw(xml_switch, sw['vdnScopeId'])

    # Find dvswitch-id and VXLAN VNI
    print('\nSearching for logical switch id & Segment ID')
    swid = (nsx.findswitch(lswitchname))

    if swid[0] and swid[1]:
        cprint('\nThe Logical Switch is created as virtualwire-' + swid[0], 'green')
        cprint('Segment-ID: ' + str(swid[1]), 'green')
    else:
        cprint("\nThe switch doesn't exist", 'red')

