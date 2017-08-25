#! /usr/bin/env python

from nsx import NSX
import getpass
from jinja2 import Template # import the class Template from module jinja2.environment


# NSX Manager credentials
edgename =  raw_input("Edge name: ")
nsx_ip = raw_input("NSX manager IP [%s]: " % '10.33.94.154') or '10.33.94.154'
account = raw_input("Account [%s]: " % 'admin') or 'admin'
passw = getpass.getpass(prompt='Password: ', stream=None)


# BGP parameters
ipAddress = raw_input("BGP neighbor: ")
localAS = raw_input("Local AS: ")
remoteAS = raw_input("Remote AS [%s]: " % '64620') or '64620'
md5 = raw_input("BGP MD5 key: ")


hgalab = NSX(nsx_ip, account, passw)


# Find edge
edgeid = hgalab.findedge(edgename)

# Get uplink IP address
if edgeid:
    routerId = hgalab.getuplinkip(edgeid)
    if not routerId:
        print("Uplink port vNIC_0 has no Ip address")
        sys.exit
else:
    print("Edge doesn't exist")
    sys.exit

print(routerId)

my_vars = { 'ipAddress': ipAddress, 'localAS': localAS, 'remoteAS': remoteAS, 'md5': md5, 'routerId': routerId }

hgalab = NSX(nsx_ip, account, passw)


# CREATE Body with Jinja2 template
with open("templates/routerid.j2") as f:
    s = f.read()

template = Template(s)

# Define XML Body - Global Routing > router ID
xml_routerID = template.render(my_vars)

# Configure Router ID
if edgeid:
    hgalab.cfgglobrouting(xml_routerID, edgeid)



# CREATE Body with Jinja2 template
with open("templates/bgp.j2") as f:
    s = f.read()

template = Template(s)


# Define XML Body
xml_BGP = template.render(my_vars)


# Configure BGP
if edgeid:
    hgalab.cfgbgp(xml_BGP, edgeid)


