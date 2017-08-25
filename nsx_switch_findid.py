#! /usr/bin/env python

from nsx import NSX
import getpass
from jinja2 import Template # import the class Template from module jinja2.environment


# NSX Manager credentials
lswitchname =  raw_input("Logical switch name: ")
nsx_ip = raw_input("NSX manager IP [%s]: " % '10.33.94.154') or '10.33.94.154'
account = raw_input("Account [%s]: " % 'admin') or 'admin'
passw = getpass.getpass(prompt='Password: ', stream=None)


hgalab = NSX(nsx_ip, account, passw)


# Find dvswitch-id and VXLAN VNI
print(hgalab.findswitch(lswitchname))


