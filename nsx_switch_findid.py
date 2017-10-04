#! /usr/bin/env python

"""
===================================================================================================
   Author:         Petr Nemec
   Description:    Resolves logical switch name to virtualwire-id
   Date:           2017-10-04
===================================================================================================
"""

from nsx import NSX
from nsx import credentials
from nsx import seldc
from termcolor import cprint
import sys

# Select the vSphere to be modified
inputs = 'inputs/nsx_' + seldc(sys.argv[1:]) + '.yml'

lswitchname = raw_input("Logical switch name: ")

# NSX Manager credentials
cred = credentials(inputs)
nsx = NSX(*cred)


# Find dvswitch-id and VXLAN VNI
print('\nSearching for logical switch id & Segment ID')
swid = (nsx.findswitch(lswitchname))


if swid[0] and swid[1]:
    cprint('\nThe Logical Switch exists as virtualwire-' + swid[0], 'green')
    cprint('Segment-ID: ' + str(swid[1]), 'green')
else:
    cprint("\nThe switch doesn't exist", 'red')

