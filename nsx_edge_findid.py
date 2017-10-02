#! /usr/bin/env python

from nsx import NSX
import getpass
edgename =  raw_input("Edge name: ")


nsx_ip = raw_input("NSX manager IP [%s]: " % '10.33.94.154') or '10.33.94.154'
account = raw_input("Account [%s]: " % 'admin') or 'admin'
passw = getpass.getpass(prompt='Password: ', stream=None)


hgalab = NSX(nsx_ip, account, passw)


print(hgalab.findedge(edgename))

