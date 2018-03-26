#! /usr/bin/env python

"""
===================================================================================================
   Author:          Petr Nemec
   Description:     Edge ownership - CSV like output
                    It parses output from three REST API calls

                    List of tenant edges from vCD
                    https://{{url}}/api/query?type=edgeGateway&format=records&pageSize=200

                    List of Organizations from vCD
                    https://{{url}}/api/org

                    List of NSX edges from NSX Manager
                    https://{{url}}/api/4.0/edges/

   Date:            2018-02-19
===================================================================================================
"""

import xml.etree.ElementTree as ET

def vcd_edges_list(xmlfile):
    """
    :param:
    :return:    list of edges defined in vCD
    """
    edge_list = []
    ns = {'vcloud': 'http://www.vmware.com/vcloud/v1.5'}
    root = ET.fromstring(xmlfile)
    for resource in root.findall('.//vcloud:EdgeGatewayRecord', ns):
        # print resource.attrib['name']
        # print resource.attrib['vdc'].split('/')[-1]
        # print resource.attrib['href'].split('/')[-1]
        # print resource.attrib['advancedNetworkingEnabled']
        # print resource.attrib['gatewayStatus']
        # print resource.attrib['haStatus']
        edge_list.append(resource.attrib['name'])

    return edge_list


def vcd_edges(xmlfile):
        """
        :param:
        :return:    directory of tenenant edges created in vCD
        """
        edge_dir = {}
        ns = {'vcloud': 'http://www.vmware.com/vcloud/v1.5'}
        root = ET.fromstring(xmlfile)
        for resource in root.findall('.//vcloud:EdgeGatewayRecord', ns):
            # print resource.attrib['name']
            # print resource.attrib['vdc'].split('/')[-1]
            # print resource.attrib['href'].split('/')[-1]
            # print resource.attrib['advancedNetworkingEnabled']
            # print resource.attrib['gatewayStatus']
            # print resource.attrib['haStatus']

            tmp_edge_dir = {resource.attrib['name']: {'vdc': resource.attrib['vdc'].split('/')[-1],
                                                      'href': resource.attrib['href'].split('/')[-1],
                                                      'advancedNetworkingEnabled': resource.attrib['advancedNetworkingEnabled'],
                                                      'haStatus': resource.attrib['haStatus']
                                                      }
                            }
            edge_dir.update(tmp_edge_dir)
        return edge_dir


def vcd_orgs(xmlfile):
    """
    :param:
    :return:    directory of Organizations in vCD
    """
    organizations = {}
    ns = {'vcloud': 'http://www.vmware.com/vcloud/v1.5'}
    root = ET.fromstring(xmlfile)
    for resource in root.findall('.//vcloud:Org', ns):
        # print(resource.attrib['name'])
        # print(resource.attrib['href'].split('/')[-1])
        organizations.update({resource.attrib['href'].split('/')[-1]: resource.attrib['name']})

    return organizations


def nsx_edges(xmlfile):
    """
    :param:
    :return:    directory of nsx edges
    """
    nsx_edges = {}
    root = ET.fromstring(xmlfile)
    for resource in root.findall('.//edgeSummary'):
        # print(resource.find('.//objectId')).text
        # print(resource.find('.//name')).text
        # print(resource.find('.//tenantId')).text
        # print(resource.find('.//appliancesSummary/vmVersion')).text
        tmp_nsx_edges = {resource.find('.//objectId').text: {'name': resource.find('.//name').text,
                                                             'tenantId': resource.find('.//tenantId').text,
                                                             'vmVersion': resource.find('.//appliancesSummary/vmVersion').text,
                                                             }
                         }
        nsx_edges.update(tmp_nsx_edges)
    return nsx_edges


def edge_in_vcd(edgename, vcd_edge_dir):
    """
    :param:
    :return:    Name of the tenent edge if exists in vCD otherwise it returns False
    """
    if str(edges_nsx[edge]['name']).startswith('vse-'):
        updated_name = edgename.split('vse-')[1]
        updated_name = updated_name.split(' (')[0]
        if updated_name in vcd_edge_dir:
            return updated_name
        else:
            updated_name = False
            return updated_name


# Load all data
# Load VCD edges
with open('vcd_edges.txt', 'r') as f:
    vcd_edges_xml = f.read()

# Load NSX edges
with open('nsx_edges.txt', 'r') as f:
    nsx_edges_xml = f.read()

# Load Organizations
with open('vcd_orgs.txt', 'r') as f:
    vcd_orgs_xml = f.read()

# Create a directory of organizations
organizations = vcd_orgs(vcd_orgs_xml)

# Create a directory of NSX edges
edges_nsx = nsx_edges(nsx_edges_xml)

# Identify the Organization the edge belongs to and update the directory
for edge in edges_nsx:
    # print(edges_nsx[edge]['name'])
    # Search for an organization the edge belongs to. The tenantId equals to Org's href
    if edges_nsx[edge]['tenantId'] in organizations:
        edges_nsx[edge]['org'] = organizations[edges_nsx[edge]['tenantId']]
    else:
        # If tenant id default
        edges_nsx[edge]['org'] = "N/A - Provider Edge"


# Create a directory of Tenant edges (created in vCD)
edges_vcd = vcd_edges(vcd_edges_xml)

# print(edges_vcd)

# Test if an edge exists in vCD
print('Edge-id,Name,Provider/Tenant,Version,Organization,AdvancedGW,haStatus')
for edge in edges_nsx:
    # print edges_nsx[edge]['name']
    # Test if the nsx edge exists in vCD
    isinvcd = edge_in_vcd(edges_nsx[edge]['name'], edges_vcd)
    if isinvcd:
        # print details of a tenant edge
        print (edge + ',' + edges_nsx[edge]['name'] + ',' + 'Tenant Edge' + ','
               + edges_nsx[edge]['vmVersion'] + ',' + edges_nsx[edge]['org'] + ','
               + edges_vcd[isinvcd]['advancedNetworkingEnabled'] + ','
               + edges_vcd[isinvcd]['haStatus'])
    else:
        # print details of a provider edge
        print (edge + ',' + edges_nsx[edge]['name'] + ',' + 'Not found in vCD' + ','
               + edges_nsx[edge]['vmVersion'] + ',' + edges_nsx[edge]['org']
               + ',,')

# Print all tenant edges
print('\n')
print('Tenant Edge Name,AdvancedGW,haStatus')
for te_edge in edges_vcd:
    print(te_edge + ',' + edges_vcd[te_edge]['advancedNetworkingEnabled'] + ',' + edges_vcd[te_edge]['haStatus'])

