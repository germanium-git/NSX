#! /usr/bin/env python

"""
===================================================================================================
   Author:          Petr Nemec
   Description:     Searching for inconsistent names in NSX & vCD - CSV like output
                    It parses output from three REST API calls

                    List of logical switches
                    https://{{url}}/api/2.0/vdn/virtualwires?pagesize=200&startindex=0

                    List of all org Networks (Power CLI) - Get-OrgNetwork
                    Use orgnw.ps1 or orgnw_v2.ps1 to get orgnwreport.csv

   Date:            2018-03-26
===================================================================================================
"""

import xml.etree.ElementTree as ET

import csv

def nsx_lswitches(xmlfile):
    """
    :param:
    :return:    nsx edges and tenant
    """
    nsx_lswitches = {}
    root = ET.fromstring(xmlfile)
    for resource in root.findall('.//virtualWire'):
        # print(resource.find('.//objectId')).text
        # print(resource.find('.//name')).text
        # print(resource.find('.//tenantId')).text
        # print(resource.find('.//vdnId')).text
        # print(resource.find('.//vdnScopeId')).text
        tmp_nsx_lswitches = {resource.find('.//objectId').text: {'name': resource.find('.//name').text,
                                                                 'tenantId': resource.find('.//tenantId').text,
                                                                 'vdnId': resource.find('.//vdnId').text,
                                                                 'vdnScopeId': resource.find('.//vdnScopeId').text,
                                                                 }
                             }
        nsx_lswitches.update(tmp_nsx_lswitches)
    return nsx_lswitches

# Load all data

# Load NSX logical switches
with open('nsx_lswitches_swe.txt', 'r') as f:
    nsx_lswitches_xml = f.read()

# Load vCD OrgVdcNetworks
with open('orgnwreport.csv', 'r') as infile:
    reader = csv.reader(infile)
    vdc_orgnetworks = {rows[0]: rows[1] for rows in reader}

# Define vimserver IDs to identify vCenter Servers where Org networks are created
vimserver = {'aaaaaaaa-xxxx-xxxx-xxxx-xxxxxxxxxxxx': 'ABC',
             'rrrrrrrr-xxxx-xxxx-xxxx-xxxxxxxxxxxx': 'RST',
             'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx': 'XYZ'
             }

# print vdc_orgnetworks

vdc_orgnw_updated = {}
for orgnw in vdc_orgnetworks:
    # print orgnw
    vcenter = vimserver[vdc_orgnetworks[orgnw].split(' on ')[1].split(':')[1][:-1]]
    providerinfo = vdc_orgnetworks[orgnw].split(' on ')[0].split(':')[1]
    vdc_orgnw_updated.update({(providerinfo, vcenter): orgnw})

#print(vdc_orgnw_updated)
# Print VDC Org Networks
print('\nList of Org VDC Networks')
print('Country,virtualwire or dvportgroup,name')
for orgnw in vdc_orgnw_updated:
    print(orgnw[1] + ',' + orgnw[0] + ',' + vdc_orgnw_updated[orgnw])


print('\nList of logical switches from vCenter')
print('virtulawire,SID,name,TZ)')
lswitches = nsx_lswitches(nsx_lswitches_xml)
for lsw in lswitches:
    # print(edges_nsx[edge]['name'])
    print (lsw + ',' + lswitches[lsw]['vdnId'] + ',' + lswitches[lsw]['name'] + ',' + lswitches[lsw]['vdnScopeId'])
